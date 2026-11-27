---
name: typescript
description:
  Use when the task creates, changes, refactors or reviews TypeScript (.ts, .tsx, .mts), including adding a
  module or feature. Adds the user's TypeScript specifics on top of code-design; gaps fall back to the Google
  TypeScript style guide. Not for plain JavaScript or other languages.
---

# typescript

This skill applies the user's TypeScript conventions. They are opinions: follow them even where common advice
differs. Use the `code-design` skill alongside it for readability, reuse, module layout and config data; this
skill adds only what is specific to TypeScript. A more specific skill (for example `github-ts-action`) layers
on top of this one.

## Precedence

1. The repo's own documented conventions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING`, lint and Prettier config)
   win inside that repo. When one contradicts a rule below, follow the repo and mention the conflict in your
   summary.
2. The rules in this skill, then `code-design`.
3. For anything neither covers, the Google TypeScript style guide:
   https://google.github.io/styleguide/tsguide.html (also published at https://ts.dev/style/). These rules win
   where the guide differs.

## Rules

### Platform APIs first

The platform already parses and formats most things; reach for these before a regex or a library:

- `new URL(input)` and its `hostname`, `pathname`, `searchParams`; `URLSearchParams` to build query strings;
  `node:path` for paths; `Intl` for number and date formatting.
- Built-ins and Node or browser APIs such as `structuredClone`, `Array.prototype.toSorted`, `AbortController`,
  `node:util` `parseArgs` and `fetch`.
- Check a candidate library with `npm view <pkg> dependencies dist.unpackedSize`. Prefer ESM and
  tree-shakeable packages, most of all for bundled output (browser, GitHub Actions, VS Code extensions).

### Types and modules

- Infer types where the code already says them (`ReturnType`, `typeof`, `satisfies`) rather than writing a
  parallel interface that can drift.
- Name the shared core module `core.ts` or `common.ts`, as `code-design` describes.
- Write `types.ts`, `constants.ts`, `utils.ts` or `helpers.ts` only when the repo's conventions require them.

### JSON and config

- Import JSON with `resolveJsonModule` (and `with { type: "json" }` under Node ESM) so TypeScript infers its
  type.
- For configuration that needs comments, use a typed `.ts` config (`export default { ... } satisfies Config`)
  or JSONC.

### Type safety and async

Do not restate these rules here; the tools own them and keep them current.

- Enable the typescript-eslint `strictTypeChecked` preset (https://typescript-eslint.io/users/configs) in new
  projects, and fix what it reports instead of silencing it. It covers `any`, unsafe assertions, floating
  promises, thrown non-errors and non-exhaustive `switch`. In an existing repo, keep its lint config and do
  not loosen it to clear an error.
- Keep `strict` on in `tsconfig.json`. For new projects also prefer `noUncheckedIndexedAccess`; check the
  current options in the TSConfig reference (https://www.typescriptlang.org/tsconfig) rather than from memory.
- Annotate the return types of exported functions: they are the public API, and inference there leaks internal
  types and hides breaking changes. Infer everything else.
- At a trust boundary (JSON, `fetch`, `process.env`) take `unknown` and narrow it with a guard or a schema
  parser the project already depends on, never an `as` cast.

## Related skills

Use these alongside when the task fits; they own their topics, so this skill does not copy them.

- `unit-tests` for the tests a change needs.
- `/mattpocock-skills:codebase-design` when the task is designing a module's interface or seam.
- `/mattpocock-skills:code-review` for a review against a base commit; apply these rules as its standards.

## Finishing

Done when `code-design`'s checks are met and `tsc --noEmit`, lint and tests have run (or the summary says
which could not). In a review, report findings with `file:line` and edit nothing until asked.
