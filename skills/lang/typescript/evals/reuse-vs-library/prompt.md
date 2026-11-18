---
tags: [typescript]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

add an update check to the cli. it should compare our installed version (from package.json) with the latest release tag from the registry (tags look like v1.4.0 or v2.0.0-beta.3) and tell the user if there's a newer one, and print the release date in the user's local time zone like "Mar 4, 2026". also when we check plugin versions, send the plugin names to the registry in batches of 20 since the api caps the list. the registry client is in src/registry.ts
Input files: see files/
