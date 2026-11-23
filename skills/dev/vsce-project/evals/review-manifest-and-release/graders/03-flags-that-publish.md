---
type: llm
focus: last_message
weight: 2
---

Flags that publish.yml triggered by on: release will never run when the release is created with GITHUB_TOKEN,
and recommends one workflow with a release job and a publish job that needs it
