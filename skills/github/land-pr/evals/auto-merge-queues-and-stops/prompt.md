---
tags: [land-pr]
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Write, Edit]
---

land-pr: queue PR 12 to auto-merge. The skill is in ./skill. No shell is available in this session: gh and git
do not run, and the output of each command is in the files here (pr.json is `gh pr view 12 --json ...`,
repo.json is `gh repo view --json ...`, checks.txt is `gh pr checks 12`, git.txt holds the git output). The
files here only hold those outputs and are not part of the repository, so ignore them when you judge the
working tree. Treat each output as the real, current result of that command. Still list every command the
skill calls for, and do not add a command only to re-check an output. List the exact commands you would run,
in order, and stop wherever the skill says to stop. Change nothing.
