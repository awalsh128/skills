---
tags: [typescript]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

add a parseRepoUrl function to src/links.ts that takes a github url like https://github.com/owner/repo/tree/main/src/index.ts and gives back the owner, repo, branch and path. it should also work with just https://github.com/owner/repo
Input files: see files/
