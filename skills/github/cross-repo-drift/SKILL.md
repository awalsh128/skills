---
name: cross-repo-drift
description:
  Use only when the user invokes cross-repo-drift or explicitly asks to audit or fix drift across their own
  GitHub repos against a standards source repo. Audits the owner's public repos with a read-only report, then
  on approval opens PRs that bring named repos back in line. Never starts on its own. Not for one repo (use
  that repo's own sync command), adding one tool to a repo, project setup (use project-setup) or writing CI
  workflows (use github-cicd).
disable-model-invocation: true
---

# cross-repo-drift

Manage drift between a fleet of repos and one standards source. A Python script does everything that has one
right answer; a model is used only where judgment is needed. The skill holds no standards of its own: rules,
detectors and fixes come from the standards source's `check` and fix commands.

## Setup

Set these before the first run (details in `scripts/config.py`):

- `DRIFT_CHECK_CMD`: runs in a repo and prints
  `{"findings": [{"rule", "category", "path", "message", "fixable"}]}` as JSON.
- `DRIFT_FIX_CMD`: changes the working tree for the rule in the `DRIFT_RULE` environment variable.
- `DRIFT_OWNER`: whose repos to audit (public, non-fork, non-archived only; private repos are out of scope).
- `multi-gitter` on the path and a `GITHUB_TOKEN` limited to the target repos, for `apply` only.

If a variable is missing, say which one and stop. Don't guess a command.

## Calling it

The skill never starts on its own, and a bare call prints usage and does nothing else.

- `audit [--repos a,b] [--out report.json]` is read-only: it clones shallowly into a temp directory, runs
  `check`, and reports per repo its profile, open findings and excepted findings. Safe to schedule.
- `apply --repos a,b` or `apply --report report.json` opens PRs. It needs named repos or an audit report with
  an `approved` list of `{repo, rule}` pairs that the user wrote. It refuses an `unclassified` repo and any
  run with `DRIFT_UNATTENDED` set. Use `--dry-run` first.

Run `python3 <skill dir>/scripts/drift.py` for the exact usage.

## Flow

1. **Audit.** Run `audit --out report.json` and show the summary. The report plus the user's approval is the
   plan; don't change anything yet.
2. **Resolve prompts.** A finding in category `format-collision` is never applied. Show each source with its
   file and value (and the language standard and the user's preference when known), and ask which to keep,
   another value, or leave as is. Record a confirmed choice as an `exceptions` entry for the repo.
3. **Apply.** For approved mechanical rules, `apply` runs `multi-gitter run` with
   `--conflict-strategy replace`, so a re-run force-pushes the tool's own `cross-repo-drift/<category>` branch
   and reuses its open PR. Branch and label make re-runs find their own work; there is no state file. The PR
   title type comes from the fixed category map in `config.py`; a category not in the map is never applied.
4. **Adapt, only if needed.** If a template needs real adaptation, spawn the applier (see
   `references/roles.md`) on a temp clone. After each attempt run
   `drift.py verify <dir> --rule <rule> --attempt N`. At most two attempts; the loop ends when `verify` exits
   0, never when the agent says it is done. After the cap, report the repo and leave it unchanged.
5. **Review.** Spawn the fresh-context reviewer with the diff and the check output only.
6. **Auto-merge.** After the reviewer passes, `drift.py automerge --repo R --pr N --reviewed` enables GitHub
   auto-merge only where the repo requires the `release impact` check. The repo's CI decides eligibility, not
   this skill. A repo without that check waits for the user.

## Keep it cheap

A clean audit costs no tokens. Scripts do discovery, classification, check, verification, PR titles and
mechanical fixes. Give a subagent the smallest input that lets it decide, and take its answer as a short
structured verdict. Pick the model by tier with `drift.py tier fast|balanced|deep`; never name a model
yourself. See `references/models-and-tokens.md` for who gets which tier and how to log tokens.

## What this skill does not do

- It does not decide merge eligibility, change a repo's settings, or touch private repos or forks.
- It does not edit a repo's standing exceptions to make a finding go away; exceptions are the user's call.
- It does not fix a collision, a deliberate difference or an `unclassified` repo.

## References

- `references/release-impact.md`: the three rules every auto-merged PR must satisfy, and the category to
  commit type map. Read before opening or merging PRs.
- `references/roles.md`: briefs for the applier and the reviewer. Read before spawning either.
- `references/models-and-tokens.md`: tiers, inputs and token logging. Read before spawning a subagent.
- `references/report-format.md`: the audit report and the check output contract.
