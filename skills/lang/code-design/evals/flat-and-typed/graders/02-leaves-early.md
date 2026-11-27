---
type: llm
focus: trace
weight: 1
---

In the final Python code, no if branch that ends in return, raise, continue or break is followed by an else or
elif, and no loop body or function body consists solely of one if block wrapping its main work. Judge only
these two points. An if/elif/else whose branches do not leave, such as one choosing which problem to record,
is fine.
