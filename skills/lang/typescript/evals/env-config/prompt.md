---
tags: [typescript]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

right now the api url and key are hardcoded in src/index.ts. i need dev, staging and prod settings (api base
url, request timeout, and an enableCache flag) and the key shouldn't be in the code. set that up Input files:
see files/
