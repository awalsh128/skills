---
type: llm
focus: last_message
weight: 2
---

The commands run in this relative order: wait for checks, `gh pr merge 12 --squash`, verify the state is
`MERGED`, switch to `staging`, `git pull --ff-only`, then delete the local branch. Extra read-only commands
between them, such as `git status`, do not break the order
