#!/usr/bin/env python3
"""Deterministic repo checks: no network, no model calls. Needs the packages in requirements.txt."""

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = ".claude-plugin/plugin.json"
MARKETPLACE_JSON = ".claude-plugin/marketplace.json"

FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.S)
REFERENCE_PATH = re.compile(r"`(references/[\w./-]+\.md)`")
# Scripts and templates a skill tells the agent to run or copy, bare or as `<skill dir>/scripts/x`.
BARE_SCRIPT_PATH = re.compile(r"`((?:scripts|templates)/[\w./-]+)`")
SKILL_DIR_SCRIPT_PATH = re.compile(r"<skill dir>/((?:scripts|templates)/[\w./-]+)")
README_SKILL_LINK = re.compile(r"\]\((skills/[\w./-]+?)/SKILL\.md\)")


def read_text(root: Path, path: Path | str) -> tuple[str | None, list[str]]:
    try:
        return (root / path).read_text(encoding="utf-8"), []
    except (OSError, UnicodeDecodeError) as error:
        return None, [f"{path}: {error}"]


def load_json_object(root: Path, path: str) -> tuple[dict, list[str]]:
    text, errors = read_text(root, path)
    if text is None:
        return {}, errors
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return {}, [f"{path}: {error}"]
    if not isinstance(data, dict):
        return {}, [f"{path}: must be a JSON object"]
    return data, []


def check_manifest_shapes(plugin: dict, marketplace: dict) -> list[str]:
    """Check the types the other checks rely on. A missing key is left for them to report."""
    errors = []
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        errors.append("marketplace.json: plugins must be a list of objects")
    skills_paths = plugin.get("skills", [])
    if not isinstance(skills_paths, list) or not all(
        isinstance(path, str) and not Path(path).is_absolute() for path in skills_paths
    ):
        errors.append("plugin.json: skills must be a list of relative paths")
    return errors


def load_manifests(root: Path) -> tuple[dict, dict, list[str]]:
    plugin, plugin_errors = load_json_object(root, PLUGIN_JSON)
    marketplace, marketplace_errors = load_json_object(root, MARKETPLACE_JSON)
    errors = plugin_errors + marketplace_errors
    if not errors:
        errors = check_manifest_shapes(plugin, marketplace)
    return plugin, marketplace, errors


def check_manifests(root: Path, plugin: dict, marketplace: dict) -> list[str]:
    # A key absent from both manifests would otherwise count as consistent.
    errors = [
        f"plugin.json: missing {key}" for key in ("name", "version", "description") if not plugin.get(key)
    ]
    if marketplace.get("plugins") == []:
        errors.append("marketplace.json: plugins has no entry for the plugin")
    for entry in marketplace.get("plugins", []):
        if entry.get("name") != plugin.get("name"):
            errors.append(
                f"marketplace.json: entry name {entry.get('name')!r} "
                f"!= plugin.json name {plugin.get('name')!r}"
            )
        else:
            # plugin.json wins at install time, so a stale entry is silently ignored (AGENTS.md).
            for key in ("version", "description"):
                if entry.get(key) != plugin.get(key):
                    errors.append(
                        f"marketplace.json: entry {key} {entry.get(key)!r} "
                        f"!= plugin.json {key} {plugin.get(key)!r}"
                    )
        source = entry.get("source")
        if isinstance(source, str) and not (root / source).is_dir():
            errors.append(f"marketplace.json: source {source!r} does not exist")
    if marketplace.get("description") != plugin.get("description"):
        errors.append(
            f"marketplace.json: description {marketplace.get('description')!r} != plugin.json description"
        )
    for key in ("name", "owner", "plugins"):
        if key not in marketplace:
            errors.append(f"marketplace.json: missing {key}")
    return errors


def find_skill_dirs(root: Path, skills_paths: list[str]) -> tuple[list[Path], list[str]]:
    skill_dirs = []
    errors = []
    for skills_path in skills_paths:
        group_dir = root / skills_path
        if not group_dir.is_dir():
            errors.append(f"plugin.json: skills path {skills_path!r} does not exist")
            continue
        skill_dirs += [skill_md.parent for skill_md in group_dir.glob("*/SKILL.md")]
    if not skill_dirs:
        errors.append("no SKILL.md found under plugin.json skills paths")
    return skill_dirs, errors


def is_eval_or_generated(path: Path) -> bool:
    """Whether a repo-relative path is eval input, run output or a cache rather than part of a skill."""
    skipped_names = {"evals", "__pycache__", "node_modules"}
    return any(part in skipped_names or part.endswith("-workspace") for part in path.parts)


def check_unlisted_skills(root: Path, skill_dirs: list[Path]) -> list[str]:
    """A skill in a group plugin.json does not list is never installed."""
    errors = []
    for skill_md in sorted(root.glob("skills/*/*/SKILL.md")):
        label = skill_md.relative_to(root)
        if skill_md.parent not in skill_dirs and not is_eval_or_generated(label):
            errors.append(f"{label}: its group is not listed under skills in plugin.json")
    return errors


def check_frontmatter(label: Path, text: str, folder_name: str) -> list[str]:
    match = FRONTMATTER.match(text)
    if not match:
        return [f"{label}: missing frontmatter"]
    try:
        # The blank line stands in for the opening ---, so YAML error line numbers match the file's.
        frontmatter = yaml.safe_load("\n" + match.group(1))
    # ValueError: a value shaped like a date but out of range.
    except (yaml.YAMLError, ValueError) as error:
        one_line_error = " ".join(str(error).split())
        return [f"{label}: invalid YAML frontmatter: {one_line_error}"]
    if not isinstance(frontmatter, dict):
        return [f"{label}: frontmatter is not a mapping"]

    errors = []
    name = frontmatter.get("name")
    if name != folder_name:
        errors.append(f"{label}: name {name!r} != folder {folder_name!r}")
    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{label}: description must be a non-empty string")
    return errors


def check_referenced_files(label: Path, text: str, skill_dir: Path) -> list[str]:
    errors = []
    for reference in REFERENCE_PATH.findall(text):
        if not (skill_dir / reference).is_file():
            errors.append(f"{label}: referenced {reference} does not exist")
    bare_scripts = set(BARE_SCRIPT_PATH.findall(text))
    skill_dir_scripts = set(SKILL_DIR_SCRIPT_PATH.findall(text))
    for script in sorted(bare_scripts | skill_dir_scripts):
        if not (skill_dir / script).exists():
            errors.append(f"{label}: referenced {script} does not exist")
    return errors


def check_skill(root: Path, skill_dir: Path) -> list[str]:
    label = skill_dir.relative_to(root) / "SKILL.md"
    text, errors = read_text(root, label)
    if text is None:
        return errors
    return check_frontmatter(label, text, skill_dir.name) + check_referenced_files(label, text, skill_dir)


def check_powerpack_names(root: Path, skill_dirs: list[Path]) -> list[str]:
    """Skills stay disjoint from gh-dev-powerpack (AGENTS.md), so none names its repo or paths.

    Only the dev-powerpack-exemplars skill reads it. Every file is scanned, whatever its type.
    """
    errors = []
    for skill_dir in skill_dirs:
        for path in sorted(skill_dir.rglob("*")):
            label = path.relative_to(root)
            if not path.is_file() or is_eval_or_generated(label):
                continue
            try:
                content = path.read_bytes()
            except OSError as error:
                errors.append(f"{label}: {error}")
                continue
            for line_number, line in enumerate(content.splitlines(), 1):
                if b"gh-dev-powerpack" in line:
                    errors.append(
                        f"{label}:{line_number}: names gh-dev-powerpack; "
                        "refer to the dev-powerpack-exemplars skill instead"
                    )
    return errors


def check_readme_table(root: Path, skill_dirs: list[Path]) -> list[str]:
    """The README skills table must link every skill, and only skills that exist."""
    readme, errors = read_text(root, "README.md")
    if readme is None:
        return errors
    listed = set(README_SKILL_LINK.findall(readme))
    actual = {str(skill_dir.relative_to(root)) for skill_dir in skill_dirs}
    for missing in sorted(actual - listed):
        errors.append(f"README.md: skills table is missing {missing}")
    for stale in sorted(listed - actual):
        errors.append(f"README.md: skills table lists {stale}, which is not a skill")
    return errors


def report_failure(errors: list[str]) -> int:
    # Two checks reading the same unreadable file report it once.
    print("\n".join(dict.fromkeys(errors)))
    return 1


def main(root: Path = REPO_ROOT) -> int:
    plugin, marketplace, manifest_errors = load_manifests(root)
    if manifest_errors:
        # Every later check reads the manifests, so going on would only add misleading errors.
        return report_failure(manifest_errors)

    errors = check_manifests(root, plugin, marketplace)
    skill_dirs, skill_dir_errors = find_skill_dirs(root, plugin.get("skills", []))
    errors += skill_dir_errors
    errors += check_unlisted_skills(root, skill_dirs)
    for skill_dir in skill_dirs:
        errors += check_skill(root, skill_dir)
    errors += check_powerpack_names(root, skill_dirs)
    errors += check_readme_table(root, skill_dirs)

    if errors:
        return report_failure(errors)
    print(f"ok: {len(skill_dirs)} skill(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
