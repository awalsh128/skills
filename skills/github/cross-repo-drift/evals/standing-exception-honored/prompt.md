---
tags: [cross-repo-drift]
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Write, Edit]
---

cross-repo-drift: DRIFT_CHECK_CMD is "python3 ../check.py" and the exceptions are in
demo/.agents/standards-overrides.json. Tell me whether rule line-width in ./demo still needs fixing. The skill
is in ./skill (SKILL.md, references, scripts). No shell is available in this session, so answer from those
files and the ones here without running anything.
