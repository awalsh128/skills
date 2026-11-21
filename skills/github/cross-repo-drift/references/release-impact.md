# Release impact

Squash-only merges make the PR title the commit, so the title type decides whether a release happens. Each
repo's CI provides a required check named `release impact`; GitHub's native auto-merge does the rest. This
skill only enables auto-merge, after the reviewer passes, and never decides eligibility itself.

## The check passes only if all three hold

1. **Title type doesn't release.** The type is non-releasing (`ci`, `chore`, `style`, `docs`, `test`,
   `refactor`) under that repo's own release config, confirmed by parsing it or by the release workflow's dry
   run.
2. **Safe paths only.** The PR touches none of the denylist in `scripts/config.py`: the release and promote
   workflows, `.github/chainguard`, `.github/rulesets`, version or dependency fields of `package.json`, or
   lockfiles. Security-sensitive paths are excluded even when the title looks harmless.
3. **Right target.** The PR targets the repo's integration branch (`staging` where one exists, or
   `integrationBranch` from its overrides file), never the release branch.

A repo with no release config gets no check and no auto-merge, so its PRs wait for the user.

## Category to commit type

The map lives in `scripts/config.py` as `CATEGORY_COMMIT_TYPES`.

| Category          | Commit type |
| ----------------- | ----------- |
| `pin`             | `ci`        |
| `workflow-syntax` | `ci`        |
| `reflow`          | `style`     |
| `agent-config`    | `chore`     |

A rule that changes behavior is never in this map, so it is never applied here and never eligible for
auto-merge.
