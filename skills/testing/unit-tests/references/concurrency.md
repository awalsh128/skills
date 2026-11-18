# Concurrent and asynchronous code

Read this when the unit under test runs work on threads, goroutines, async tasks or timers, or when its result depends on ordering. The core rules in `SKILL.md` still apply; this file is about making such tests deterministic.

## Synchronize on events, not time

A test that sleeps and hopes the work finished is flaky on a slow CI machine and slow everywhere else.

- Wait on the thing that signals completion: a returned promise or future, a channel receive, `sync.WaitGroup`, `CountDownLatch`, `join()`, an awaited event. Bound the wait with a timeout that fails the test, not one that lets it pass.
- Replace real time with controlled time: inject a clock, or use the framework's fake time (`vi.useFakeTimers()` / `jest.useFakeTimers()`, Go `testing/synctest`, a fake `Clock` in Java, `tokio::time::pause()` in Rust). Advance it explicitly to the moment under test.
- Test the logic apart from the scheduling where you can: a worker's per-item function is often a plain unit test, and only a thin layer needs the concurrent harness.

## Make ordering bugs reproducible

- Run with the race or thread-safety detector the language offers (`go test -race`, ThreadSanitizer, `loom` for Rust) and say in the summary whether you did.
- Assert on outcomes that hold for every valid interleaving (the final count, the set of results), not on one particular order unless order is the contract.
- For logic where interleavings matter, use a tool that explores schedules systematically rather than a loop that runs the test many times and hopes: [Coyote](https://microsoft.github.io/coyote/) (.NET), [VMLens](https://www.vmlens.com/) (Java), [`loom`](https://github.com/tokio-rs/loom) (Rust), Go `testing/synctest` for time-driven code.
- Give each test its own instances of pools, queues and caches so parallel tests cannot interfere.

## Further reading

- [JUnit wiki: multithreaded code and concurrency](https://github.com/junit-team/junit4/wiki/multithreaded-code-and-concurrency)
- [Baeldung: testing multi-threaded code in Java](https://www.baeldung.com/java-testing-multithreaded)
- [ConcurrentUnit](https://github.com/jhalterman/concurrentunit), [tempus-fugit](https://github.com/tobyweston/tempus-fugit), [MultithreadedTC](https://www.cs.umd.edu/projects/PL/multithreadedtc/)
