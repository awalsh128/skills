---
type: llm
focus: trace
weight: 1
---

Each newly added test builds its own RateLimiter and does not depend on another test having run. Pre-existing
tests are not judged.
