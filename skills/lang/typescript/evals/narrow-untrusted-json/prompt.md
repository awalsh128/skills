---
tags: [typescript]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

add a fetchUser(id) function to src/api.ts that gets https://example.com/api/users/<id>, which returns { "id":
number, "name": string, "email": string | null }, and gives back a typed user. the response comes from a
server we don't control Input files: see files/
