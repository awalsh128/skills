# Roles

There are two agent roles. Everything else is script.

## Applier

Used only where a template needs real adaptation to one repo. It is the only role that writes.

- Run it on a temp clone, with a token limited to the target repo. A real sandbox is deferred until a scoped
  token proves insufficient.
- Brief it with the one template, the one repo's relevant files and the check finding. Don't pass the
  conversation or the other repos.
- It returns a short structured verdict: files changed, anything it could not adapt, and why.
- After each attempt run `drift.py verify <dir> --rule <rule> --attempt N`. Two attempts at most. Exit 0 ends
  the loop; exit 2 means report the repo and leave it unchanged.

## Reviewer

Read-only, with fresh context, so it does not grade work it watched being made.

- Input is the diff and the check output only, never the repo or the conversation.
- It returns `pass`, `fail` or `unsure`, with a reason of one or two lines.
- It gates auto-merge, so it starts on `balanced`. `deep` only when it is unsure or the diff touches a path on
  the denylist. Drop it to `fast` only after `fast` catches every planted defect in a test against a
  deliberately failing template.
- On `fail` or `unsure` at the highest tier, don't enable auto-merge; leave the PR for the user.
