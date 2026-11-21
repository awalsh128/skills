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
- Keep a regex short and named (`const SEMVER_TAG = /^v\d+\.\d+\.\d+$/`).
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

## Finishing

Done when `code-design`'s checks are met and `tsc --noEmit`, lint and tests have run (or the summary says
which could not).
