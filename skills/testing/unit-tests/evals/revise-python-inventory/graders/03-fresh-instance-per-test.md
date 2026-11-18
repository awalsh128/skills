---
type: llm
focus: trace
weight: 1
---

There is no module-level Inventory shared between tests; each test builds its own (directly, via a factory, or via a function-scoped fixture), so tests pass in any order
