---
name: github-cicd
description:
  Create, change or review GitHub Actions workflow files to the user's own opinionated CI/CD pipeline -
  staging/main promotion by fast-forward, CI-gated releases, nightly release candidates, semantic-release
  through npm-publish-strict, OIDC instead of secrets, SHA-pinned actions, Dependabot. Use only when the task
  adds or modifies files under .github/workflows, .github/actions, .github/chainguard or
  .github/dependabot.yml, or reviews them, or the user says "github-cicd". Not for code that merely runs in CI
  (tests, build scripts), the code of a GitHub Action (use github-ts-action), a README (use create-readme), or
  other CI systems.
---

# github-cicd

This skill applies the user's CI/CD conventions to a repository's GitHub Actions. They are opinions: follow
them even where common advice differs. Exemplar: https://github.com/awalsh128/winston-host-adapters (branch
`staging` is the latest). Read the local clone at `~/repos/winston-host-adapters` if it exists, and check
`git -C ~/repos/winston-host-adapters log origin/staging..HEAD` for unpushed changes, otherwise
`gh api repos/awalsh128/winston-host-adapters/contents/<path>?ref=staging`. The templates in
`references/workflows.md` are distilled from it; when the exemplar has moved on, the exemplar wins.

## Precedence

1. The repo's documented conventions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`) win inside that repo;
   mention the conflict in the summary.
2. The rules in this skill.
3. For anything else, GitHub's own security hardening guidance for Actions.

## Modes

- **Scaffold**: no workflows yet. Create the set below.
- **Extend**: workflows exist. Add or change a job while keeping the rules. Do not restructure workflows the
  task did not touch; list wider violations as suggestions.
- **Review**: report pass/fail per rule with `file:line` and the concrete fix. Edit nothing until asked.

## Before writing

1. Read `.github/`, `package.json` (scripts, workspaces, `engines`), `CONTRIBUTING.md`, `release.config.*` and
   the lockfile. Match what exists before applying the defaults.
2. `git remote -v` and `git branch -a` for the real owner, repo and branches. Never hardcode them.
3. Classify the project, because it decides the publish workflow. Read `references/workflows.md` for the npm
   package and monorepo forms. For anything else (GitHub Action, VS Code extension, Python, Go, container
   image), build CI and the promotion flow from the templates and ask the user how it should publish, instead
   of guessing.
4. Resolve every action SHA and version at write time (`gh api repos/<owner>/<repo>/git/ref/tags/<tag>`,
   `npm view <pkg> version`). The numbers in the templates are placeholders, never copy them from memory.
5. Ask before assuming: the package list and release order, the baseline commit, whether the repo is allowed
   the staging/main split, and the Node version.

## The pipeline

| File                                 | Job                                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------------- |
| `ci.yml`                             | Build, typecheck, test, audit, pack. Runs on every push, PR, nightly and by hand.   |
| `pr.yml`                             | Base branch is `staging`, the title is a Conventional Commit, dependency review.    |
| `nightly.yml`                        | Starts a release candidate on `staging` when shippable files changed since release. |
| `promote.yml`                        | Fast-forwards `main` to a CI-passed `staging` commit, then starts the release.      |
| `publish.yml`                        | Releases with semantic-release via `awalsh128/npm-publish-strict`; deploys docs.    |
| `.github/actions/setup`              | Composite action: Node, cache, `npm ci`, optional `--ignore-scripts`.               |
| `.github/actions/require-ci-success` | Composite action: fails unless the commit's latest completed CI run succeeded.      |
| `.github/chainguard/*.sts.yaml`      | Octo STS trust policies that mint the `main` and tag tokens.                        |
| `.github/dependabot.yml`             | Weekly grouped updates to `staging` with a cooldown.                                |

## Branching model

- `staging` is the integration branch and the base of every pull request, Dependabot's included. Pull requests
  are squash-merged with the title as the commit subject.
- `main` never gets commits of its own: no merges, squashes or release commits. It only moves by `promote.yml`
  fast-forwarding it to a `staging` commit that CI passed, so it is always an ancestor of `staging`. Its
  ruleset lets only the Octo STS app update it.
- `staging` releases candidates (`1.2.0-rc.1`, npm dist-tag `rc`). `main` releases official versions.
- The `.husky/commit-msg` hook runs commitlint; the `pr.yml` title lint is the gate that counts, because the
  title becomes the commit.

## Hard rules

1. **No stored secrets.** Credentials are exchanged from the job's OIDC token: Octo STS for GitHub tokens that
   `GITHUB_TOKEN` can't get (tags, pushes to a protected `main`), npm trusted publishing with provenance for
   npm. If a design seems to need a secret, say so and ask.
2. **Pin every `uses:` to a full commit SHA** with a `# vX.Y.Z` comment, in workflows and composite actions
   alike. Dependabot keeps them current.
3. **Least privilege.** Top-level `permissions: {}` or `contents: read`; each job grants only what it uses,
   with a trailing comment saying why (`id-token: write # For OIDC: ...`). Set `timeout-minutes` on every job.
4. **Release is gated on CI for the exact commit.** `require-ci-success` runs before any promotion or manual
   release. Candidates and official releases both go through `publish.yml` started on its own
   (`gh workflow run`), never called from another workflow, because npm trusted publishing trusts that
   workflow file started directly.
5. **Privileged jobs run no dependency code.** Any job that can mint a publish or tag token installs with
   `--ignore-scripts` and checks out with `persist-credentials: false`.
6. **Untrusted input goes through `env`,** never interpolated into `run:`
   (`${{ github.event.pull_request.title }}`, branch names, commit messages).
7. **Serialize what mutates.** `concurrency` with `cancel-in-progress: false` on promote, nightly and release;
   never cancel a job that is tagging.
8. **Trust policies are exact.** Octo STS policies match the owner and repository IDs in the OIDC subject
   (`repo:<owner>@<id>/<repo>@<id>:.*`), the branch, and the exact workflow file. They are read from the
   default branch, so a change takes effect when promoted.
9. **Audits fail by risk.** Runtime dependencies fail the build at any severity; development dependencies
   report moderate-and-up in a deduplicated issue without failing; high and critical anywhere fail, because
   release tooling runs with credentials.
10. **Comment the why** in the workflow (a short block at the top says what the workflow does and what it
    trusts). Skip comments that restate the step name.

## Finishing

- Validate: `actionlint` if installed, otherwise a YAML parse of each file;
  `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for each pinned SHA. Say plainly what you could not run.
- Don't commit, push or enable anything unless asked. Never run a release, tag or promotion without
  confirmation; suggest `gh workflow run publish.yml --ref staging -f dry-run=true` to test a change.
- Setup the files cannot do (rulesets, the Octo STS app, the `release` environment, the npm trusted publisher,
  Pages source) goes in the summary as a checklist from `references/repo-setup.md`, not into the workflows.
- Summarize: files created or changed, assumptions (Node version, package order, baseline commit), anything
  unverified, and suggestions.
