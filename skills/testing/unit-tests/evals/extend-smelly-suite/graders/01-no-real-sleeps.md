---
type: llm
focus: trace
weight: 1
---

The newly added tests never wait on real time (no sleep or real setTimeout); time is controlled with the
injected now function or fake timers. Pre-existing tests are not judged.
