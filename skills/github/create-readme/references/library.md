# Library or package README

Applies to repos published to a registry (npm, PyPI, crates.io...). Exemplar: https://github.com/awalsh128/ts-apt

Uses the standard layout in `SKILL.md`. Type-specific rules:

- **Badges:** CI for each branch that has a workflow (e.g. `main` and `staging`), license, release. Label each CI badge by its branch; see the same-label rule in `SKILL.md`.
- **Warnings:** `[!IMPORTANT]` for hard requirements like `sudo`.

## Middle sections

1. **Quick Start:** the install command plus the shortest working example. This comes first.
2. **Requirements:** a one-line runtime and platform requirement taken from the manifest, only if the manifest declares one.
3. **Usage / API:** the main calls, then a link to generated API docs if they exist.
4. **Testing:** the real test command. Omit this section if the repo has no tests; don't print a command that runs nothing.

## Registry quick reference

Take the runtime version from the manifest field, not from memory.

| Registry | Install | Runtime field | Badge snippet (suggest, don't insert) |
| --- | --- | --- | --- |
| npm | `npm install <name>` | `engines.node` | `https://img.shields.io/npm/v/<name>` |
| PyPI | `pip install <name>` | `requires-python` | `https://img.shields.io/pypi/v/<name>` |
| crates.io | `cargo add <name>` | `rust-version` | `https://img.shields.io/crates/v/<name>` |
| Go modules | `go get <module>` | `go` directive in `go.mod` | `https://img.shields.io/github/v/tag/<owner>/<repo>` |

## Is it published?

Check before writing an install command: `npm view <name>`, `pip index versions <name>`, `cargo search <name> --limit 1`, or `go list -m <module>@latest`. If it is not published or the check can't run, show a source install (clone, then the repo's own build command) and say in the summary that publication is unverified.

## Optional badges

Suggest these only if the repo qualifies; don't insert them:

- **Coverage:** `https://img.shields.io/codecov/c/github/<owner>/<repo>` (Codecov) or similar if the repo publishes coverage reports.
- **Docker images:** `https://img.shields.io/docker/v/<org>/<image>` (Docker Hub) or `ghcr.io/<owner>/<repo>` (GitHub Container Registry) if the repo publishes images.
- **GitHub Release (generic):** `https://img.shields.io/github/v/release/<owner>/<repo>` if the project uses GitHub Releases and doesn't publish to a language-specific registry.
