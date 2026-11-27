---
type: llm
focus: trace
weight: 1
---

In the final Python code, each service file is turned into a named type such as a dataclass (endpoints
included) where it is read and validated. Checks made after that, such as duplicate ports and duplicate
endpoints, read attributes of that type and do not index or call .get on the raw JSON dictionaries.
