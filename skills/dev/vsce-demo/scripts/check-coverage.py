#!/usr/bin/env python3
"""Fail when demo/COVERAGE.md does not account for every feature, or does not match the scenes.

usage: check-coverage.py [extension-dir]

COVERAGE.md is a table whose first column holds feature ids in backticks (from inventory.py) and whose second
column is a scene name, followed by a "Not demoed" list of "- `id`: reason" lines. Checks, all must pass:
  - every id from inventory.py appears, as a scene row or as a not-demoed line with a reason
  - no scene cell is empty or TODO, and every named scene exists in demo/scenes
  - every scene file is imported by demo/scenes/index.ts and named in the table (a row may have no id, for a
    scene that shows a variant of a feature already listed)
  - no id in COVERAGE.md is stale (no longer in the inventory)
Standard library only.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import inventory  # noqa: E402


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    coverage_file, scenes_dir = root / "demo/COVERAGE.md", root / "demo/scenes"
    errors = []
    if not coverage_file.is_file():
        print(f"{coverage_file}: missing; run inventory.py and fill it in", file=sys.stderr)
        return 1

    expected = set(inventory(root)["features"])
    covered, not_demoed, rows = {}, {}, []
    for line in coverage_file.read_text().splitlines():
        if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            ids = re.findall(r"`([A-Za-z]+:[^`]+)`", cells[0])  # ids have a kind: prefix; other code spans are prose
            if len(cells) > 1 and cells[1].lower() != "scene":  # a row may name a scene and no id: a variant
                rows.append((ids, cells[1]))
        match = re.match(r"^\s*[-*]\s+`([A-Za-z]+:[^`]+)`\s*[:–-]\s*(.+)$", line)
        if match:
            not_demoed[match.group(1)] = match.group(2).strip()

    scene_names = {}
    for path in sorted(scenes_dir.glob("*.ts")):
        if path.name == "index.ts":
            continue
        for name in re.findall(r"\bname:\s*[\"']([^\"']+)[\"']", path.read_text()):
            scene_names[name] = path
    index_text = (scenes_dir / "index.ts").read_text() if (scenes_dir / "index.ts").is_file() else ""

    used = set()
    for ids, scene in rows:
        scene = scene.strip("` ")
        label = ", ".join(ids) or scene or "a row"
        if scene.upper() in {"", "TODO"}:
            errors.append(f"{label}: scene is {scene or 'empty'}")
            continue
        if scene not in scene_names:
            errors.append(f"{label}: scene {scene!r} has no file in demo/scenes")
        used.add(scene)
        for feature in ids:
            covered[feature] = scene
    for feature, reason in not_demoed.items():
        if len(reason) < 8:
            errors.append(f"{feature}: not-demoed reason {reason!r} is too short to be a reason")
    for feature in sorted(expected - set(covered) - set(not_demoed)):
        errors.append(f"{feature}: in the inventory, but neither demoed nor listed as not demoed")
    for feature in sorted((set(covered) | set(not_demoed)) - expected):
        errors.append(f"{feature}: in COVERAGE.md but no longer in the inventory (stale)")
    for name, path in scene_names.items():
        if name not in used:
            errors.append(f"scene {name!r} ({path.name}) is not named in COVERAGE.md")
        if f"./{path.stem}" not in index_text:
            errors.append(f"scene file {path.name} is not imported by demo/scenes/index.ts")

    for error in errors:
        print(f"FAIL {error}")
    print(f"{len(expected)} features, {len(covered)} demoed, {len(not_demoed)} not demoed, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
