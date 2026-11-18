# Repository setup the workflows depend on

The workflows can't create these. Give the user this as a checklist in the summary, trimmed to what the
generated files use.

## Branches and rulesets

- Create `staging` from `main`. Make `staging` the base for pull requests (the default branch stays `main`,
  because Octo STS reads trust policies and schedules run from it).
- `main` ruleset: restrict updates and deletion, require linear history, and add the Octo STS app as a bypass
  actor, so only `promote.yml` can move it.
- `staging` ruleset: require pull requests and the CI and PR checks; allow squash merge only, with the pull
  request title as the commit subject.
- Tag ruleset: restrict tag creation, with the Octo STS app as a bypass actor (`GITHUB_TOKEN` can't create
  tags under it).

## Octo STS

1. Install the app: https://github.com/apps/octo-sts/installations/new on the repository.
2. Commit `.github/chainguard/release.sts.yaml` and `promote.sts.yaml` to `main`; policy changes take effect
   only once promoted.

## Environments

- `release`: restrict deployment branches to `main` and `staging`. npm trusted publishing names this
  environment.
- `github-pages` (only with a docs site): restrict to `main`, and set Pages to deploy from GitHub Actions.

## npm

- The first version of each package is published by hand so it exists on npm; then add a trusted publisher in
  the package's npmjs.com settings: this repository, workflow `publish.yml`, environment `release`. Until then
  the release fails on that package.
- A package renamed or added later needs the same two steps.

## Repository settings

- Actions: allow only actions pinned to a full SHA ("Require actions to be pinned to a commit SHA", where
  available), default workflow permissions read-only.
- Enable Dependabot alerts and security updates, and the dependency graph (required by `dependency-review`).
- Labels `vulnerability` and `test` for the audit issues.
