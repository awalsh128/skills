---
type: llm
focus: trace
weight: 1
---

`.husky/pre-commit` also fails when the lock file is out of sync with `package.json` (for example by running
`npm ci --dry-run`), and every dependency was added with `npm install` so `package-lock.json` matches
`package.json`
