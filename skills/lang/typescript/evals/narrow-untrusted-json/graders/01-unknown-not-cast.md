---
type: llm
focus: trace
weight: 1
---

The response body is typed unknown (or read through a type-checked guard), and it is never converted to the
user type or to any with an as cast. A cast to Record<string, unknown> inside a type guard, used only to read
properties, is allowed
