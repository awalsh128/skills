---
type: llm
focus: trace
weight: 1
---

In the final Python code, no function returns two or more values as a tuple or as a dictionary with fixed
keys. Each return value is a single value, a collection of one kind of item, or a named type such as a
dataclass or NamedTuple. Tuples used inside a function, for example as set members or dictionary keys, do not
count.
