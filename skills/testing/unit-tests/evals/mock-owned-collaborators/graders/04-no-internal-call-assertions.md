---
type: llm
focus: trace
weight: 1
---

No assertion checks calls to the repository or to totalCents (such as toHaveBeenCalledWith on save or find).
Outcomes are checked through return values, thrown errors, repository state or the payment boundary.
