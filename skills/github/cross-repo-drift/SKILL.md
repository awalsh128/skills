---
name: cross-repo-drift
description:
  Audit your public GitHub repos against a standards source repo with a read-only report, then on approval
  open PRs that bring named repos back in line. Use when the user asks to check or sync their public repos
  against a standards repo. Not for private repos, forks or a one-off edit to a single repo.
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
- `gh` logged in (`gh auth login`). That is the only credential: the owner defaults to the logged-in account,
  and `apply` passes `gh auth token` to `multi-gitter` for that one process. No token is set by hand.
- `DRIFT_OWNER` (optional): audit another user or org instead of the logged-in account. Public, non-fork,
  non-archived repos only; private repos are out of scope.
- `multi-gitter`, for `apply` only. `drift.py deps` reports what's missing; `drift.py deps --install`
  downloads `multi-gitter` into `~/.local/bin` (sha256-verified) with no root, or the user can install it
  themselves. `gh`, `git` and `jq` need a package manager, so `deps` prints the command for the user to run.
  Ask before running `--install`.

If `DRIFT_CHECK_CMD` or `DRIFT_FIX_CMD` is missing, say which one and stop. Don't guess a command.

## Calling it

The skill runs only when the user calls it by name, and a bare call prints usage and does nothing else.

- `repos` prints a checklist of in-scope repos, numbered, with the repo the working directory belongs to
  pre-checked. Show it and let the user pick by number, name or `all`; pass the picks to `--repos`.
- `audit [--repos a,b|1,3|all] [--out report.json]` is read-only: it clones shallowly into a temp directory,
  runs `check`, and reports per repo its profile, open findings and excepted findings. Safe to schedule.
- `apply --repos a,b` or `apply --report report.json` opens PRs. It needs named repos or an audit report with
  an `approved` list of `{repo, rule}` pairs that the user wrote. It refuses an `unclassified` repo and any
  run with `DRIFT_UNATTENDED` set. Use `--dry-run` first.

Run `python3 <skill dir>/scripts/drift.py` for the exact usage.

Done when every approved `{repo, rule}` pair has a PR (reviewed, and auto-merge enabled where eligible) or a
reported reason it was left unchanged.

## Flow

1. **Audit.** Run `repos`, show the checklist and ask which to include. Then run `audit --out report.json` and
   show the summary. The report plus the user's approval is the plan; don't change anything yet.
2. **Resolve prompts.** A finding in category `format-collision` is never applied. Show each source with its
   file and value (and the language standard and the user's preference when known), and ask which to keep,
   another value, or leave as is. Record a confirmed choice as an `exceptions` entry for the repo.
3. **Apply.** For approved mechanical rules, `apply` runs `multi-gitter run` with
   `--conflict-strategy replace`, so a re-run force-pushes the tool's own `cross-repo-drift/<category>` branch
   and reuses its open PR. Findings are grouped into one job per repo and category, so a repo gets one PR per branch however many
   findings it has. Branch and label make re-runs find their own work; there is no state file. The PR
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

## Boundaries

- Merge eligibility belongs to each repo's CI, and settings belong to the repo owner.
- Scope is public, non-fork repos; private repos and forks are out.
- A repo's standing exceptions stay as the user wrote them; only the user edits them.
- A collision, a deliberate difference or an `unclassified` repo goes to the user as a prompt, unfixed.

## References

- `references/release-impact.md`: the three rules every auto-merged PR must satisfy, and the category to
  commit type map. Read before opening or merging PRs.
- `references/roles.md`: briefs for the applier and the reviewer. Read before spawning either.
- `references/models-and-tokens.md`: tiers, inputs and token logging. Read before spawning a subagent.
- `references/report-format.md`: the audit report and the check output contract.
