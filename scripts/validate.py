#!/usr/bin/env python3
"""Deterministic repo checks: no network, no model calls. Needs the packages in requirements.txt."""

import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = ".claude-plugin/plugin.json"
MARKETPLACE_JSON = ".claude-plugin/marketplace.json"
REQUIRED_MARKETPLACE_KEYS = ("name", "owner", "plugins")
POWERPACK_NAME = b"gh-dev-powerpack"

FRONTMATTER = re.compile(r"---\n(.*?)\n---\n", re.S)
REFERENCE_PATH = re.compile(r"`(references/[\w./-]+\.md)`")
# Scripts and templates a skill tells the agent to run or copy, bare or as `<skill dir>/scripts/x`.
BARE_SCRIPT_PATH = re.compile(r"`((?:scripts|templates)/[\w./-]+)`")
SKILL_DIR_SCRIPT_PATH = re.compile(r"<skill dir>/((?:scripts|templates)/[\w./-]+)")
README_SKILL_LINK = re.compile(r"\]\((skills/[\w./-]+?)/SKILL\.md\)")


class UnusableInput(Exception):
    """Input the checks cannot work with. Each argument is one problem to report."""


# Fields typed as object are only compared and reported, so any JSON or YAML value is kept as written.
@dataclass(frozen=True)
class PluginManifest:
    name: object
    version: object
    description: object
    skills_paths: list[str]


@dataclass(frozen=True)
class MarketplaceEntry:
    name: object
    version: object
    description: object
    source: str | None  # None unless the source is a path


@dataclass(frozen=True)
class Marketplace:
    description: object
    entries: list[MarketplaceEntry] | None  # None when there is no plugins key
    missing_keys: list[str]


@dataclass(frozen=True)
class Manifests:
    plugin: PluginManifest
    marketplace: Marketplace


@dataclass(frozen=True)
class Frontmatter:
    name: object
    description: object


def read_text(root: Path, path: Path | str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise UnusableInput(f"{path}: {error}") from error


def read_json_object(root: Path, path: str) -> dict:
    text = read_text(root, path)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise UnusableInput(f"{path}: {error}") from error
    if not isinstance(data, dict):
        raise UnusableInput(f"{path}: must be a JSON object")
    return data


def read_json_objects(root: Path, paths: Sequence[str]) -> list[dict]:
    """Read every file, so that one run reports all the unreadable ones."""
    documents = []
    problems = []
    for path in paths:
        try:
            documents.append(read_json_object(root, path))
        except UnusableInput as error:
            problems.extend(error.args)
    if problems:
        raise UnusableInput(*problems)
    return documents


def check_manifest_shapes(plugin: dict, marketplace: dict) -> list[str]:
    """Check the types parsing relies on. A missing key is left for the later checks to report."""
    problems = []
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        problems.append("marketplace.json: plugins must be a list of objects")
    skills_paths = plugin.get("skills", [])
    if not isinstance(skills_paths, list) or not all(
        isinstance(path, str) and not Path(path).is_absolute() for path in skills_paths
    ):
        problems.append("plugin.json: skills must be a list of relative paths")
    return problems


def parse_plugin(data: dict) -> PluginManifest:
    return PluginManifest(
        name=data.get("name"),
        version=data.get("version"),
        description=data.get("description"),
        skills_paths=data.get("skills", []),
    )


def parse_entry(data: dict) -> MarketplaceEntry:
    source = data.get("source")
    return MarketplaceEntry(
        name=data.get("name"),
        version=data.get("version"),
        description=data.get("description"),
        source=source if isinstance(source, str) else None,
    )


def parse_marketplace(data: dict) -> Marketplace:
    entries = None
    if "plugins" in data:
        entries = [parse_entry(entry) for entry in data["plugins"]]
    return Marketplace(
        description=data.get("description"),
        entries=entries,
        missing_keys=[key for key in REQUIRED_MARKETPLACE_KEYS if key not in data],
    )


def load_manifests(root: Path) -> Manifests:
    plugin, marketplace = read_json_objects(root, (PLUGIN_JSON, MARKETPLACE_JSON))
    problems = check_manifest_shapes(plugin, marketplace)
    if problems:
        raise UnusableInput(*problems)
    return Manifests(parse_plugin(plugin), parse_marketplace(marketplace))


def check_stale_field(key: str, listed: object, actual: object) -> list[str]:
    # plugin.json wins at install time, so a stale entry is silently ignored (AGENTS.md).
    if listed == actual:
        return []
    return [f"marketplace.json: entry {key} {listed!r} != plugin.json {key} {actual!r}"]


def compare_entry(plugin: PluginManifest, entry: MarketplaceEntry) -> list[str]:
    if entry.name != plugin.name:
        return [f"marketplace.json: entry name {entry.name!r} != plugin.json name {plugin.name!r}"]
    stale_version = check_stale_field("version", entry.version, plugin.version)
    stale_description = check_stale_field("description", entry.description, plugin.description)
    return stale_version + stale_description


def check_entry(root: Path, plugin: PluginManifest, entry: MarketplaceEntry) -> list[str]:
    problems = compare_entry(plugin, entry)
    if entry.source is None or (root / entry.source).is_dir():
        return problems
    return [*problems, f"marketplace.json: source {entry.source!r} does not exist"]


def check_manifests(root: Path, manifests: Manifests) -> list[str]:
    plugin = manifests.plugin
    marketplace = manifests.marketplace
    # A key absent from both manifests would otherwise count as consistent.
    required = {"name": plugin.name, "version": plugin.version, "description": plugin.description}
    problems = [f"plugin.json: missing {key}" for key, value in required.items() if not value]
    if marketplace.entries == []:
        problems.append("marketplace.json: plugins has no entry for the plugin")
    for entry in marketplace.entries or []:
        problems.extend(check_entry(root, plugin, entry))
    if marketplace.description != plugin.description:
        problems.append(
            f"marketplace.json: description {marketplace.description!r} != plugin.json description"
        )
    problems.extend(f"marketplace.json: missing {key}" for key in marketplace.missing_keys)
    return problems


def find_skill_dirs(root: Path, skills_paths: list[str]) -> list[Path]:
    return [skill_md.parent for path in skills_paths for skill_md in (root / path).glob("*/SKILL.md")]


def check_skills_paths(root: Path, skills_paths: list[str], skill_dirs: list[Path]) -> list[str]:
    problems = [
        f"plugin.json: skills path {path!r} does not exist"
        for path in skills_paths
        if not (root / path).is_dir()
    ]
    if not skill_dirs:
        problems.append("no SKILL.md found under plugin.json skills paths")
    return problems


def is_eval_or_generated(path: Path) -> bool:
    """Whether a repo-relative path is eval input, run output or a cache rather than part of a skill."""
    skipped_names = {"evals", "__pycache__", "node_modules"}
    return any(part in skipped_names or part.endswith("-workspace") for part in path.parts)


def check_unlisted_skills(root: Path, skill_dirs: list[Path]) -> list[str]:
    """A skill in a group plugin.json does not list is never installed."""
    problems = []
    for skill_md in sorted(root.glob("skills/*/*/SKILL.md")):
        label = skill_md.relative_to(root)
        if skill_md.parent not in skill_dirs and not is_eval_or_generated(label):
            problems.append(f"{label}: its group is not listed under skills in plugin.json")
    return problems


def parse_frontmatter(label: Path, text: str) -> Frontmatter:
    match = FRONTMATTER.match(text)
    if not match:
        raise UnusableInput(f"{label}: missing frontmatter")
    try:
        # The blank line stands in for the opening ---, so YAML error line numbers match the file's.
        data = yaml.safe_load("\n" + match.group(1))
    # ValueError: a value shaped like a date but out of range.
    except (yaml.YAMLError, ValueError) as error:
        one_line_error = " ".join(str(error).split())
        raise UnusableInput(f"{label}: invalid YAML frontmatter: {one_line_error}") from error
    if not isinstance(data, dict):
        raise UnusableInput(f"{label}: frontmatter is not a mapping")
    return Frontmatter(name=data.get("name"), description=data.get("description"))


def check_frontmatter(label: Path, text: str, folder_name: str) -> list[str]:
    try:
        frontmatter = parse_frontmatter(label, text)
    except UnusableInput as error:
        return list(error.args)
    problems = []
    if frontmatter.name != folder_name:
        problems.append(f"{label}: name {frontmatter.name!r} != folder {folder_name!r}")
    description = frontmatter.description
    if not isinstance(description, str) or not description.strip():
        problems.append(f"{label}: description must be a non-empty string")
    return problems


def check_referenced_files(label: Path, text: str, skill_dir: Path) -> list[str]:
    problems = []
    for reference in REFERENCE_PATH.findall(text):
        if not (skill_dir / reference).is_file():
            problems.append(f"{label}: referenced {reference} does not exist")
    bare_scripts = set(BARE_SCRIPT_PATH.findall(text))
    skill_dir_scripts = set(SKILL_DIR_SCRIPT_PATH.findall(text))
    for script in sorted(bare_scripts | skill_dir_scripts):
        if not (skill_dir / script).exists():
            problems.append(f"{label}: referenced {script} does not exist")
    return problems


def check_skill(root: Path, skill_dir: Path) -> list[str]:
    label = skill_dir.relative_to(root) / "SKILL.md"
    try:
        text = read_text(root, label)
    except UnusableInput as error:
        return list(error.args)
    return check_frontmatter(label, text, skill_dir.name) + check_referenced_files(label, text, skill_dir)


def check_file_for_powerpack_name(root: Path, path: Path) -> list[str]:
    label = path.relative_to(root)
    if not path.is_file() or is_eval_or_generated(label):
        return []
    try:
        content = path.read_bytes()
    except OSError as error:
        return [f"{label}: {error}"]
    return [
        f"{label}:{line_number}: names gh-dev-powerpack; refer to the dev-powerpack-exemplars skill instead"
        for line_number, line in enumerate(content.splitlines(), 1)
        if POWERPACK_NAME in line
    ]


def check_powerpack_names(root: Path, skill_dirs: list[Path]) -> list[str]:
    """Skills stay disjoint from gh-dev-powerpack (AGENTS.md), so none names its repo or paths.

    Only the dev-powerpack-exemplars skill reads it. Every file is scanned, whatever its type.
    """
    problems = []
    for skill_dir in skill_dirs:
        for path in sorted(skill_dir.rglob("*")):
            problems.extend(check_file_for_powerpack_name(root, path))
    return problems


def check_readme_table(root: Path, skill_dirs: list[Path]) -> list[str]:
    """The README skills table must link every skill, and only skills that exist."""
    try:
        readme = read_text(root, "README.md")
    except UnusableInput as error:
        return list(error.args)
    listed = set(README_SKILL_LINK.findall(readme))
    actual = {str(skill_dir.relative_to(root)) for skill_dir in skill_dirs}
    problems = [f"README.md: skills table is missing {missing}" for missing in sorted(actual - listed)]
    problems.extend(
        f"README.md: skills table lists {stale}, which is not a skill" for stale in sorted(listed - actual)
    )
    return problems


def check_repo(root: Path, manifests: Manifests, skill_dirs: list[Path]) -> list[str]:
    problems = check_manifests(root, manifests)
    problems.extend(check_skills_paths(root, manifests.plugin.skills_paths, skill_dirs))
    problems.extend(check_unlisted_skills(root, skill_dirs))
    for skill_dir in skill_dirs:
        problems.extend(check_skill(root, skill_dir))
    problems.extend(check_powerpack_names(root, skill_dirs))
    problems.extend(check_readme_table(root, skill_dirs))
    return problems


def report_failure(problems: Sequence[str]) -> int:
    # Two checks reading the same unreadable file report it once.
    print("\n".join(dict.fromkeys(problems)))
    return 1


def main(root: Path = REPO_ROOT) -> int:
    try:
        manifests = load_manifests(root)
    except UnusableInput as error:
        # Every later check reads the manifests, so going on would only add misleading errors.
        return report_failure(error.args)

    skill_dirs = find_skill_dirs(root, manifests.plugin.skills_paths)
    problems = check_repo(root, manifests, skill_dirs)
    if problems:
        return report_failure(problems)
    print(f"ok: {len(skill_dirs)} skill(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
