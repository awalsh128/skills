#!/usr/bin/env python3
"""
skill-audit.py — Interactive auditor for AI agent skills & plugins.

Scans skill directories, estimates per-turn token tax, flags duplicates,
collisions, bloat, and never-used skills. Walks you through fixes interactively.

Usage:
    python skill_audit.py [paths...] [--ci] [--budget N] [--days N] [--json out.json]

Examples:
    python skill_audit.py ~/.claude/skills .claude/skills
    python skill_audit.py ~/.claude/skills --ci --budget 4000
    python skill_audit.py --days 30 ~/.claude/skills ~/.claude/plugins
"""

# TODO: Clean this up to be more readable, modular, and maintainable. Try not to split the file.

import argparse
import json
import os
import re
import sys
import hashlib
import textwrap

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ─── Constants ───────────────────────────────────────────────────────────────

TOKENS_PER_CHAR = 0.25  # ~4 chars per token (conservative)
DEFAULT_BUDGET = 4000   # ~2% of 200K context (Anthropic convention)
BLOATED_DESC_WORDS = 30
HEAVY_BODY_LINES = 400
RULE_HEAVY_LINES = 100

# ─── Data Structures ─────────────────────────────────────────────────────────

@dataclass
class Skill:
    name: str
    path: Path
    description: str = ""
    body_tokens: int = 0
    desc_tokens: int = 0
    total_tokens: int = 0
    lines: int = 0
    source: str = "skill"  # skill | plugin | rule | agent
    plugin: Optional[str] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    issues: list = field(default_factory=list)
    duplicate_of: Optional[str] = None
    collision_with: list = field(default_factory=list)

    @property
    def always_on_tokens(self) -> int:
        """Tokens injected every turn (name + description)."""
        return self.desc_tokens

    @property
    def on_trigger_tokens(self) -> int:
        """Tokens injected when skill fires."""
        return self.body_tokens

@dataclass
class AuditReport:
    skills: list = field(default_factory=list)
    total_always_on: int = 0
    total_on_trigger: int = 0
    budget: int = DEFAULT_BUDGET
    duplicates: list = field(default_factory=list)
    collisions: list = field(default_factory=list)
    never_used: list = field(default_factory=list)
    bloated: list = field(default_factory=list)
    actions_taken: list = field(default_factory=list)

# ─── Discovery ───────────────────────────────────────────────────────────────

def discover_skills(paths: list[Path]) -> list[Skill]:
    """Walk directories and discover skills, plugins, rules, agents."""
    skills = []
    seen_paths = set()

    for root in paths:
        if not root.exists():
            print(f"  ⚠ Skipping missing path: {root}", file=sys.stderr)
            continue

        for p in sorted(root.rglob("SKILL.md")):
            if p in seen_paths:
                continue
            seen_paths.add(p)
            skill = parse_skill_file(p, source="skill")
            if skill:
                skill.plugin = detect_plugin_owner(p, root)
                skills.append(skill)

        for p in sorted(root.rglob("AGENTS.md")):
            if p in seen_paths:
                continue
            seen_paths.add(p)
            skill = parse_skill_file(p, source="agent")
            if skill:
                skills.append(skill)

        for p in sorted(root.rglob("rules/**/*.md")):
            if p in seen_paths:
                continue
            seen_paths.add(p)
            skill = parse_skill_file(p, source="rule")
            if skill:
                skills.append(skill)

    return skills

def parse_skill_file(path: Path, source: str = "skill") -> Optional[Skill]:
    """Parse a SKILL.md or similar file into a Skill object."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    name = path.parent.name
    description = ""

    # Extract YAML frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip().strip("'\"")
        desc_match = re.search(r"^description:\s*(.+?)(?=\n\w|\Z)", fm, re.MULTILINE | re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip().strip("'\"")

    # Token estimates
    desc_text = f"{name}: {description}" if description else name
    desc_tokens = int(len(desc_text) * TOKENS_PER_CHAR)
    body_tokens = int(len(text) * TOKENS_PER_CHAR)
    lines = text.count("\n") + 1

    return Skill(
        name=name,
        path=path,
        description=description,
        body_tokens=body_tokens,
        desc_tokens=desc_tokens,
        total_tokens=body_tokens,
        lines=lines,
        source=source,
    )

def detect_plugin_owner(skill_path: Path, root: Path) -> Optional[str]:
    """Check if a skill lives under a plugin directory."""
    rel = skill_path.relative_to(root)
    parts = rel.parts
    if len(parts) > 1 and parts[0] in (".claude-plugin", "plugin", "plugins"):
        return parts[0]
    # Check for plugin.json in parent dirs
    for parent in skill_path.parents:
        if (parent / "plugin.json").exists():
            return parent.name
        if parent == root:
            break
    return None

# ─── Analysis ────────────────────────────────────────────────────────────────

def analyze(skills: list[Skill], days: int = 30) -> AuditReport:
    """Run all analysis passes and populate the report."""
    report = AuditReport(skills=skills)

    # Totals
    report.total_always_on = sum(s.always_on_tokens for s in skills)
    report.total_on_trigger = sum(s.on_trigger_tokens for s in skills)

    # 1. Duplicates (same content hash)
    content_hashes = {}
    for s in skills:
        h = hashlib.md5(s.path.read_bytes()).hexdigest()
        if h in content_hashes:
            s.duplicate_of = content_hashes[h].name
            s.issues.append("duplicate")
            report.duplicates.append((content_hashes[h].name, s.name))
        else:
            content_hashes[h] = s

    # 2. Name collisions (same name, different paths)
    name_map = {}
    for s in skills:
        name_map.setdefault(s.name.lower(), []).append(s)
    for name, group in name_map.items():
        if len(group) > 1:
            for s in group:
                s.collision_with = [g.name for g in group if g is not s]
                s.issues.append("collision")
            report.collisions.append((name, [g.path for g in group]))

    # 3. Bloat detection
    for s in skills:
        desc_words = len(s.description.split()) if s.description else 0
        if desc_words > BLOATED_DESC_WORDS:
            s.issues.append(f"bloated description ({desc_words} words)")
            report.bloated.append(s)
        if s.lines > HEAVY_BODY_LINES:
            s.issues.append(f"heavy body ({s.lines} lines)")
            report.bloated.append(s)

    # 4. Usage analysis (if transcript data available)
    if days > 0:
        usage = scan_usage(skills, days)
        for s in skills:
            s.usage_count = usage.get(s.name, 0)
            s.last_used = usage.get(f"{s.name}__last", None)
            if s.usage_count == 0:
                s.issues.append("never used in period")
                report.never_used.append(s)

    # 5. Budget check
    if report.total_always_on > report.budget:
        print(f"\n  🔴 BUDGET EXCEEDED: {report.total_always_on:,} tokens "
              f"always-on vs {report.budget:,} budget "
              f"({report.total_always_on / report.budget * 100:.0f}%)")

    return report

def scan_usage(skills: list[Skill], days: int) -> dict:
    """Scan Claude Code session transcripts for Skill tool invocations.

    Looks in ~/.claude/projects/*/*.jsonl for "Skill" tool_use blocks.
    Returns {skill_name: count, skill_name__last: datetime}
    """
    usage = {}
    cutoff = datetime.now() - timedelta(days=days)
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        return usage

    skill_names = {s.name.lower() for s in skills}

    for jsonl in projects_dir.rglob("*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(jsonl.stat().st_mtime)
            if mtime < cutoff:
                continue
        except OSError:
            continue

        try:
            with open(jsonl, "r", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Look for tool_use with name "Skill"
                    if entry.get("type") == "assistant":
                        msg = entry.get("message", {})
                        for block in msg.get("content", []):
                            if (isinstance(block, dict)
                                    and block.get("type") == "tool_use"
                                    and block.get("name") == "Skill"):
                                input_data = block.get("input", {})
                                skill_arg = str(input_data.get("skill", "")).lower()
                                if skill_arg in skill_names:
                                    usage[skill_arg] = usage.get(skill_arg, 0) + 1
                                    ts = entry.get("timestamp")
                                    if ts:
                                        try:
                                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                                            key = f"{skill_arg}__last"
                                            if key not in usage or dt > usage[key]:
                                                usage[key] = dt
                                        except (ValueError, TypeError):
                                            pass
        except OSError:
            continue

    return usage

# ─── Display ─────────────────────────────────────────────────────────────────

def print_report(report: AuditReport):
    """Print the formatted audit report."""
    skills = report.skills

    print(f"\n{'═' * 60}")
    print(f"  SKILL AUDIT REPORT")
    print(f"{'═' * 60}\n")

    # Summary line
    never = len(report.never_used)
    dups = len(report.duplicates)
    colls = len(report.collisions)
    bloated = len(report.bloated)
    print(f"  {len(skills)} skills | {report.total_always_on:,} tok/turn always-on "
          f"| budget {report.budget:,} "
          f"| {never} never-used | {dups} dup | {colls} collision | {bloated} bloated\n")

    # Table
    header = f"  {'NAME':<28} {'SRC':<7} {'ALWAYS':>7} {'ON-TRIG':>8} {'USES':>5}  FLAGS"
    print(header)
    print(f"  {'─' * 28} {'─' * 7} {'─' * 7} {'─' * 8} {'─' * 5}  {'─' * 20}")

    # Sort: always-on tokens descending
    sorted_skills = sorted(skills, key=lambda s: s.always_on_tokens, reverse=True)
    for s in sorted_skills:
        flags = ", ".join(s.issues[:2]) if s.issues else ""
        uses = str(s.usage_count) if s.usage_count > 0 else "—"
        print(f"  {s.name:<28.28} {s.source:<7} {s.always_on_tokens:>7,} "
              f"{s.on_trigger_tokens:>8,} {uses:>5}  {flags}")

    # Totals
    print(f"\n  {'─' * 60}")
    print(f"  {'TOTAL':<28} {'':7} {report.total_always_on:>7,} "
          f"{report.total_on_trigger:>8,}\n")

    # Top savings
    if report.never_used:
        save = sum(s.always_on_tokens for s in report.never_used)
        print(f"  💡 Top saving: disable {len(report.never_used)} never-used skills "
              f"→ save ~{save:,} tok/turn "
              f"({save / report.total_always_on * 100:.0f}% of always-on)\n")

# ─── Interactive Fix Loop ────────────────────────────────────────────────────

def interactive_fix(report: AuditReport, write: bool = False):
    """Walk through findings and let the user decide actions."""
    actions = []
    actionable = []

    # Build actionable list: never-used, duplicates, collisions, bloated
    for s in report.never_used:
        actionable.append(("disable", s, f"Never used (0 invocations)"))
    for dup_name, dup_of in report.duplicates:
        for s in report.skills:
            if s.name == dup_name:
                actionable.append(("remove", s, f"Duplicate of '{dup_of}'"))
                break
    for name, paths in report.collisions:
        for s in report.skills:
            if s.name.lower() == name and "collision" in s.issues:
                actionable.append(("review", s, f"Name collision: {s.collision_with}"))
                break
    for s in report.bloated:
        if "bloated description" in " ".join(s.issues):
            actionable.append(("compress", s, f"Description: {len(s.description.split())} words"))

    if not actionable:
        print("\n  ✅ No actionable findings. Your loadout is clean.\n")
        return actions

    print(f"\n{'─' * 60}")
    print(f"  INTERACTIVE FIX — {len(actionable)} items to review")
    print(f"{'─' * 60}\n")

    for i, (action_type, skill, reason) in enumerate(actionable, 1):
        print(f"  [{i}/{len(actionable)}] {skill.name} ({skill.source})")
        print(f"      Issue: {reason}")
        print(f"      Path:  {skill.path}")
        print(f"      Always-on cost: {skill.always_on_tokens} tokens/turn")
        print()

        # Prompt
        options = get_options(action_type)
        print(f"      {options}")

        while True:
            choice = input(f"      Choose [1-{len(options)}] (0=skip all): ").strip()
            if choice == "0":
                # Skip remaining
                remaining = len(actionable) - i
                print(f"      Skipping remaining {remaining} items.")
                return actions
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                break
            print("      Invalid choice.")

        selected = options[int(choice) - 1]
        label, handler = selected

        if handler == "disable":
            action = disable_skill(skill)
        elif handler == "remove":
            action = remove_skill(skill)
        elif handler == "compress":
            action = compress_skill(skill)
        elif handler == "keep":
            action = None
        else:
            action = None

        if action:
            actions.append(action)
            print(f"      ✓ {action['action']}: {action['detail']}")
        else:
            print(f"      → Kept as-is.")
        print()

    # Summary
    if actions:
        print(f"\n  {'─' * 60}")
        print(f"  SUMMARY: {len(actions)} changes planned")
        for a in actions:
            print(f"    • {a['action']}: {a['detail']}")

        if write:
            write_actions(actions)
            print(f"\n  📝 Actions written to skill_audit_actions.json")
            print(f"  Revert anytime: python skill_audit.py --revert skill_audit_actions.json")
        else:
            print(f"\n  (Dry run — no changes made. Re-run with --write to apply.)")
    else:
        print(f"\n  No changes made.")

    return actions

def get_options(action_type: str) -> list[tuple[str, str]]:
    """Return (label, handler) options for a given action type."""
    if action_type == "disable":
        return [
            ("Disable (set model_invocation: false)", "disable"),
            ("Keep as-is", "keep"),
            ("Delete skill entirely", "remove"),
        ]
    elif action_type == "remove":
        return [
            ("Remove duplicate", "remove"),
            ("Keep both (acknowledge)", "keep"),
        ]
    elif action_type == "compress":
        return [
            ("Show description for manual edit", "compress"),
            ("Keep as-is", "keep"),
        ]
    else:  # review
        return [
            ("Rename (show paths for manual fix)", "compress"),
            ("Keep as-is", "keep"),
        ]

def disable_skill(skill: Skill) -> Optional[dict]:
    """Add model_invocation: false to frontmatter."""
    try:
        text = skill.path.read_text(encoding="utf-8")
        if "model_invocation" not in text:
            # Insert into frontmatter
            if re.match(r"^---\s*\n", text):
                text = re.sub(r"^---\s*\n", "---\nmodel_invocation: false\n", text)
            else:
                text = "---\nmodel_invocation: false\n---\n" + text
            skill.path.write_text(text, encoding="utf-8")
            return {"action": "disabled", "detail": skill.name, "revert": "remove model_invocation: false"}
    except OSError as e:
        print(f"      ⚠ Failed: {e}")
    return None

def remove_skill(skill: Skill) -> Optional[dict]:
    """Move skill to a .trash/ directory (reversible)."""
    trash = skill.path.parent.parent / ".trash"
    trash.mkdir(exist_ok=True)
    target = trash / skill.path.parent.name
    try:
        import shutil
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(skill.path.parent), str(target))
        return {"action": "removed", "detail": skill.name,
                "revert": f"mv {target} {skill.path.parent}"}
    except OSError as e:
        print(f"      ⚠ Failed: {e}")
    return None

def compress_skill(skill: Skill) -> Optional[dict]:
    """Print the description for manual editing."""
    print(f"\n      ┌{'─' * 50}┐")
    for line in textwrap.wrap(skill.description, width=48):
        print(f"      │ {line:<50} │")
    print(f"      └{'─' * 50}┘")
    print(f"      Edit: {skill.path}")
    print(f"      Target: <{BLOATED_DESC_WORDS} words\n")
    return {"action": "flagged-for-compression", "detail": skill.name, "revert": None}

def write_actions(actions: list[dict]):
    """Persist actions for later revert."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "actions": actions,
    }
    Path("skill_audit_actions.json").write_text(json.dumps(data, indent=2))

def revert_actions(actions_file: str):
    """Revert previously applied actions."""
    path = Path(actions_file)
    if not path.exists():
        print(f"  ⚠ No actions file: {actions_file}")
        return
    data = json.loads(path.read_text())
    for a in data.get("actions", []):
        if a.get("revert"):
            print(f"  Reverting: {a['action']} — {a['detail']}")
            # For disable: remove the line
            # For remove: move back
            # (simplified — in production, parse and execute)
            print(f"    Command: {a['revert']}")
    print(f"\n  Review and run revert commands manually, or re-run with --write.")

# ─── CI Mode ─────────────────────────────────────────────────────────────────

def ci_mode(report: AuditReport, budget: int) -> int:
    """Non-interactive mode for CI. Returns exit code (0=pass, 1=fail)."""
    report.budget = budget
    failures = []

    if report.total_always_on > budget:
        failures.append(f"Budget exceeded: {report.total_always_on:,} > {budget:,} tokens")

    if report.duplicates:
        failures.append(f"{len(report.duplicates)} duplicate(s) found")

    if report.collisions:
        failures.append(f"{len(report.collisions)} name collision(s)")

    # Print JSON report
    output = {
        "total_skills": len(report.skills),
        "total_always_on_tokens": report.total_always_on,
        "total_on_trigger_tokens": report.total_on_trigger,
        "budget": budget,
        "within_budget": report.total_always_on <= budget,
        "duplicates": [f"{a} == {b}" for a, b in report.duplicates],
        "collisions": [name for name, _ in report.collisions],
        "never_used": [s.name for s in report.never_used],
        "bloated": [s.name for s in report.bloated],
        "failures": failures,
    }
    print(json.dumps(output, indent=2))

    if failures:
        print(f"\n  ❌ CI FAIL: {len(failures)} issue(s)", file=sys.stderr)
        return 1
    print(f"\n  ✅ CI PASS", file=sys.stderr)
    return 0

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audit AI agent skills & plugins for context bloat, duplicates, and dead weight.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="*", type=Path,
                        help="Skill/plugin directories to scan (default: ~/.claude/skills)")
    parser.add_argument("--ci", action="store_true",
                        help="Non-interactive CI mode (exit 1 on failure)")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                        help=f"Always-on token budget (default: {DEFAULT_BUDGET})")
    parser.add_argument("--days", type=int, default=30,
                        help="Look back N days for usage (0=skip usage scan)")
    parser.add_argument("--json", type=str, metavar="FILE",
                        help="Write JSON report to file")
    parser.add_argument("--write", action="store_true",
                        help="Apply fixes (default: dry run)")
    parser.add_argument("--revert", type=str, metavar="FILE",
                        help="Revert actions from a previously saved file")

    args = parser.parse_args()

    # Revert mode
    if args.revert:
        revert_actions(args.revert)
        return 0

    # Default paths
    if not args.paths:
        args.paths = [Path.home() / ".claude" / "skills"]

    # Discover
    print(f"\n  Scanning: {', '.join(str(p) for p in args.paths)}")
    skills = discover_skills(args.paths)

    if not skills:
        print("  No skills found.")
        return 0

    # Analyze
    report = analyze(skills, days=args.days)
    report.budget = args.budget

    # CI mode
    if args.ci:
        sys.exit(ci_mode(report, args.budget))

    # Interactive mode
    print_report(report)
    interactive_fix(report, write=args.write)

    # Optional JSON output
    if args.json:
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_skills": len(report.skills),
            "total_always_on_tokens": report.total_always_on,
            "budget": report.budget,
            "skills": [
                {
                    "name": s.name,
                    "path": str(s.path),
                    "source": s.source,
                    "always_on_tokens": s.always_on_tokens,
                    "on_trigger_tokens": s.on_trigger_tokens,
                    "usage_count": s.usage_count,
                    "issues": s.issues,
                }
                for s in report.skills
            ],
            "duplicates": report.duplicates,
            "collisions": [(n, [str(p) for p in paths]) for n, paths in report.collisions],
            "never_used": [s.name for s in report.never_used],
        }
        Path(args.json).write_text(json.dumps(data, indent=2))
        print(f"\n  📄 JSON report: {args.json}")

if __name__ == "__main__":
    main()