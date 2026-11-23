---
tags: [npm-audit]
max_turns: 20
timeout_seconds: 480
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

an auto-filed issue "npm audit found vulnerabilities" is open (issue.md) and CI is red because of it. Fix it.
audit-now.json is the output of `npm audit --json` run on the current tree a minute ago. No network or shell
is available, so answer from the files here without running anything. Input files: see files/
