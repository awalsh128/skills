---
name: land-pr
description:
  Use when the user asks to merge, land or auto-merge an open pull request and then tidy up, with phrases like
  "merge it", "squash merge once checks pass", "queue it to auto-merge", "switch back and delete the branch",
  or says "land-pr". Waits for the checks, squash-merges, returns to the right branch and deletes the local
  and remote head branch. Not for opening or reviewing the pull request (use /ship), promoting or releasing
  (use github-cicd), or a repo that merges by another method.
---

# land-pr

The tail of the pull request flow: merge, go back to where you were, delete the branch. Each step is small,
and the risk is in the ordering: deleting a branch before the merge is confirmed, or deleting one that holds
commits the pull request never got.

## Scope

- Runs only when the user asks to merge in this turn. Approval for one pull request does not carry to the
  next, and an open pull request is never merged just because its checks went green.
- Stops at the merge and the cleanup. Promotion, tagging and releases belong to `github-cicd`; if the repo has
  them, name the next step in the summary and don't run it.

## Steps

1. **Identify.** Use the number the user gave, else the current branch's pull request:
   `gh pr view [<n>] --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,headRepository,mergeable,mergeStateStatus`.
   Stop and say why if it is not open, is a draft, or is `CONFLICTING`. Note the branch the user is on now.
2. **Check the target.** The base must be where the user's flow merges. If the repo has a `staging` branch and
   the base is `main` or `master`, stop and ask; a base of `main` only moves by promotion. Take the merge
   method from the repo's allowed methods
   (`gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`); prefer squash. If squash
   is not allowed, ask.
3. **Wait for checks.** `gh pr checks <n> --watch --fail-fast`. On a failure, stop and show the failing check
   and its log tail. Never merge past a failing or missing required check, never use `--admin`, and never edit
   branch protection. If the pull request has no checks at all, say so before merging.
4. **Merge.** `gh pr merge <n> --squash`, leaving the title as the commit subject. If the user said queue or
   auto-merge, add `--auto`, report that it is queued, and stop: cleanup waits until the pull request is
   merged. Don't pass `--delete-branch`; deletion is step 6, after verification.
5. **Verify.** `gh pr view <n> --json state,mergeCommit`. Continue only on `MERGED`. On anything else, report
   the state and leave every branch alone.
6. **Clean up.** In this order:
   1. Switch to the branch the user was on before the pull request branch, else the base branch. If the
      working tree is dirty, don't force the switch: stash with the user's agreement or stop and say so. Then
      `git pull --ff-only`.
   2. Delete the local head branch. A squash merge leaves it unmerged by ancestry, so `git branch -d` will
      refuse; use `-D` only after confirming `git rev-parse <branch>` equals `headRefOid`. If it differs, the
      branch has commits the pull request never carried: keep it and report them.
   3. Delete the remote head branch only if the head repository is this one (not a fork) and the branch is
      neither the base nor the default branch. Check `git ls-remote --heads origin <branch>` first, since the
      repo may already delete head branches on merge. Then `git push origin --delete <branch>` and
      `git fetch --prune`.
   4. Don't touch other branches, even merged ones. Offer a wider sweep and wait.

Done when the pull request is `MERGED`, the user is on the right branch up to date, and both head branches are
gone or a stated reason says why one was kept.

## Report

One block: the pull request and its merge commit, the branch you are now on, each branch deleted or kept with
the reason, and the next step the repo's flow expects (promote, release) without running it. If the title
looked wrong for the release it triggers, point to `check-pr-release-type` before the user merges the next
one.
