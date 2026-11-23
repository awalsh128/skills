---
tags: [github-cicd]
max_turns: 20
timeout_seconds: 480
allowed_tools: [Read, Glob, Grep, Skill]
---

github-cicd: review .github/workflows/release.yml and report pass or fail per rule with file:line and the fix.
Edit nothing. The input files are in the working directory.
