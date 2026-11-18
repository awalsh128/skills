# DOM and UI tests

Read this when the unit under test renders UI or touches the DOM. The core rules in `SKILL.md` still apply; this file covers what changes when the "public API" is a screen.

## Test what the user perceives

The public API of a component is what a user sees and does. Query and assert on that, so a markup or styling refactor leaves the tests green.

- Find elements the way a user or assistive technology does, in this order: `getByRole` (with `name`), `getByLabelText`, `getByPlaceholderText`, `getByText`, `getByDisplayValue`. Use `getByTestId` only when no accessible query can reach the element, and say why in a comment.
- Leave CSS selectors, `container.querySelector`, component instance internals and component state out of tests. Adding a `data-testid` to shipped markup just to reach an element is a test-only change; prefer an accessible name, which also improves the component.
- Assert on visible outcomes: text shown, element present or gone, `toBeDisabled`, `toHaveValue`, `toHaveAccessibleName`, a callback prop called with the right value.

## Interact like a user

- Drive input with `@testing-library/user-event` (`await user.type(...)`, `await user.click(...)`) over `fireEvent`; it fires the full event sequence a browser would. Create the instance per test with `userEvent.setup()`.
- Wait for async UI with `findBy*` or `waitFor` on an observable change. Never wait with a fixed timeout.
- For debounces and timers, use fake timers and hand them to user-event so its own internal delays advance too: `vi.useFakeTimers({ shouldAdvanceTime: true })` with `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })` (Jest: `jest.advanceTimersByTime`). Then step the clock explicitly (`await vi.advanceTimersByTimeAsync(300)`) to the moment under test. Without the `advanceTimers` option user-event hangs under fake timers; fix it with that option, not by stubbing a global `jest` object in Vitest.
- Fake the network at the boundary (MSW, or an injected client) rather than mocking the component's own data hooks.

## Framework libraries

Use the Testing Library flavour that matches the repo: [React](https://testing-library.com/docs/react-testing-library/intro/), [DOM](https://testing-library.com/docs/dom-testing-library/intro/), [Angular](https://testing-library.com/docs/angular-testing-library/intro/), [Vue Test Utils](https://test-utils.vuejs.org/), [Svelte](https://svelte.dev/docs/svelte/add_svelte_test).

## When a unit test is the wrong level

Behavior that needs real layout, navigation across pages, or several services together belongs in a browser end-to-end test with the repo's tool ([Playwright](https://playwright.dev/docs/intro), [Cypress](https://docs.cypress.io/), [Selenium](https://www.selenium.dev/documentation/), [WebdriverIO](https://webdriver.io/docs/gettingstarted)). Suggest one in the summary rather than forcing it into a jsdom unit test.
