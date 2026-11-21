#!/usr/bin/env bash
set -eu
if [ -d "$(dirname "$0")/files" ]; then cp -R "$(dirname "$0")/files/." .; fi
git init -q . 2>/dev/null || true
