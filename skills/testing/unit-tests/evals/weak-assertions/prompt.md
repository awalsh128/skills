---
tags: [unit-tests, anti-pattern]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

cover parseConfig in src/parse-config.ts with unit tests, we use vitest. The input files are in the working
directory.
