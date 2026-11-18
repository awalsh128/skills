---
type: llm
focus: trace
weight: 1
---

The audit flags the package-level counter shared between TestPool and TestPool2 (order dependence, and a data
race since workers increment it concurrently)
