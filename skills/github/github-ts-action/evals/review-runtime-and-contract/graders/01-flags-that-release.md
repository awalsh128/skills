---
type: llm
focus: last_message
weight: 2
---

Flags that release.config.ts imports @semantic-release/git, which is only a devDependency, so it breaks
consumers when the action installs with --omit=dev, and that it belongs in dependencies
