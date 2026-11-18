---
type: llm
focus: trace
weight: 1
---

The new parameter has a default that keeps current behavior (time.time), so src/auth/app.py works unchanged
and SessionStore() still constructs with no arguments
