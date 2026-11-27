---
type: llm
focus: trace
weight: 1
---

The newly added tests do not read or set private members such as hits or capacity, including through an any
cast. Pre-existing tests are not judged.
