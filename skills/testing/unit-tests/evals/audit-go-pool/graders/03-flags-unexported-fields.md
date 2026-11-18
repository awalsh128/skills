---
type: llm
focus: trace
weight: 1
---

The audit flags assertions on unexported fields p.errs and p.running as testing implementation details (and
unsynchronized reads), and suggests asserting via Close()'s returned errors or observable behavior instead
