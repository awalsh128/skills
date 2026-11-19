# Workflow templates

Distilled from https://github.com/awalsh128/winston-host-adapters (branch `staging`). Placeholders in
`<angle brackets>`. `<sha>` means resolve the full commit SHA of the latest release tag at write time and keep
the `# vX.Y.Z` comment. Adjust job names, build commands and the package list to the repo.

## Composite action: setup (`.github/actions/setup/action.yml`)

```yaml
name: "Setup environment"
description: "Sets up Node.js and installs dependencies"

inputs:
  ignore-scripts:
    description: >-
      Skip install scripts, both dependencies' and the root prepare script (husky). For privileged jobs, so
      dependency code can't run with their credentials at install.
    required: false
    default: "false"

runs:
  using: "composite"
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@<sha> # vX
      with:
        node-version: "<major>"
        cache: "npm"
        registry-url: "https://registry.npmjs.org"

    - name: Install dependencies
      shell: bash
      env:
        IGNORE_SCRIPTS: ${{ inputs.ignore-scripts }}
      run: |
        set -euo pipefail
        if [[ "$IGNORE_SCRIPTS" == "true" ]]; then
          npm ci --ignore-scripts
        else
          npm ci
        fi
```

## Composite action: require-ci-success (`.github/actions/require-ci-success/action.yml`)

```yaml
name: "Require CI success"
description: "Fails unless the latest completed CI workflow run for a commit concluded successfully."

inputs:
  sha:
    description: "Full commit SHA that must have passed CI."
    required: true
  token:
    description: "Token with actions: read permission."
    required: true

runs:
  using: "composite"
  steps:
    - name: Check CI conclusion
      shell: bash
      env:
        GH_TOKEN: ${{ inputs.token }}
        SHA: ${{ inputs.sha }}
      run: |
        set -euo pipefail
        # Only completed runs count: promoting main starts a CI run for the same commit, which is
        # still in progress when the release checks CI.
        conclusion="$(gh run list --repo "$GITHUB_REPOSITORY" --workflow ci.yml --commit "$SHA" \
          --status completed --limit 1 --json conclusion --jq '.[0].conclusion // ""')"
        if [[ "$conclusion" != "success" ]]; then
          echo "::error::CI for commit $SHA is '${conclusion:-missing}', not 'success'."
          exit 1
        fi
        echo "CI passed for commit $SHA."
```

## ci.yml

Triggers: `staging` gives nightly and promote a result for staging's exact commit; `main` reports each
promotion's status. The workflow must be named `ci.yml`, because `require-ci-success` looks it up by file
name. The `main` trigger is optional: promote only fast-forwards `main` to a commit whose CI already passed on
`staging`, and `require-ci-success` reads that run, so a `main` run repeats it. Drop it where nothing needs a
status on `main`, and then drop any "skipped on main" handling from the gate job.

```yaml
name: CI

on:
  push:
    branches: [main, staging]
  pull_request:
  schedule:
    - cron: "0 18 * * *"
  workflow_dispatch:

# Supersede running PR checks; any other run gets its own group, so none is cancelled or dropped.
concurrency:
  group: ci-${{ github.event_name == 'pull_request' && github.ref || github.run_id }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    permissions:
      contents: read
      issues: write # Audit findings are reported as issues
      pull-requests: write # and as PR comments

    steps:
      - name: Checkout code
        uses: actions/checkout@<sha> # vX

      - name: Setup
        uses: ./.github/actions/setup

      # Runtime dependencies ship to users, so any advisory fails the build.
      - name: Audit runtime dependencies
        uses: oke-py/npm-audit-action@<sha> # vX
        with:
          production_flag: true
          audit_level: low
          github_token: ${{ secrets.GITHUB_TOKEN }}
          create_pr_comments: true
          create_issues: true
          issue_title: npm audit found vulnerabilities in runtime dependencies
          issue_labels: vulnerability,test
          dedupe_issues: true

      # Development tools never ship, so moderate advisories are reported without failing.
      - name: Report development dependency advisories
        uses: oke-py/npm-audit-action@<sha> # vX
        with:
          audit_level: moderate
          fail_on_vulnerabilities: false
          github_token: ${{ secrets.GITHUB_TOKEN }}
          create_pr_comments: true
          create_issues: true
          issue_labels: vulnerability,test
          dedupe_issues: true

      # Some tools run with publishing credentials, so high and critical advisories still fail.
      - name: Audit all dependencies for high severity
        uses: oke-py/npm-audit-action@<sha> # vX
        with:
          audit_level: high
          github_token: ${{ secrets.GITHUB_TOKEN }}
          create_pr_comments: false
          create_issues: false

      - name: Build
        run: npm run build

      - name: Typecheck
        run: npm run typecheck

      - name: Unit tests
        run: npm test

      # Catches packaging regressions, such as missing dist files, before a release.
      - name: Pack
        run: npm pack --dry-run # add --workspaces for a monorepo
```

Add `lint`, `npm run docs:api` and coverage steps when the repo has those scripts. `secrets.GITHUB_TOKEN` is
the built-in token, not a stored secret.

## pr.yml

```yaml
name: Pull Request

on:
  pull_request:
    types: [opened, synchronize, reopened, edited]

permissions:
  contents: read

jobs:
  check-branch:
    name: Check branch
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      # main is only updated by promote.yml, which fast-forwards it to staging; a merge into main
      # would add a commit that staging doesn't have.
      - name: Require staging as the base branch
        env:
          BASE_REF: ${{ github.base_ref }}
        run: |
          if [ "$BASE_REF" != "staging" ]; then
            echo "::error::Pull requests target staging, not $BASE_REF; main is updated by promotion."
            exit 1
          fi

  commitlint:
    name: Lint pull request title
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - name: Checkout code
        uses: actions/checkout@<sha> # vX

      - name: Setup
        uses: ./.github/actions/setup

      # Pull requests are squash-merged with the title as the commit subject, and semantic-release
      # versions the package from it, so only the title has to be a Conventional Commit. The
      # edited trigger reruns this check when the title changes.
      - name: Lint pull request title
        env:
          TITLE: ${{ github.event.pull_request.title }}
        run: printf '%s\n' "$TITLE" | npx commitlint --verbose

  dependency-review:
    name: Dependency review
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - name: Checkout code
        uses: actions/checkout@<sha> # vX

      - name: Dependency Review
        uses: actions/dependency-review-action@<sha> # vX
```

Needs `@commitlint/cli` and `@commitlint/config-conventional` as dev dependencies,
`"commitlint": { "extends": ["@commitlint/config-conventional"] }` in `package.json`, and a husky `commit-msg`
hook running `npx --no -- commitlint --edit "$1"`.

## nightly.yml

Schedules only run on the default branch, so this runs on `main` and starts `publish.yml` on `staging`.

```yaml
# Starts a nightly release candidate when staging has shippable changes since its last release.
# Candidates are published under the `rc` dist-tag, so they run publish.yml on its own: npm trusted
# publishing trusts that workflow file started directly, not through another workflow.
name: Nightly release candidate

on:
  schedule:
    - cron: "0 8 * * *"
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: nightly
  cancel-in-progress: false

jobs:
  nightly:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read
      actions: write # Start the publish workflow
    steps:
      - name: Checkout staging
        uses: actions/checkout@<sha> # vX
        with:
          ref: staging
          fetch-depth: 0
          persist-credentials: false

      # Shippable files are what the package publishes: sources and manifests, not docs, tests or
      # workflows. publish.yml still releases nothing when no commit calls for a version.
      - name: Look for shippable changes since the last release
        id: changes
        shell: bash
        run: |
          set -euo pipefail
          last="$(git describe --tags --abbrev=0 --match "<tag-pattern, e.g. v*>" HEAD 2>/dev/null || true)"
          if [[ -z "$last" ]]; then
            echo "No release yet, so everything is new."
            echo "changed=true" >> "$GITHUB_OUTPUT"
            exit 0
          fi
          files="$(git diff --name-only "$last" HEAD -- src package.json package-lock.json tsconfig.json)"
          if [[ -z "$files" ]]; then
            echo "No shippable changes since $last."
            echo "changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "Shippable changes since $last:"
            echo "$files"
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi

      - name: Start release candidate
        if: ${{ steps.changes.outputs.changed == 'true' }}
        env:
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: gh workflow run publish.yml --ref staging
```

For a monorepo, loop over `"<package directory>:<tag pattern>"` entries and compare each package with its own
last tag, excluding its `test` directory and README; the shared lockfile and base tsconfig count for every
package.

## promote.yml

```yaml
# Promotes staging to main by fast-forwarding main to staging's latest commit, then starts the
# official release. main never gets commits of its own, so it is always an ancestor of staging.
name: Promote staging to main

on:
  workflow_dispatch:
    inputs:
      confirm-major:
        description: "Required for a major release: the version being released (e.g. 2.0.0)"
        type: string
        required: false
        default: ""

permissions:
  contents: read

concurrency:
  group: promote
  cancel-in-progress: false

jobs:
  promote:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    permissions:
      contents: read
      actions: write # Read CI runs and start the release workflow
      id-token: write # For OIDC: the Octo STS token that updates main
    steps:
      # main's ruleset only lets the Octo STS app update it, so main is pushed with its token,
      # issued under .github/chainguard/promote.sts.yaml to this workflow on staging only.
      - name: Create main token
        id: octo-sts
        uses: octo-sts/action@<sha> # vX
        with:
          scope: ${{ github.repository }}
          identity: promote

      - name: Checkout repository
        uses: actions/checkout@<sha> # vX
        with:
          ref: staging
          fetch-depth: 0
          token: ${{ steps.octo-sts.outputs.token }}

      - name: Resolve staging commit
        id: staging
        shell: bash
        run: echo "sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"

      - name: Require CI success on staging
        uses: ./.github/actions/require-ci-success
        with:
          sha: ${{ steps.staging.outputs.sha }}
          token: ${{ github.token }}

      # A major release strands users of the previous major (there is no maintenance branch), so it
      # needs its version typed in. The first official release counts as a major. Assumes `v${version}` tags.
      - name: Confirm a major release
        env:
          STAGING_SHA: ${{ steps.staging.outputs.sha }}
          CONFIRM: ${{ inputs.confirm-major }}
        shell: bash
        run: |
          set -euo pipefail
          official="$(git tag --merged origin/main --list 'v[0-9]*' | grep -v -- '-' | sort -V | tail -n1 || true)"
          candidate="$(git tag --merged "$STAGING_SHA" --list 'v[0-9]*-rc.*' | sort -V | tail -n1 || true)"
          if [[ -z "$candidate" ]]; then
            echo "Nothing new to release: staging has no candidate. main still fast-forwards."
            exit 0
          fi
          next="${candidate#v}"
          next="${next%%-*}"
          if [[ -n "$official" && "$(printf '%s\n%s\n' "${official#v}" "$next" | sort -V | tail -n1)" == "${official#v}" ]]; then
            echo "Nothing new to release: $official is already out. main still fast-forwards."
            exit 0
          fi
          echo "Promotion releases $next."
          if [[ -z "$official" || "${next%%.*}" -gt "$(cut -d. -f1 <<<"${official#v}")" ]]; then
            [[ "$CONFIRM" == "$next" ]] || {
              echo "::error::$next is a major release. Run Promote again with confirm-major set to $next."
              exit 1
            }
          fi

      - name: Fast-forward main to staging
        env:
          STAGING_SHA: ${{ steps.staging.outputs.sha }}
        shell: bash
        run: |
          set -euo pipefail
          if ! git merge-base --is-ancestor origin/main "$STAGING_SHA"; then
            echo "::error::main has commits that are not on staging, so it can't be fast-forwarded."
            echo "Get those commits onto staging through a pull request, then promote again."
            exit 1
          fi
          # Not a force push, so the remote rejects anything but a fast-forward.
          git push origin "$STAGING_SHA:refs/heads/main"

      # Starting the release on main makes semantic-release cut an official release, not a candidate.
      - name: Start official release
        env:
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: gh workflow run publish.yml --ref main
```

## publish.yml (single npm package)

```yaml
# Releases the package, always gated by CI:
# - staging: nightly.yml starts this when staging has shippable changes, releasing a candidate
#   (e.g. v1.2.0-rc.1) to npm under the `rc` dist-tag.
# - main: promote.yml starts this after fast-forwarding main, releasing an official version.
# No secrets: the job's OIDC token is exchanged for each credential. Tags are pushed with an Octo
# STS token; npm trusted publishing is bound to this workflow file and the 'release' environment.
name: Publish

on:
  workflow_dispatch:
    inputs:
      dry-run:
        description: "Run the release process without publishing anything or pushing tags"
        type: boolean
        required: false
        default: false

permissions: {}

jobs:
  release:
    # Off switch for every route to a release (see rule 11). A dry run publishes nothing, so it is always allowed.
    if: ${{ vars.RELEASES_ENABLED != 'false' || inputs.dry-run }}
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    environment: release
    # One release per branch at a time; never cancel one that is tagging.
    concurrency:
      group: release-${{ github.ref }}
      cancel-in-progress: false
    permissions:
      actions: read # For checking CI results
      contents: write # For GitHub releases
      id-token: write # For OIDC: the Octo STS tag token and npm trusted publishing with provenance
      issues: write # For semantic-release comments
      pull-requests: write # For semantic-release comments
    steps:
      - name: Checkout repository
        uses: actions/checkout@<sha> # vX
        with:
          fetch-depth: 0 # semantic-release reads every commit and tag since the last release
          persist-credentials: false

      - name: Require CI success
        uses: ./.github/actions/require-ci-success
        with:
          sha: ${{ github.sha }}
          token: ${{ github.token }}

      # This job can mint npm publish and GitHub tokens, so dependencies' install scripts don't run.
      - name: Setup
        uses: ./.github/actions/setup
        with:
          ignore-scripts: true

      - name: Create tag token
        id: octo-sts
        uses: octo-sts/action@<sha> # vX
        with:
          scope: ${{ github.repository }}
          identity: release

      - name: Build
        run: npm run build

      - name: Release
        uses: awalsh128/npm-publish-strict@<sha> # vX
        with:
          dry-run: ${{ inputs.dry-run || 'false' }}
          baseline-commit: <last commit without a Conventional Commit message, or omit>
          git-credentials: x-access-token:${{ steps.octo-sts.outputs.token }}
          github-token: ${{ github.token }}
```

Read the pinned version's `action.yml` (`gh api repos/awalsh128/npm-publish-strict/contents/action.yml`) for
current inputs and outputs rather than trusting this list. Run `mode: check` (or a dry run) after any change
to confirm the preconditions without releasing.

### Monorepo form

One `Release <package>` step per package, in dependency order, so a package never publishes before what it
depends on and a failure stops the rest. Per step: `working-directory`, `tag-format` (`<package>-v${version}`;
omit to keep plain `v*` tags for a package continuing older tags), `commit-paths` (the package directory), and
`pin-dependencies` (`"<dependency name>=<dependency tag format>"`) for internal dependencies. Between steps,
`git checkout -- .` restores the manifests semantic-release rewrote, so the next package installs from the
committed tree. Set `workspaces-update=false` in `.npmrc`, because `npm version` otherwise re-resolves the
workspace and fails on placeholder internal versions. Packages keep the placeholder version `0.0.0` in git.

### Docs site (optional)

Only official releases (`github.ref == 'refs/heads/main'`) rebuild the docs. In the release job: a step
computing `any=true` when a `version` output is set, then `npm run docs:api`, `actions/configure-pages` (needs
`pages: read`) and `actions/upload-pages-artifact`. A separate `deploy-pages` job (`needs: release`, `if:` on
main and the output) runs `actions/deploy-pages` with `pages: write`, `id-token: write` and the `github-pages`
environment, which only allows `main`; the release job can't use it because it also runs on `staging`.

## Octo STS trust policies (`.github/chainguard/`)

Get the IDs with `gh api repos/<owner>/<repo> --jq '"\(.owner.id) \(.id)"'`. The subject is
`repo:<owner>@<owner-id>/<repo>@<repo-id>:.*`, so a repository that later takes the same name doesn't match.
Policies are read from the default branch.

`release.sts.yaml` (tags, used by `publish.yml` on `main` and `staging`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/octo-sts/app/refs/heads/main/pkg/octosts/octosts.TrustPolicy.json
issuer: https://token.actions.githubusercontent.com
subject_pattern: "repo:<owner>@<owner-id>/<repo>@<repo-id>:.*"
claim_pattern:
  ref: "refs/heads/(main|staging)"
  job_workflow_ref: "<owner>/<repo>/\\.github/workflows/publish\\.yml@refs/heads/(main|staging)"

permissions:
  contents: write
```

`promote.sts.yaml` (fast-forwards `main`, used by `promote.yml` on `staging` only): the same, with
`ref: "refs/heads/staging"` and `job_workflow_ref` set to `promote\\.yml@refs/heads/staging`.

## dependabot.yml

Pull requests target `staging`. Titles use the `build` type, which doesn't trigger a release; retitle one as
`fix:` when a runtime dependency update should ship. The cooldown skips releases younger than a week, giving a
compromised release time to be caught.

```yaml
version: 2

updates:
  - package-ecosystem: github-actions
    directories:
      - "/"
      - "/.github/actions/*"
    target-branch: staging
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
    commit-message:
      prefix: build
      include: scope
    groups:
      actions:
        patterns: ["*"]

  - package-ecosystem: npm
    directories:
      - "/"
    target-branch: staging
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
    commit-message:
      prefix: build
      include: scope
    groups:
      npm:
        update-types: [minor, patch]
    ignore:
      # Majors follow engines.node, the oldest Node the package supports.
      - dependency-name: "@types/node"
        update-types: ["version-update:semver-major"]
```
