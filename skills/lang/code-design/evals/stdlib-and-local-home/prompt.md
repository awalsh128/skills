---
tags: [code-design]
max_turns: 20
timeout_seconds: 480
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

add a `weekly_totals(csv_path)` function that reads sales.csv (columns date as YYYY-MM-DD, amount) and returns
the total amount per ISO week as a dict keyed by "YYYY-Www". The input files are in the working directory.
