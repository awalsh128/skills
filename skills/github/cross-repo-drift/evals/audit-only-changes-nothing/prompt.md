---
tags: [cross-repo-drift]
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Write, Edit]
---

cross-repo-drift audit, just tell me what has drifted. Don't change anything. The skill is in ./skill
(SKILL.md, references, scripts). No shell is available in this session, so answer from those files and the
ones here without running anything.
