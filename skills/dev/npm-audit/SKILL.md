---
name: npm-audit
description:
  Evaluate and fix npm audit findings in a Node project or npm workspaces monorepo - triage by severity and by
  runtime versus dev dependency, decide which findings are real, apply the smallest non-breaking fix (lockfile
  refresh, bumped parent, or an override) and verify it. Use when the user asks to check, evaluate or fix npm
  audit, vulnerabilities, advisories or Dependabot security alerts, or when a CI audit step or an auto-filed
  "npm audit found vulnerabilities" issue fails. Not for general dependency upgrades (use Dependabot), other
  package managers, or CI workflow edits (use github-cicd).
---

# npm-audit

Find out what is actually vulnerable now, fix it with the least change, and prove it. The common trap is
acting on a stale report: auto-filed issues and old CI logs describe the tree of the day they ran.

## Steps

1. **Triage on the current tree, in one call.** Run `node <skill dir>/scripts/triage.mjs` in the project root
   (add `--omit=dev` for what ships to users). It prints each vulnerable package once with severity, direct or
   transitive, and the fix type. Don't run `npm audit` several times with different flags.
2. **Check for staleness first.** If the result is `0 vulnerabilities`, the findings are stale: compare any
   open issue or failing log against the current lockfile, say so, and close the issue with a comment naming
   the fix (mocha 12 instead of 11, an override). Don't change code to chase a stale report.
3. **Rank by exposure.** Production dependencies ship to users: fix all of them. Dev-only findings matter when
   the tool runs with credentials (publish, release or deploy jobs) or on untrusted input; otherwise moderate
   and below can wait for a grouped Dependabot PR. Say which bucket each finding is in.
4. **Fix in this order, stopping at the first that works:**
   1. `npm audit fix` (never `--force` on its own: it can major-bump or downgrade the parent to hide the
      advisory).
   2. Bump the direct parent the report names (`npm install parent@latest -w <workspace>`), reading its
      changelog if the bump is major.
   3. An `overrides` entry in the root `package.json` for the vulnerable transitive package, with a floor such
      as `">=14.0.3"`. Add it only when the parent has no fixed release yet.
5. **Prune stale overrides.** When a parent now ships a fixed version, an override can go. Test it in a
   throwaway `git worktree` (not the working tree, which may hold the user's uncommitted work): remove the
   override, restore the lockfile with `git checkout package-lock.json`, run `npm install --ignore-scripts`
   and the triage. If findings come back, keep the override. Never delete and regenerate the lockfile to test
   this: it re-resolves everything and reports noise.
6. **Verify.** Triage shows `0 vulnerabilities` (or only accepted ones, listed), then run the project's build,
   typecheck and tests. Commit lockfile changes as `build(deps)` or `fix(deps)` following the repo's release
   rules: only a change that must ship to users is `fix`.
7. **Report** what was found, what was stale, what was fixed and how, and what was left and why.

## Rules

- Install with `--ignore-scripts` when probing in a throwaway tree.
- Don't dismiss a finding as unreachable without reading how the package is used; say it is a judgment.
- Ask before closing issues or pushing; both are visible to others.
