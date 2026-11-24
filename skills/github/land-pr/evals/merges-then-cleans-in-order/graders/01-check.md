---
type: llm
focus: last_message
weight: 2
---

The reply lists these commands in this relative order: wait for checks, `gh pr merge 12 --squash`, verify the
state is `MERGED`, switch to `staging`, `git pull --ff-only`, then delete the local branch. It only describes
the commands and has not run them, which is expected. Extra read-only commands between them, such as
`git status`, do not break the order
