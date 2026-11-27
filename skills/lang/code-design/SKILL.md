---
name: code-design
description:
  Use when the task writes, changes, refactors or reviews code in any language, including adding a module or
  feature or choosing between a library and hand-written code. Applies the user's design conventions for
  readability, reuse, module layout and config data. Not for formatting (Prettier and linters own it), tests
  (use unit-tests) or CI files (use github-cicd).
---

# code-design

This skill applies the user's language-agnostic design conventions. They are opinions: follow them even where
common advice differs. A language skill (for example `typescript`) adds the specifics of its language on top.

Use `/mattpocock-skills:codebase-design` alongside it when the task is designing or deepening a module's
interface or deciding where a seam goes; this skill covers conventions, not interface design. For review mode
against a base commit or spec, use `/mattpocock-skills:code-review` and apply these rules as its standards.

## Precedence

1. The repo's own documented conventions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING`, lint and formatter config)
   win inside that repo. When one contradicts a rule below, follow the repo and mention the conflict in your
   summary.
2. The rules in this skill.
3. For anything neither covers, the language's official or most widely used style guide.

## Modes

- **Write**: new code. Apply every rule.
- **Modify**: existing code. Apply the rules to the code you add or touch, and match the file's surroundings
  otherwise. List wider violations as suggestions instead of restructuring files the task did not touch.
- **Review**: report each finding with `file:line`, the rule, and the concrete fix. Edit nothing until asked.

## Before writing

Read the neighbouring files, the manifest (what is already a dependency) and the lint config. The environment
answers "what is available"; these rules answer "what to prefer".

## Rules

### Readable over terse

Write the version a newcomer understands on first read, even when it is longer.

- Parse structured strings with the format's own parser: a URL type, a path library, a date or number
  formatting library. A regex is the right tool only for a genuinely pattern-shaped string, kept short and
  named.
- Name intermediate values instead of chaining long one-liners. Prefer `if` blocks to nested ternaries. Prefer
  plain loops or a single map or filter to a clever fold.
- **Flat control flow.** Open with guard clauses: handle the skipped or failing case first and leave (`return`
  or `raise` in a function, `continue` in a loop), then write the main path after it, outside any `else`. A
  function nests at most two blocks (`if`, loop, `try`); past that, move the loop body into a function named
  for what it does to one item.
- **Named shapes.** Data with fixed fields gets a named type (data class, record, interface, struct): several
  values returned together, table rows of three or more fields, and keyed data passed between functions. Keep
  dictionaries and maps for lookup, where the keys are data. The language's own idiom stays, such as Go's
  `(value, error)`.
- **Parse, don't validate.** Turn each external record (from a file, request or environment) into a named type
  where it is read, collecting problems as you build it, and run every later check on that type. This includes
  code whose job is validation. That type is the one statement of the input's shape, so declaring it is not
  duplication.
- Comment the non-obvious why, not the what.

### Reuse before writing

Decide in this order and stop at the first that fits:

1. **The platform**: the language's standard library and runtime APIs.
2. **A dependency already in the manifest.**
3. **A new library**, when it is well maintained and light for what it buys: few transitive dependencies,
   small next to the code it replaces. Check with the package manager's metadata command, not from memory.
   Weight matters most for bundled or shipped output.
4. **Write it yourself** when it is simple: a few lines, no tricky edge cases, cheaper to read than a
   dependency is to audit.

Domains full of edge cases always go to a library or the platform, never a hand-rolled version: dates and time
zones, CSV, YAML, semver, globs, shell quoting, crypto, HTML escaping.

### One responsibility, kept local

Each module and class has a single responsibility, and its name says what that is. Code that changes together
lives together.

- Name a module or class after the concept it owns (`order`, `RateLimiter`, `parseRepoUrl`). A name that needs
  a vague suffix to hold it together (`*Helper`, `*Util`, `*Utils`, `*Manager`, `*Handler`, `*Processor`,
  `*Service` used as a catch-all) is a sign it has several jobs: split it by job and name each part for what
  it does.
- Find a home before making a file. For a function or type, take the first that fits:
  1. The module of its only caller, when it is small and nothing else needs it.
  2. The existing module that already owns its concept (a level helper in `levels`, a text helper in
     `format`).
  3. A new module named for its job (`batch`, `slug`), only when two or more modules need it and no existing
     module owns the concept.
- Don't make a module for one small function (under about 30 lines) when step 1 or 2 fits. Many one-function
  files are as hard to navigate as one grab-bag file; match the granularity of the neighbouring modules.
- **Shared core module**: when functionality is used across many modules and doesn't belong to any one
  concept, it may be combined into a single `core` or `common` module (not `utils` or `helpers`). Check for an
  existing pattern first: if the repo already has one (or equivalent), use that name and put the code there.
  If there is none, ask the user which they prefer (`core`, `common`, or neither) before creating one, and
  recommend `core`. Only functionality with real fan-out qualifies; keep one-caller code local per the steps
  above, and keep the file cohesive rather than a dumping ground.
- A vague filename alone doesn't force a split. If the file's contents are cohesive, renaming it to the
  concept is enough; split only when it holds unrelated jobs.
- In Review mode, when a finding would create a new file, offer the choice (fold into an existing module, or
  create one) instead of fixing one target, and say which you recommend.
- A type or constant lives in the file that uses it. When several modules share one, export it from the module
  that owns the concept (`order` exports `Order` beside the functions that work on orders), not from a
  grab-bag file. Write `types`, `constants`, `utils` or `helpers` files only when the repo's conventions
  require them. Rationale: https://www.totaltypescript.com/where-to-put-your-types-in-application-code
- Derive a type from the code that already states it, where the language allows, rather than writing a
  parallel declaration that can drift.
- Organise folders by feature, not by kind.

### Data files or code

Use a **data file** (JSON, YAML, TOML) for data that should change without touching logic:

- Per-environment configuration (endpoints, feature flags), one file per environment, selected at runtime.
- Static data: fixtures and mock data, localisation strings, lookup tables.
- Load it by the parse, don't validate rule above.

Use **code** when the values need logic, functions, computed values or comments. For configuration that needs
documentation, use a typed code config or a format that allows comments.

Secrets (API keys, tokens, passwords) come from environment variables, never from data files or source.

## Finishing

Done when every file you wrote or touched is checked against the rules above, and the repo's build, lint and
tests have run (or the summary says which could not).

- Say plainly what you could not run.
- Summarize: what changed, any library chosen or skipped and why, repo conventions that overrode these rules,
  and suggestions for wider violations you left alone.
