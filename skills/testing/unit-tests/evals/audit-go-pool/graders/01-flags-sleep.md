---
type: llm
focus: trace
weight: 1
---

The audit flags the time.Sleep waits as flaky synchronization and proposes an event-based fix (waiting on
Close, a WaitGroup or channel, or testing/synctest)
