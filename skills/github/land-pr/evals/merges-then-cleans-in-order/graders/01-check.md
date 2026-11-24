---
type: llm
focus: last_message
weight: 2
---

The commands run in this order: wait for checks, `gh pr merge 12 --squash`, verify the state is `MERGED`,
switch to `staging`, `git pull --ff-only`, then delete the local branch
