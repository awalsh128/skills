<p align="center">
  <img src="assets/logo.svg" alt="Agent Skills logo" width="128" height="128">
</p>

<h1 align="center">Agent Skills</h1>

<p align="center">
  Installable agentic skills for dev workflows, built for <a href="https://claude.com/claude-code">Claude Code</a>.
</p>

<p align="center">
  <a href="https://github.com/awalsh128/skills/actions/workflows/validate.yml"><img src="https://github.com/awalsh128/skills/actions/workflows/validate.yml/badge.svg" alt="validate"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/awalsh128/skills" alt="License"></a>
</p>

Opinionated skills for developers who use [Claude Code](https://claude.com/claude-code) or another agent that
reads `SKILL.md` files. Each one covers a recurring dev task, such as READMEs, CI workflows, TypeScript style
and unit tests, and applies one consistent set of conventions.

- 🧩 **One folder per skill:** a `SKILL.md` plus an optional `references/` folder that loads only when needed
- ✅ **Tested:** most skills ship their own `evals/` cases
- 🔌 **Plugin and marketplace manifests:** [`plugin.json`](.claude-plugin/plugin.json) and
  [`marketplace.json`](.claude-plugin/marketplace.json)

<p align="center">
  <a href="https://github.com/sponsors/awalsh128"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor"></a>
</p>

If you find this project useful, please consider [sponsoring it](https://github.com/sponsors/awalsh128) and
show some ❤️ for open source maintainers.

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

Add `--skill create-readme` to pick one skill and `-a claude-code` to target Claude Code. To copy a skill by
hand instead, put its folder in `~/.claude/skills/`.

Then ask for what the skill does, for example "write a README for this repo".

## Skills

| Group     | Skill                                                                   | Use it to                                                                                                                                                 |
| --------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dev`     | [`npm-audit`](skills/dev/npm-audit/SKILL.md)                            | Triage and fix `npm audit` findings with the smallest safe change.                                                                                        |
| `dev`     | [`project-setup`](skills/dev/project-setup/SKILL.md)                    | Set up a new project's VS Code or Cursor, EditorConfig, Prettier and husky baseline.                                                                      |
| `dev`     | [`vsce-project`](skills/dev/vsce-project/SKILL.md)                      | Publish a VS Code extension: manifest, Marketplace, Open VSX and pre-releases. Runs only when called by name.                                             |
| `github`  | [`check-pr-release-type`](skills/github/check-pr-release-type/SKILL.md) | Check a pull request title's Conventional Commits type against what its diff does to consumers.                                                           |
| `github`  | [`create-readme`](skills/github/create-readme/SKILL.md)                 | Write, revise or audit a README, plus the repo description and topics.                                                                                    |
| `github`  | [`cross-repo-drift`](skills/github/cross-repo-drift/SKILL.md)           | Audit your public repos for drift from a standards source, then open fix PRs on approval.                                                                 |
| `github`  | [`github-cicd`](skills/github/github-cicd/SKILL.md)                     | Create or review GitHub Actions workflows: promotion, releases, OIDC, pinned actions.                                                                     |
| `github`  | [`github-ts-action`](skills/github/github-ts-action/SKILL.md)           | Create, extend or review a TypeScript GitHub Action.                                                                                                      |
| `lang`    | [`code-design`](skills/lang/code-design/SKILL.md)                       | Write or review code in any language: readable over terse, platform and small libraries, single-responsibility modules, co-located types, config as data. |
| `lang`    | [`typescript`](skills/lang/typescript/SKILL.md)                         | Add my TypeScript specifics on top of `code-design`: platform APIs first, inferred types, JSON imports, typed config.                                     |
| `testing` | [`unit-tests`](skills/testing/unit-tests/SKILL.md)                      | Write, revise or audit unit tests in any language.                                                                                                        |

## Layout

```text
skills/<group>/<skill-name>/
├── SKILL.md      # frontmatter name and description, then the instructions
├── references/   # longer material, read only when the skill needs it
└── evals/        # test cases
```
