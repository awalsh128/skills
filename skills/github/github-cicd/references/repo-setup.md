# Repository setup the workflows depend on

The workflows can't create these. Give the user this as a checklist in the summary, trimmed to what the
generated files use.

## Branches and rulesets

- Create `staging` from `main`. Make `staging` the base for pull requests (the default branch stays `main`,
  because Octo STS reads trust policies and schedules run from it).
- `main` ruleset: restrict updates and deletion, require linear history, and add the Octo STS app as a bypass
  actor, so only `promote.yml` can move it.
- `staging` ruleset: require pull requests and the CI and PR checks; allow squash merge only, with the pull
  request title as the commit subject. Apply it once `pr.yml` is on `staging`: a required check that has never
  reported blocks every pull request, including the one that adds it.
- Tag ruleset: restrict tag creation, with the Octo STS app as a bypass actor (`GITHUB_TOKEN` can't create
  tags under it).

## Octo STS

1. Install the app: https://github.com/apps/octo-sts/installations/new on the repository. A user token cannot
   list installations (GitHub answers 403), so ask the user to confirm the install instead of detecting it.
2. Commit `.github/chainguard/release.sts.yaml` and `promote.sts.yaml` to `main`; policy changes take effect
   only once promoted.
3. Promote by hand with `gh workflow run promote.yml --ref staging`. Without `--ref staging` the run is on
   `main` and the trust policy rejects it. Put this command in the repo's `CONTRIBUTING.md`.

## Repositories created from a template

- Octo STS policies name the owner and repository IDs (`repo:<owner>@<id>/<repo>@<id>`) and the workflow path.
  A copy keeps the template's, so every run is rejected: rewrite both from
  `gh api repos/<owner>/<repo> --jq '"\(.owner.id) \(.id)"'` before the first promotion.
- Create `staging`, the rulesets and the squash-only merge settings from the files in the repo, and keep the
  release job held (see rule 11) until the app is installed and the policies are on `main`.
- The first run that names the `release` environment creates it; restrict its branches afterwards.

## Environments

- `release`: restrict deployment branches to `main` and `staging`. npm trusted publishing names this
  environment.
- `github-pages` (only with a docs site): restrict to `main`, and set Pages to deploy from GitHub Actions.
  Both `publish.yml` and `docs.yml` deploy through it.

## npm

- The first version of each package is published by hand so it exists on npm; then add a trusted publisher in
  the package's npmjs.com settings: this repository, workflow `publish.yml`, environment `release`. Until then
  the release fails on that package.
- A package renamed or added later needs the same two steps.

## Repository settings

- Actions: allow only actions pinned to a full SHA ("Require actions to be pinned to a commit SHA", where
  available), default workflow permissions read-only.
- Enable Dependabot alerts and security updates, and the dependency graph (required by `dependency-review`).
- Public repositories: enable secret scanning and push protection, turn on private vulnerability reporting
  (`gh api -X PUT repos/<owner>/<repo>/private-vulnerability-reporting`) and commit a `SECURITY.md` that links
  to it. Require actions pinned to a SHA via
  `gh api -X PUT repos/<owner>/<repo>/actions/permissions -F enabled=true -f allowed_actions=all -F sha_pinning_required=true`,
  only after every workflow is pinned.
- Immutable releases (`gh api -X PUT repos/<owner>/<repo>/immutable-releases`) once the first tags are final:
  they block deleting or re-creating a published tag, so turn them on after any re-release.
- Labels `vulnerability` and `test` for the audit issues.

## Rulesets and tags after setup

- Merging a changed `.github/rulesets/*.json` applies nothing. Apply it with
  `gh api -X PUT repos/<owner>/<repo>/rulesets/<id> --input <file>`, then compare the live ruleset with the
  file. Server defaults on the live copy (`required_reviewers: []` and the like) are not drift.
- The tag ruleset blocks deleting tags. To re-release a version, turn the ruleset off, delete the release and
  tag, and turn it back on in a trap, so a failed step still restores it.
- The first release has no tag to start from, so semantic-release reads all history. Set the release's
  baseline commit (commits before it are ignored by versioning and notes) so old history can't leak into the
  first release notes, and remove it once that release is tagged.
