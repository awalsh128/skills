---
tags: [code-design]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

add a `check_services(root)` function in fleet/catalog.py that reads every services/<folder>/service.json
under root and gives back how many services it checked along with the problems it found. problems: the file is
not valid JSON, name, owner or port is missing or the wrong type, name does not match the folder, two services
use the same port, an endpoint is missing path or method, a method other than GET, POST, PUT or DELETE, and
the same method and path listed twice in one service. The input files are in the working directory.
