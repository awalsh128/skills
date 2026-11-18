---
type: llm
focus: trace
weight: 1
---

The 300 ms debounce is handled with fake timers (vi.useFakeTimers with advanceTimers) or findBy/waitFor on an observable change, never a fixed real-time sleep or setTimeout in the test
