# Report and check formats

## Check output (standards source to this skill)

`DRIFT_CHECK_CMD` prints JSON on stdout. Exit code is ignored; a non-JSON output is reported as `no-check`.

```json
{
  "findings": [
    {
      "rule": "unpinned-uses",
      "category": "pin",
      "path": ".github/workflows/ci.yml",
      "message": "pin actions to full SHAs",
      "fixable": true
    }
  ]
}
```

`category` picks the commit type through the map in `scripts/config.py`. `fixable: false` findings are
reported, not applied.

## Repo overrides file

`.agents/standards-overrides.json` in each repo holds `profile`, `releaseBranch`, `integrationBranch` and
`exceptions: [{"rule", "reason"}]`. An exception is permanent, lives next to the code, and keeps a finding out
of the open list. Missing file means no exceptions and a detected profile.

## Audit report (this skill to the user)

```json
{
  "generated": "2026-11-20T21:30:00+00:00",
  "owner": "<owner>",
  "repos": [
    {
      "repo": "<name>",
      "status": "ok | unclassified | no-check | clone-failed",
      "profile": "node-package",
      "release_model": "semantic-release | none",
      "base_branch": "staging",
      "findings": [],
      "excepted": []
    }
  ]
}
```

To approve work, add `"approved": [{"repo": "<name>", "rule": "<rule>"}]` at the top level and pass the file
to `apply --report`. Only those pairs are acted on. An `unclassified` repo is refused until it has a `profile`
in its overrides file.
