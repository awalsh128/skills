---
type: llm
focus: trace
weight: 2
---

runAction fails with a clear Error message when failOnMiss is true and the cache misses, and does not fail on
a hit or when failOnMiss is false; index.ts keeps the try/catch with core.setFailed
