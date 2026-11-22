---
type: llm
focus: trace
weight: 1
---

Because the package is published to npm, which does not rewrite relative image paths, the demos use absolute
`https` URLs, or the final message flags that relative `media/` paths will break on the npm page, and says the
media should stay out of the published package (`files` or `.npmignore`).
