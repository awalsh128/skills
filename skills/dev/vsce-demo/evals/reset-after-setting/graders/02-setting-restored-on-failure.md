---
type: llm
focus: trace
weight: 1
---

The setting is put back to its default (`undefined`, not a hard-coded `true`) in a `finally` or a shared
reset, so a thrown scene or a re-run still starts clean.
