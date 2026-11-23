---
name: unit-tests
description:
  Use when the task is writing, changing, fixing or judging unit tests in any language (Jest, Vitest, pytest,
  Go testing, JUnit, Rust), including the tests a feature or bug fix needs. Applies the user's conventions
  (public-API behavior, Arrange-Act-Assert, faked boundaries only). Not for integration, end-to-end, load or
  manual testing, nor for non-test code.
---

# unit-tests

This skill applies the user's unit-test conventions in any language. The rules are language-agnostic; the repo
supplies the framework, file layout and commands.

This skill covers what a good unit test looks like, not the workflow. When the user wants to work test-first
(red-green-refactor), use `/mattpocock-skills:tdd` alongside it and apply these rules to each test it has you
write. For a failing test or bug whose cause is unknown, use `/mattpocock-skills:diagnosing-bugs` first.

## Precedence

1. The repo's documented conventions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING`, test config) win inside that
   repo. When one contradicts a rule below, follow the repo and mention the conflict in your summary.
2. The rules in this skill.
3. For anything neither covers, the test framework's own documentation.

## Modes

- **Write**: the code has no tests yet. Add them.
- **Revise**: tests exist. Bring the tests you add or touch up to the rules, keep every behavior the old tests
  covered, and list wider issues as suggestions.
- **Audit**: the user asks whether tests are good or says "check". Report each finding with `file:line`, the
  rule, and the concrete fix. Edit nothing until asked.

## Before writing

Read the existing tests, the test runner config (`package.json` scripts, `vitest.config.*`, `pyproject.toml`,
`go.mod`, `pom.xml`, `Cargo.toml`) and CI. Match the framework, assertion library, file placement and naming
style already in use. Run the existing suite once so you know its starting state.

Then read a reference when the code under test needs it:

- UI components, DOM or browser code: `references/dom.md`.
- Threads, goroutines, async workers, locks, timers or anything order-dependent: `references/concurrency.md`.

## Rules

### Behavior through the public API

A test describes what the unit does for its callers, so it survives any refactor that keeps that behavior.

- Call the unit the way production code does and assert on what a caller can observe: return values, thrown
  errors, emitted events, state read back through public methods, calls across an external boundary.
- Leave private fields, internal helpers and call order between internal functions out of the assertions. A
  test that needs them is testing the implementation; find the observable outcome instead.
- Shipped code stays free of test-only exports, flags and branches. Make a unit testable by injecting what it
  depends on (clock, random source, HTTP client, file system root) through its constructor or parameters.
- When a public API has to change, prefer a backwards-compatible change so existing tests keep passing
  unedited; a test rewrite should mean the behavior changed.

### One behavior per test, in three parts

- Each test checks one behavior. Several asserts are fine when they describe that one outcome.
- Lay the body out as **Arrange, Act, Assert**, in that order, with a blank line between the parts. One Act
  per test.
- Name each test with three parts: the **method** (or unit), the **condition**, and the **expected result**.
  Express them in the framework's shape: `test_withdraw_insufficient_funds_raises_error` in pytest,
  `describe("withdraw")` > `it("throws when funds are insufficient")` in Jest,
  `TestWithdraw/insufficient_funds_returns_error` in Go. A reader should know what broke from the name alone.
- A regression test carries a comment linking the bug or issue it guards (`// Regression: #412`).

### Named values, kept local

- Give a meaningful input or expected value a name (`EXPIRED_TOKEN`, `const maxRetries = 3`) so the assert
  reads as intent. A literal whose meaning is obvious in place (`0`, `""`, `"alice"`) can stay a literal.
- Keep those names in the test file that uses them, beside the tests. Shared `testConstants` or `fixtures`
  grab-bag files only when the repo already uses them.

### Parameterize, but keep setup readable

- When cases differ only in data, write one table-driven or parameterized test (`it.each`,
  `@pytest.mark.parametrize`, a Go table with `t.Run`, `@ParameterizedTest`) and give each row a readable case
  name.
- Test every limit at three points: just below, exactly at, and just above (a timeout, a minimum length, a
  cap, a range end). The exact value is where `>` and `>=` differ, so it is the case that catches an
  off-by-one; a parameterized table holds all three. When the code's behavior at the exact value looks
  unintended, pin what it does and flag it in the summary.
- Favor readable tests over DRY tests. Each test shows the setup that matters to it; push only incidental
  setup into a small factory with defaults (`makeOrder({ status: "paid" })`). Deep `beforeEach` chains and
  shared fixtures that a reader must trace across the file cost more than a few repeated lines.

### Real dependencies, fake boundaries

- Use the real collaborator when it runs in-process, fast and deterministically: value objects, pure
  functions, in-memory stores, a temp directory.
- Replace what crosses a process or time boundary: network, external services, databases, the system clock,
  randomness, environment. Prefer a simple fake or the framework's fake timers to a mock that scripts every
  call.
- Mock only what you own an interface to, and assert on a mock's calls only when that call is the behavior
  under test (for example, "sends the receipt email").

### Isolated, parallel, deterministic

- Each test creates the data it needs and leaves nothing behind. No module-level mutable state, no order
  dependence between tests.
- Run tests in parallel where the framework supports it (`t.Parallel()`, Vitest and Jest workers,
  `pytest-xdist` if the repo uses it). Shared state is what makes parallel tests flaky; remove the sharing
  rather than serializing the suite.
- Control time and randomness instead of waiting on them: inject or fake the clock, seed the random source. A
  sleep in a unit test is a bug.

### Files and tools

- One test file per module, placed and named the way the repo already does (`cart.test.ts` beside `cart.ts`,
  `tests/test_cart.py`, `cart_test.go`, Rust `#[cfg(test)] mod tests`).
- Use the repo's framework, assertion and mocking libraries. Hand-roll a test helper only when nothing in them
  does the job, and keep it in the test file that uses it.

## Finishing

Done when every test you wrote or touched is checked against the rules above and the full suite has run.

- Run the tests you wrote or changed, then the full suite. Say plainly what failed or what you could not run.
- Summarize: behaviors covered, any boundary you faked and why, repo conventions that overrode these rules,
  and suggested follow-ups you left alone (for example, production code that needs a seam to be testable).

## Sources

For people maintaining this skill; the agent does not need to fetch them.

- [Microsoft: unit testing best practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)
- [Code With Engineering Playbook: unit testing](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/unit-testing/)
- [Google: testing content-driven backends](https://developers.google.com/solutions/content-driven/backend/testing)
- Framework docs: [Jest](https://jestjs.io/docs/),
  [pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html),
  [Go testing](https://pkg.go.dev/testing),
  [Go best practices](https://google.github.io/styleguide/go/best-practices.html),
  [JUnit](https://docs.junit.org/current/user-guide/),
  [Rust: writing tests](https://doc.rust-lang.org/book/ch11-01-writing-tests.html),
  [Rust: test organization](https://doc.rust-lang.org/book/ch11-03-test-organization.html)
