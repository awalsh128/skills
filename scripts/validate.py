#!/usr/bin/env python3
"""Deterministic repo checks. Pure standard library: no network, no model calls."""
import json, re, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
errors = []

def err(msg):
    errors.append(msg)

def load(path):
    try:
        return json.loads((root / path).read_text())
    except Exception as e:  # missing file or bad JSON
        err(f"{path}: {e}")
        return {}

plugin = load(".claude-plugin/plugin.json")
market = load(".claude-plugin/marketplace.json")

if plugin.get("name") is None:
    err("plugin.json: missing name")
for entry in market.get("plugins", []):
    if entry.get("name") != plugin.get("name"):
        err(f"marketplace.json: entry name {entry.get('name')!r} != plugin.json name {plugin.get('name')!r}")
    if entry.get("name") == plugin.get("name"):
        # plugin.json wins at install time, so a stale entry is silently ignored (AGENTS.md).
        for key in ("version", "description"):
            if entry.get(key) != plugin.get(key):
                err(f"marketplace.json: entry {key} {entry.get(key)!r} != plugin.json {key} {plugin.get(key)!r}")
    src = entry.get("source")
    if isinstance(src, str) and not (root / src).is_dir():
        err(f"marketplace.json: source {src!r} does not exist")
if market.get("description") != plugin.get("description"):
    err(f"marketplace.json: description {market.get('description')!r} != plugin.json description")
for key in ("name", "owner", "plugins"):
    if key not in market:
        err(f"marketplace.json: missing {key}")

skill_dirs = []
for p in plugin.get("skills", []):
    d = root / p
    if not d.is_dir():
        err(f"plugin.json: skills path {p!r} does not exist")
    else:
        skill_dirs += [s.parent for s in d.glob("*/SKILL.md")]

if not skill_dirs:
    err("no SKILL.md found under plugin.json skills paths")

for d in skill_dirs:
    rel = d.relative_to(root)
    text = (d / "SKILL.md").read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{rel}/SKILL.md: missing frontmatter")
        continue
    fm = dict(re.findall(r"^(name|description):\s*(.+)$", m.group(1), re.M))
    if fm.get("name") != d.name:
        err(f"{rel}/SKILL.md: name {fm.get('name')!r} != folder {d.name!r}")
    if not fm.get("description"):
        err(f"{rel}/SKILL.md: missing description")
    for ref in re.findall(r"`(references/[\w./-]+\.md)`", text):
        if not (d / ref).is_file():
            err(f"{rel}/SKILL.md: referenced {ref} does not exist")
    # Scripts and templates a skill tells the agent to run or copy, bare or as `<skill dir>/scripts/x`.
    for script in set(re.findall(r"`((?:scripts|templates)/[\w./-]+)`", text)) | set(
        re.findall(r"<skill dir>/((?:scripts|templates)/[\w./-]+)", text)
    ):
        if not (d / script).exists():
            err(f"{rel}/SKILL.md: referenced {script} does not exist")

# Skills stay disjoint from gh-dev-powerpack (AGENTS.md): only the dev-powerpack-exemplars skill reads it, so
# no skill names its repo or paths. Eval inputs and workspace output are skipped.
for d in skill_dirs:
    for md in d.rglob("*.md"):
        rel_md = md.relative_to(root)
        if any(part == "evals" or part.endswith("-workspace") for part in rel_md.parts):
            continue
        for line_no, line in enumerate(md.read_text().splitlines(), 1):
            if "gh-dev-powerpack" in line:
                err(f"{rel_md}:{line_no}: names gh-dev-powerpack; refer to the dev-powerpack-exemplars skill instead")

# README skills table must link every skill, and only skills that exist.
readme = (root / "README.md").read_text()
listed = set(re.findall(r"\]\((skills/[\w./-]+?)/SKILL\.md\)", readme))
actual = {str(d.relative_to(root)) for d in skill_dirs}
for missing in sorted(actual - listed):
    err(f"README.md: skills table is missing {missing}")
for stale in sorted(listed - actual):
    err(f"README.md: skills table lists {stale}, which is not a skill")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok: {len(skill_dirs)} skill(s) checked")
