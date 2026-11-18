# AGENTS.md

Claude Code plugin of personal agentic skills. Skills live in `skills/<group>/<name>/SKILL.md` and are listed
in `.claude-plugin/plugin.json`.

These rules apply only when modifying this repository's own files. They are not conventions to follow when
using the skills in other projects; each skill's `SKILL.md` carries those.

## Rules

- ALWAYS keep a skill's `description` narrow: it states when the skill applies and what it is not for. Quote
  nothing with `: ` in it, or the YAML frontmatter stops parsing.
- ALWAYS run `python3 scripts/validate.py` after changing a skill or manifest.
- NEVER edit `*-workspace/` folders; they are eval run output and are git-ignored.
- Files under `skills/*/*/evals/**/files/` (including their nested `AGENTS.md`) are test input for evals, not
  guidance for this repo.
- The pre-commit hook (`npm install` enables it) bumps the patch version in `.claude-plugin/plugin.json` when
  a commit does not. Do not bypass it with `--no-verify`.
- ASK FIRST before pushing, tagging or publishing.

## Quick Commands

```bash
python3 scripts/validate.py
npm install   # enables the husky pre-commit hook
```
