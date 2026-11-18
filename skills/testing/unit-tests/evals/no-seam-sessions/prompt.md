---
tags: [unit-tests]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

we have zero tests on src/auth/sessions.py and it's security-sensitive. sessions are supposed to expire after
30 min idle and hard-expire after 12h no matter what. add tests, there's an empty tests/ folder Input files:
see files/
