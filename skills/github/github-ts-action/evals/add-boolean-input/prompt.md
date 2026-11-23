---
tags: [github-ts-action]
max_turns: 25
timeout_seconds: 480
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

add a boolean input `fail_on_miss` (default false) to this action. When true and the cache misses, the run
should fail with a clear message. Input files: see files/
