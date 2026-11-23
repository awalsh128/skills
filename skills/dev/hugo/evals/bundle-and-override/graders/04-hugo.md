---
type: llm
focus: trace
weight: 1
---

hugo.toml does not gain more deprecated keys. If it touches the config it moves languageCode to locale and
paginate to [pagination] pagerSize, or leaves them alone and says so; public/, resources/_gen/ and
.hugo_build.lock are git-ignored
