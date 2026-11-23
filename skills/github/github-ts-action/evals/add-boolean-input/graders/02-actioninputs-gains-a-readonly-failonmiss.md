---
type: llm
focus: trace
weight: 2
---

ActionInputs gains a readonly failOnMiss: boolean field, and getInputs in src/index.ts reads it with
core.getBooleanInput; @actions/core is not imported in src/action.ts and runAction does not read process.env
