# Library or package README

Applies to repos published to a registry (npm, PyPI, crates.io...). Exemplar:
https://github.com/awalsh128/ts-apt

Uses the standard layout in `SKILL.md`. Type-specific rules:

- **Badges:** CI for each branch that has a workflow (e.g. `main` and `staging`), release. Label each CI badge
  by its branch; see the same-label rule in `SKILL.md`. Also add the registry version badge once the package
  is published (see "Is it published?") and the coverage badge when a workflow uploads coverage (see "Coverage
  and registry badges").
- **Warnings:** `[!IMPORTANT]` for hard requirements like `sudo`.
- **Demos:** a CLI (a terminal recording of a real command) or a library with visual output (the input and the
  image it produces) gets a hero demo; a plain code library gets none. See `references/demos.md`, including
  the packaged-README rules for registry pages.

## Middle sections

1. **Quick Start:** the install command plus the shortest working example. This comes first.
2. **Requirements:** a one-line runtime and platform requirement taken from the manifest, only if the manifest
   declares one.
3. **Usage / API:** the main calls, then a link to generated API docs if they exist.
4. **Testing:** the real test command. Omit this section if the repo has no tests; don't print a command that
   runs nothing.
5. **Credits:** optional and last. Allowed when it credits real third-party code the library wraps or depends
   on in a way users should know about. Each entry links the project and says what it provides.

## Registry quick reference

Take the runtime version from the manifest field, not from memory.

| Registry   | Install              | Runtime field              | Version badge snippet (insert once published)        |
| ---------- | -------------------- | -------------------------- | ---------------------------------------------------- |
| npm        | `npm install <name>` | `engines.node`             | `https://img.shields.io/npm/v/<name>`                |
| PyPI       | `pip install <name>` | `requires-python`          | `https://img.shields.io/pypi/v/<name>`               |
| crates.io  | `cargo add <name>`   | `rust-version`             | `https://img.shields.io/crates/v/<name>`             |
| Go modules | `go get <module>`    | `go` directive in `go.mod` | `https://img.shields.io/github/v/tag/<owner>/<repo>` |

## Is it published?

Check before writing an install command: `npm view <name>`, `pip index versions <name>`,
`cargo search <name> --limit 1`, or `go list -m <module>@latest`. If it is not published or the check can't
run, show a source install (clone, then the repo's own build command) and say in the summary that publication
is unverified.

## Coverage and registry badges

Insert these when they apply, and suggest them in the summary when they don't yet:

- **Registry version:** the snippet in the table above, once `Is it published?` confirms the package exists.
  Link it to the registry page.
- **Coverage (Codecov):** applies only when a workflow runs `codecov/codecov-action`. A `.codecov.yml` alone
  (the powerpack `node` set ships one) is not enough, since nothing uploads. Verify with
  `curl -s https://codecov.io/api/v2/github/<owner>/repos/<repo>`: if it returns the repo with
  `"active":true`, use its `branch` value in
  `https://codecov.io/gh/<owner>/<repo>/branch/<branch>/graph/badge.svg`, linked to
  `https://codecov.io/gh/<owner>/<repo>`. If the repo isn't found, insert the badge anyway only when the
  workflow uploads, and say in the summary that Codecov isn't authorized or has no upload yet (the badge shows
  "unknown" until then). A repo with a staging/main split has one branch on Codecov; use the one the API
  reports. If the API call itself fails (error or timeout, not a not-found), keep the existing badge or use
  the default branch from `gh repo view --json defaultBranchRef`, and say in the summary that the Codecov
  branch is unverified. Never skip the check silently.

## Optional badges

Suggest these only if the repo qualifies; don't insert them:

- **Coverage (other services):** `https://img.shields.io/codecov/c/github/<owner>/<repo>` or similar if the
  repo publishes coverage reports somewhere other than Codecov.
- **Docker images:** `https://img.shields.io/docker/v/<org>/<image>` (Docker Hub) or `ghcr.io/<owner>/<repo>`
  (GitHub Container Registry) if the repo publishes images.
- **GitHub Release (generic):** `https://img.shields.io/github/v/release/<owner>/<repo>` if the project uses
  GitHub Releases and doesn't publish to a language-specific registry.
