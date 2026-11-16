#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q . 2>/dev/null || true
git remote add origin https://github.com/jdoe/vscode-tidy.git 2>/dev/null || true
