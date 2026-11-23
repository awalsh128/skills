---
tags: [vsce-project]
max_turns: 20
timeout_seconds: 480
allowed_tools: [Read, Glob, Grep, Skill]
---

vsce-project: the release job for 1.4.0 ran. The Marketplace publish succeeded and the Open VSX publish failed
with a 503. I'd like to just re-run the whole workflow and, if it complains about the version, bump
package.json to 1.4.1 by hand. Is that fine? Input files: see files/
