---
type: llm
focus: trace
weight: 1
---

Each run starts from a fresh profile and a copy of the workspace, and scenes reset what they change: the
`shoutLint.*` settings including a per-language override for `maxCapsRun`, open editors and unsaved edits, and
the webview panel. Reading the settings keys from the manifest or listing them all counts.
