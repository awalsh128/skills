---
name: github-ts-action
description:
  Create, scaffold, extend or review a TypeScript GitHub Action (JavaScript action running on node24) to the
  user's own conventions - src/index.ts plus a testable runner, rollup bundle to dist/action/index.js, vitest,
  semantic-release, SHA-pinned workflows. Use only when the project is a GitHub Action (it has or needs an
  action.yml), meaning the user wants a new one in TypeScript, asks to add an input, output or feature to an
  existing one, says "github-ts-action", or asks whether an action repo follows their standards. Not for
  general TypeScript outside a GitHub Action (use typescript), nor for composite or Docker actions, reusable
  workflows, or the action's README (use create-readme).
---

# github-ts-action

This skill applies the user's conventions for TypeScript GitHub Actions. They are opinions: follow them even
where common advice differs. Exemplar: https://github.com/awalsh128/cache-apt-pkgs-action on branch `main-2`
(read a local clone only if one exists; otherwise
`gh api repos/awalsh128/cache-apt-pkgs-action/contents/<path>?ref=main-2`).

## Modes

- **Scaffold**: no action yet. Create the layout below.
- **Extend**: action exists. Add inputs, outputs or logic while keeping the layers separate (see
  **Architecture**).
- **Review**: report pass/fail per convention with file references. Edit nothing until asked.

## Before writing

1. Read `action.yml`, `package.json`, `tsconfig*.json`, `.github/workflows/` and `src/` if they exist. Match
   what is there before applying the defaults below.
2. `git remote -v` for the real owner/repo. Never hardcode either.
3. Ask what the action does, its inputs and outputs, if not evident. Do not invent behavior.
4. Check the latest major versions of dependencies and actions (`npm view <pkg> version`, `gh api`) instead of
   copying the exemplar's numbers.

## Layout

```text
action.yml                 runs: using node24, main: dist/action/index.js
src/index.ts               entrypoint only: read inputs, call runner, set outputs, fail
src/action.ts              ActionInputs, ActionOutputs, ActionRunner, runAction()
src/<domain>.ts            domain modules, one concern each
src/instrumentation.ts     loggers and diagnostic artifacts (when the action needs them)
test/*.test.ts             vitest, one file per src module
scripts/dev/ scripts/ops/  repo tooling (.mts, run with node --experimental-strip-types)
.github/actions/setup/     composite action: setup-node, npm ci, cached build
.github/workflows/ci.yml   build once, then lint, typecheck, CodeQL, test, integration
release.config.ts          semantic-release
AGENTS.md                  agent rules (see references/ci-and-release.md)
```

`dist/` is gitignored and built in CI. Do not hand-edit it.

## Architecture

1. **`index.ts` is thin and untested glue.** It is the only file that touches `@actions/core` inputs and
   outputs. It is excluded from coverage.
2. **Typed inputs and outputs.** `ActionInputs` and `ActionOutputs` are `readonly` interfaces in `action.ts`.
   `getInputs()` in `index.ts` validates: `core.getInput(name, { required: true })`, `core.getBooleanInput`
   for booleans, and a `parseX` function that throws a clear error for enum-like strings. Input names are
   `snake_case` (match `action.yml`); output names are `kebab-case`; TypeScript fields are camelCase.
3. **`runAction(inputs, ...deps)` is the testable core.** Wrap logic in an `ActionRunner` class with
   dependencies (cache, command runner, logger) passed to the constructor, and export a plain `runAction`
   function over it. No `process.env` or `@actions/core` reads inside; tests pass mocks.
4. **Fail explicitly.** `main()` wraps everything in try/catch and calls `core.setFailed(message)` with
   `error instanceof Error ? error.message : String(error)`. No silent fallbacks.
5. **Diagnostics are optional and never fatal.** Upload logs as an artifact only when `debug` or on failure,
   in `finally`, and turn a failed upload into `core.warning`. Artifact names are unique per run, attempt, job
   and step.
6. **Boundaries.** If a sibling library owns a domain (the exemplar's `ts-apt` owns every `apt`/`dpkg` call),
   never reimplement it in `src/`. Add a method there and call it.
7. **Docs.** TSDoc on every exported type and function (`@param`, `@returns`, `@throws`). Comment the
   non-obvious why, not the what.

## Conventions

- **Node**: `engines.node >=24`, `.node_ver` holds the major, `action.yml` uses `node24`.
- **ESM**: `"type": "module"`, relative imports end in `.js`, `module`/`moduleResolution` `nodenext`, strict
  TS with `noUncheckedIndexedAccess`.
- **Bundle**: `tsc -p tsconfig.build.json` to `dist/src`, then rollup bundles `dist/src/index.js` to a single
  self-contained `dist/action/index.js` (ES format, `createRequire` banner, nodeResolve, commonjs, json).
  Actions do not run `npm install`. Files the bundle needs at runtime (shell scripts) are copied by a rollup
  `writeBundle` plugin, and `chmod`ed at startup because artifacts drop file modes.
- **Dependencies**: `@actions/core`, `@actions/cache`, `@actions/artifact` as needed; `winston` for logging.
  Pin sibling libraries to an exact version, never a range.
- **Formatting**: Prettier `printWidth` 110. Lint with ESLint flat config and `@typescript-eslint/parser`.
- **Bash**: `shellcheck`-clean with `set -euo pipefail`.
- **Branding**: `action.yml` has `name`, `description`, `author`, `branding` (Feather icon and color), and
  every input and output has a `description`. Defaults for booleans are the strings `"true"`/`"false"`.

## Tests

- Vitest, `globals: true`, `environment: node`, `include: ["test/**/*.test.ts"]`, v8 coverage over
  `src/**/*.ts` excluding `src/index.ts`. Run as `vitest run --coverage`.
- Name tests `<method> <conditions> <expected>`. Test behavior, not implementation. No control flow in test
  bodies. Constants when the value doesn't matter. Parameterize repeated cases.
- Mock at the dependency seam (`vi.mock` on the library, or hand-built mock objects cast `as never`), not by
  patching internals.
- CI also enforces `type-coverage --at-least 95`.

## CI, release and repo tooling

For the staging/main promotion, nightly candidates and OIDC-based release flow, use the `github-cicd` skill
alongside this one. Read `references/ci-and-release.md` before writing workflows, the setup action, release
config, `AGENTS.md` or package scripts. Read `references/configs.md` before writing `tsconfig*`,
`rollup.config.mjs`, `vitest.config.ts`, `eslint.config.js` or `package.json`.

Hard rules:

- Every `uses:` pinned to a full commit SHA with a `# vX.Y.Z` comment. Resolve SHAs with
  `gh api repos/<owner>/<repo>/git/ref/tags/<tag>`, never from memory.
- Least-privilege `permissions:` per job (`contents: read` by default).
- Build once, upload the bundle as an artifact, and have integration jobs run it with `uses: ./`.
- `main` is stable, `staging` is the prerelease branch (`rc`), released by semantic-release from Conventional
  Commits.

## Finishing

- Verify before claiming done: `npx tsc -p tsconfig.json --noEmit`, `npm run lint`, `npx vitest run`, and
  `npm run build` confirming `dist/action/index.js` exists. Say plainly what you could not run.
- Don't commit unless asked. Do not publish, tag or push a release without confirmation.
- Summarize: files created or changed, assumptions (Node version, dependency versions, branch names),
  unverified items, and suggestions (README via `create-readme`, Codecov setup, Sponsors, missing
  CONTRIBUTING).
