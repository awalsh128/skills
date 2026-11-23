---
type: llm
focus: last_message
weight: 1
---

Suggests --ignore-scripts for probing, verifies with a triage showing 0 or listed accepted findings plus build
and tests, names the commit type as fix(deps) only for what ships to users and build(deps) otherwise, and asks
before pushing or closing issues
