#!/usr/bin/env bash
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
skill="$here/../.."
[ -f "$skill/SKILL.md" ] || { echo "skill directory not found at $skill" >&2; exit 1; }
if [ -d "$here/files" ]; then cp -R "$here/files/." .; fi
mkdir skill && cp -R "$skill/SKILL.md" "$skill/references" "$skill/scripts" skill/
git init -q . 2>/dev/null || true
