---
type: llm
focus: trace
weight: 1
---

Time is controlled by an injected clock: SessionStore gains a constructor (or method) parameter for the time source, and tests pass a fake; time.time is not patched with monkeypatch, mock.patch or freezegun
