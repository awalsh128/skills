# GitHub Action README

Applies when the repo has an `action.yml`. Exemplar: https://github.com/awalsh128/cache-apt-pkgs-action

Uses the standard layout in `SKILL.md`. Type-specific rules:

- **Badges:** CI for each workflow that matters (test workflows may live in a sibling `-ci` repo, so check
  where they run), latest release. Label CI badges by workflow or branch when more than one; see the
  same-label rule in `SKILL.md`.
- **Warnings:** `[!IMPORTANT]` for real constraints such as required permissions.
- **Demos:** only when the Action has a visible effect (a PR comment, a job summary, an annotation): one
  screenshot of it, per `references/demos.md`. The `steps:` example stays text.

## Middle sections

1. Quick Start: a minimal `steps:` block using the real `uses: owner/repo@<latest tag>`
2. Requirements: runner OS, permissions
3. Configuration: an `### Inputs` and an `### Outputs` heading, each over its own table built from
   `action.yml` (name, description, required, default). The inputs table never sits under Quick Start without
   its heading; Audit reports that as a fail
4. Usage Guide: version selection, basic and advanced example
5. Caveats (⚠️)

## Notes

- Tables must match `action.yml` exactly: no invented inputs, none omitted.
- Pin the example to a tag the repo publishes (`git tag`, releases). With no tags yet, use the default branch
  and note that it should become a tag.
- If `runs.main` (or `runs.image`) points at a file the repo doesn't contain, such as an uncommitted `dist/`,
  say so in the summary; don't invent build steps.
- Composite and Docker actions: the `runs.using` value decides Requirements (runner OS, `docker`
  availability); don't claim a Node runtime for them.
- **Suggest, never apply: an all-outputs param.** When the action has two or more outputs and no such input,
  add one line to the summary suggesting an opt-in boolean input (for example `output-all`, default `false`)
  that, when `true`, uploads every output as one JSON file (for example `outputs.json`) in a workflow artifact
  (via `@actions/artifact`), instead of adding another output. The individual outputs stay set either way. It
  is a suggestion about `action.yml` and the action's code: do not add the input to the README tables or
  example, and do not change `action.yml`, unless the user asks.
- Drop Usage Guide and Caveats when there is nothing real to put in them.
