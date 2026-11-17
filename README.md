# <img src="assets/logo.svg" alt="Agent Skills logo" height="60" align="center"> awalsh128 Agent Skills

[![validate](https://github.com/awalsh128/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/awalsh128/skills/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/awalsh128/skills)](LICENSE)

Installable agentic skills that I use in my dev workflows, built for [Claude Code](https://claude.com/claude-code).

- 🧩 **One folder per skill:** a `SKILL.md` plus an optional `references/` folder that loads only when needed
- ✅ **Tested:** each skill ships its own `evals/` cases
- 🔌 **Plugin and marketplace manifests:** [`plugin.json`](.claude-plugin/plugin.json) and [`marketplace.json`](.claude-plugin/marketplace.json)

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/awalsh128)

If you find this project useful, please consider [sponsoring it](https://github.com/sponsors/awalsh128) and show some ❤️ for open source maintainers.

## Quick Start

Install as a Claude Code plugin (Claude Code 2.1.275 or later):

```sh
claude plugin marketplace add awalsh128/skills
claude plugin install awalsh128@awalsh128-skills
```

Or install with the [skills CLI](https://github.com/vercel-labs/skills), which works across agents:

```sh
npx skills add awalsh128/skills
```

Add `--skill create-readme` to pick one skill and `-a claude-code` to target Claude Code. To copy a skill by hand instead, put its folder in `~/.claude/skills/`.

Then ask for what the skill does, for example "write a README for this repo".

## Skills

| Group     | Skill                                                         | What it does                                                                                                                                                         |
| --------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `github`  | [`create-readme`](skills/github/create-readme/SKILL.md)       | Writes, revises or audits a GitHub README to my own conventions: logo, badge row, emoji feature bullets, sponsor badge, compact layout chosen by repo type.          |
| `github`  | [`github-ts-action`](skills/github/github-ts-action/SKILL.md) | Creates, extends or reviews a TypeScript GitHub Action: testable runner, rollup bundle, Vitest, semantic-release, SHA-pinned workflows.                               |
| `lang`    | [`typescript`](skills/lang/typescript/SKILL.md)               | Writes, modifies or reviews TypeScript: readable over terse, platform and small libraries over hand-rolled code, single-responsibility modules, co-located types.     |
| `testing` | [`unit-tests`](skills/testing/unit-tests/SKILL.md)            | Writes, revises or audits unit tests in any language: behavior through the public API, Arrange-Act-Assert, three-part names, parameterized cases, faked boundaries. |

## Layout

```text
skills/<group>/<skill-name>/
├── SKILL.md      # frontmatter name and description, then the instructions
├── references/   # longer material, read only when the skill needs it
└── evals/        # test cases
```
