---
name: typescript
description: Write, modify or review TypeScript to the user's own conventions - readable over terse (URL over regex), platform and small libraries over hand-rolled code, single-responsibility modules named for their job (no utils, helpers or managers), types and constants co-located with the code that uses them (no types.ts or constants.ts), JSON for data and per-environment config. Use whenever creating or changing .ts, .tsx or .mts code, adding a module or feature, refactoring, or reviewing TypeScript, even if the user never mentions style. Gaps fall back to the Google TypeScript style guide.
---

# typescript

This skill applies the user's TypeScript conventions. They are opinions: follow them even where common advice differs.

## Precedence

1. The repo's own documented conventions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING`, lint and Prettier config) win inside that repo. When one contradicts a rule below, follow the repo and mention the conflict in your summary.
2. The rules in this skill.
3. For anything neither covers, the Google TypeScript style guide: https://google.github.io/styleguide/tsguide.html (also published at https://ts.dev/style/). These rules win where the guide differs.

A more specific skill (for example `github-ts-action`) layers on top of this one.

## Modes

- **Write**: new code. Apply every rule.
- **Modify**: existing code. Apply the rules to the code you add or touch, and match the file's surroundings otherwise. List wider violations as suggestions instead of restructuring files the task did not touch.
- **Review**: report each finding with `file:line`, the rule, and the concrete fix. Edit nothing until asked.

## Before writing

Read the neighbouring files, `package.json` (what is already a dependency), `tsconfig*.json` and the lint config. The environment answers "what is available"; these rules answer "what to prefer".

## Rules

### Readable over terse

Write the version a newcomer understands on first read, even when it is longer.

- Parse structured strings with the structured API: `new URL(input)` and its `hostname`, `pathname`, `searchParams`; `URLSearchParams` to build query strings; `node:path` for paths; `Intl` for number and date formatting. A regex is the right tool only for a genuinely pattern-shaped string, kept short and named (`const SEMVER_TAG = /^v\d+\.\d+\.\d+$/`).
- Name intermediate values instead of chaining long one-liners. Prefer early returns and `if` blocks to nested ternaries. Prefer plain loops or a single `map`/`filter` to a clever `reduce`.
- Comment the non-obvious why, not the what.

### Reuse before writing

Decide in this order and stop at the first that fits:

1. **The platform**: JavaScript built-ins and Node or browser APIs (`URL`, `structuredClone`, `Intl`, `Array.prototype.toSorted`, `AbortController`, `node:util` `parseArgs`, `fetch`).
2. **A dependency already in `package.json`.**
3. **A new library**, when it is well maintained and light for what it buys: few transitive dependencies, ESM and tree-shakeable, small next to the code it replaces. Check with `npm view <pkg> dependencies dist.unpackedSize` rather than from memory. Weight matters most for bundled output (browser, GitHub Actions, VS Code extensions).
4. **Write it yourself** when it is simple: a few lines, no tricky edge cases, cheaper to read than a dependency is to audit.

Domains full of edge cases always go to a library or the platform, never a hand-rolled version: dates and time zones, CSV, YAML, semver, globs, shell quoting, crypto, HTML escaping.

### One responsibility, kept local

Each module and class has a single responsibility, and its name says what that is. Code that changes together lives together.

- Name a module or class after the concept it owns (`order.ts`, `RateLimiter`, `parseRepoUrl`). A name that needs a vague suffix to hold it together (`*Helper`, `*Util`, `*Utils`, `*Manager`, `*Handler`, `*Processor`, `*Service` used as a catch-all) is a sign it has several jobs: split it by job and name each part for what it does. A small helper function belongs in the module that calls it; when two modules need it, give it its own module named for its job (`batch.ts`, `slug.ts`).
- A type or constant lives in the file that uses it. When several modules share one, export it from the module that owns the concept (`order.ts` exports `Order` beside the functions that work on orders), not from a grab-bag file. Write `types.ts`, `constants.ts`, `utils.ts` or `helpers.ts` only when the repo's conventions require them. Rationale: https://www.totaltypescript.com/where-to-put-your-types-in-application-code
- Infer types where the code already says them (`ReturnType`, `typeof`, `satisfies`) rather than writing a parallel interface that can drift.
- Organise folders by feature, not by kind.

### JSON or TypeScript

Use **JSON** for data that should change without touching logic:

- Per-environment configuration (endpoints, feature flags), one file per environment, selected at runtime.
- Static data: fixtures and mock data, localisation strings, lookup tables.
- Import it with `resolveJsonModule` (and `with { type: "json" }` under Node ESM) so TypeScript infers its type; validate at the boundary when the file is user-editable.

Use **TypeScript** when the values need logic, functions, computed values or comments. For configuration that needs documentation, use a typed `.ts` config (`export default { ... } satisfies Config`) or JSONC.

Secrets (API keys, tokens, passwords) come from environment variables, never from JSON or source.

## Finishing

- Run what the repo has: typecheck (`tsc --noEmit`), lint, tests. Say plainly what you could not run.
- Summarize: what changed, any library chosen or skipped and why, repo conventions that overrode these rules, and suggestions for wider violations you left alone.
