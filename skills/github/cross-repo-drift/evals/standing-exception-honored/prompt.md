---
tags: [cross-repo-drift]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

cross-repo-drift: with DRIFT_CHECK_CMD="python3 ../check.py", verify rule line-width in ./demo with
`drift.py verify`, and tell me whether it still needs fixing.
