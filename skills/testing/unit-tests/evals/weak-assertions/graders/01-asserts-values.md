---
type: llm
focus: trace
weight: 1
---

Every successful-parse test asserts concrete values of the returned config. None relies only on toBeDefined,
toBeTruthy, not.toThrow, toBeInstanceOf(Object) or a length check.
