# Release and ruleset rules

Rules 11-15 of the hard rules in `SKILL.md`, kept here because they apply to release, ruleset and audit work,
not to every workflow edit.

11. **Releases have an off switch.** The release job's `if` is
    `vars.RELEASES_ENABLED != 'false' || inputs.dry-run`. Every route to a release (a staging push, promote, a
    manual run) goes through that one job, and a dry run is always allowed. A repo that must hold releases
    while it settles inverts it (`== 'true'`) and sets the variable when ready. A release job that merely
    fails is not a hold: with no tags, every staging push plans `1.0.0-rc.1`, and a pipeline fixed later
    releases at once.
12. **A major release needs a typed confirmation.** `promote.yml` takes an optional `confirm-major` input. A
    step compares the latest candidate tag on `staging` with the latest official tag on `main` and fails
    unless the input equals the planned version, when it starts a new major or is the first official release.
    There is no maintenance branch, so a major strands users of the previous one. Where the repo has a
    TypeScript toolchain, put the comparison in a tested script instead of the bash step in the template.
13. **One gate job per matrix, and rulesets match names exactly.** A matrix job reports one check per
    combination, but a ruleset requires a name, so add a gate job named like the required check that `needs:`
    the matrix and passes only when every case did. Pin each required check to the GitHub Actions app
    (`integration_id` 15368). Merging a changed `.github/rulesets/*.json` applies nothing: apply it, then
    compare the live ruleset with the file.
14. **Don't run what proves nothing.** `concurrency` cancels superseded runs only for pull requests
    (`group: ${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.ref || github.run_id }}`,
    `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`), so staging pushes that release are
    never cancelled or dropped. With squash-only merges the title is the commit, so skip per-commit commitlint
    in CI and keep the title lint.
15. **Verify a release from the source, not from `npm view`.** The registry's metadata is cached and can lag a
    publish by minutes: right after `Published <pkg>@<version>` in the release log, `npm view <pkg>` and its
    `dist-tags` can still show the old version. Take the proof from the release job log, the tag and the
    GitHub release, then ask the registry for the exact version (`npm view <pkg>@<version> version`) and retry
    for a few minutes before calling it a failure. Don't treat `latest` still showing the old version as a
    failed release, and never re-run a release because of it.
