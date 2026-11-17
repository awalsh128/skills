# CI, release and agent rules

## Setup composite action (`.github/actions/setup/action.yml`)

Used by every job so setup lives in one place. Steps: `actions/setup-node` (Node from `.node_ver`, `cache: npm`), `npm ci`, try to download a build artifact named `build-dist-<sha>` (`dawidd6/action-download-artifact`, `if_no_artifact_found: ignore`), then `npm run build` and upload `dist` (`retention-days: 1`, `overwrite: true`) only when `steps.<id>.outputs.found_artifact != 'true'`. With `ignore` the download step always succeeds, so test `found_artifact`, not the step outcome. All steps with `run:` set `shell: bash`.

## ci.yml jobs

Triggers: `push`, `pull_request` (opened, synchronize, reopened, ready_for_review), nightly `schedule`, `workflow_dispatch` with a `debug` boolean. Top-level `permissions` minimal; each job narrows further.

1. `setup-and-cache`: checkout, setup (build), upload the bundle (`action.yml`, `dist/action/`, plus any runtime scripts) as `action-bundle-<sha>` with `if-no-files-found: error`, `retention-days: 1`.
2. `codeql` (needs 1): `github/codeql-action` init (`javascript-typescript`), setup, analyze. Skip on fork PRs, which can't upload security events. Needs `security-events: write`.
3. `linters` (needs 1): `npm run lint`, `npm run typecheck`.
4. `action-deps-pinned` (needs 1): a script that fails on any unpinned or outdated `uses:` and on locally linked or ranged sibling dependencies. Pass `GITHUB_TOKEN` to avoid shared-IP rate limits.
5. `testing` (needs 1): `npm run test`, `npx type-coverage --at-least 95`, Codecov upload (OIDC, `fail_ci_if_error`), then `npm audit --audit-level=high --omit=dev` with `if: always()` so earlier failures still surface.
6. Integration jobs (need `testing`): download the bundle artifact to `.`, run the action with `uses: ./`, give each run a unique input (e.g. `version: ${{ github.run_id }}-${{ github.run_attempt }}-<job>`), then assert on `steps.<id>.outputs.*` in a Verify step. Cover cache miss and hit, each input, and each failure mode.

Checkout with `ref: ${{ github.event.pull_request.head.ref || github.ref_name }}`.

## Release

`release.config.ts` (semantic-release), branches in order least to most stable: `{ name: "staging", channel: "next", prerelease: "rc" }`, `"main"`. Plugins: commit-analyzer, release-notes-generator, changelog (`CHANGELOG.md`), npm (`npmPublish` only if the package is meant for npm; otherwise `false`), git (commit `CHANGELOG.md`, `package.json`, `package-lock.json` with `chore(release): ${nextRelease.version} [skip ci]`), github. Commits follow Conventional Commits.

Because `dist/` is gitignored, the release workflow must build the bundle and make it part of the tagged release so `uses: owner/repo@vX` finds `dist/action/index.js`. The exemplar's `main-2` branch has no release workflow yet, so confirm how the user wants the bundle shipped (commit to a release branch, or force-add `dist/` in the release commit) before writing it.

Release publishing is irreversible: confirm before running or enabling it.

## PR policy

A `pr.yml` workflow plus `scripts/ops/pr_checks.mts` enforces branch policy (feature branches target `staging`, `staging` targets `main`) and workflow pinning. `scripts/ops/check_latest_action_pin.mts` checks every `uses:` is a full SHA at the latest release. A husky `.husky/pre-push` hook runs the dependency-pin check; never bypass with `--no-verify`.

## AGENTS.md

Keep it short, one rule per line, MUST/NEVER/ASK FIRST for high-priority rules, scoped sections: Always Apply, Code Changes, Tests, CI/CD and Release, Repo Paths and Commands, plus a section per sibling-library boundary. End with a Quick Commands block:

```bash
npx eslint src test scripts --ext .ts,.mts
npx tsc -p tsconfig.json --noEmit
npx vitest run
```

Core always-apply rules: be accurate not agreeable; minimal reversible changes; no public API change unless asked; confirm irreversible actions (force-push, history rewrite, release publishing); never claim success unverified; stop after two failed repair attempts and report the root cause; least privilege and explicit failure; actions pinned to full SHAs.
