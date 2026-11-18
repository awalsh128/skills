---
type: llm
focus: trace
weight: 1
---

Discount cases that differ only in data (percent off, cap, rounding or rejection reasons) are written as one
parameterized test (it.each/test.each or a case table looped over), not copy-pasted tests
