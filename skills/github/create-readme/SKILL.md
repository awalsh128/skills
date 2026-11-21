---
name: create-readme
description:
  Use when the task is a repository's README.md or its GitHub description and topics - write, revise or audit
  one to the user's own conventions (logo, badges, emoji feature bullets, sponsor badge, structure by repo
  type) - or the user says "create-readme" or asks whether a README follows their standards. Not for API docs,
  docstrings, changelogs or design docs.
---

# create-readme

This skill applies the user's personal README conventions. They are opinions, not generic best practice:
follow them even where common advice differs. Exemplar of the conventions:
https://github.com/awalsh128/vscode-keep-sorted (read a local clone only if one exists).

## Modes

- **Write**: no README yet. Draft one.
- **Revise**: a README exists. Enforce the structural rules (order, sponsor badge, badges, Quick Start first,
  no tab duplication). Flag content judgment calls (extra sections, long rationale) in the summary instead of
  deleting them. Keep accurate content and move it into the right slot.
- **Audit**: the user asks whether a README complies or says "check". Report pass/fail per convention with
  line references. Edit nothing until asked.

## Before writing

Ground every claim in the repo. A README that describes things the code doesn't do is worse than none.

1. Read the existing `README.md`, manifests (`package.json`, `pyproject.toml`, `go.mod`, `action.yml`...),
   `LICENSE`, `.github/workflows/`, and any `images/`, `assets/` or `logo.*`.
2. Run `git remote -v` for the real owner/repo. Every badge and link is built from it, never hardcoded.
3. Work out the **project name**: the plain-English name a person would call it, not the repo slug
   (`cache-apt-pkgs-action` → "Cache APT Packages", `vscode-keep-sorted` → "Keep Sorted"). Take it from, in
   order: the existing README title, the manifest's display name (`displayName`, `name` in `action.yml`,
   package description), then the slug with separators spaced, generic suffixes (`-action`, `vscode-`, `-cli`)
   dropped and words capitalized. Keep proper nouns and acronyms as the project writes them. If more than one
   reading is plausible, pick one and say so in the summary. Use it in the title, the logo alt text and prose.
   Keep the repo slug only where it must be literal: URLs, badge links, `uses:`, install commands and code.
   For a VS Code extension the manifest's `displayName` is authoritative, not a suggestion: the Marketplace
   requires it to be unique, so it can carry a suffix the repo slug and prose don't (`Regex Explain Lab` for
   `regex-explain`). Use it as written for the title, the logo alt text and Marketplace-facing prose, never
   "correct" it toward the slug, and don't flag the difference as an inconsistency. See
   `references/vscode-extension.md`.
4. Find real install, build and test commands from scripts, Makefile or CI. Run the cheap ones.
5. Classify the repo and read its template (see **Templates**). If the type or purpose isn't evident (e.g. a
   lone `main.go`), ask the user what the project is for instead of guessing.

## Conventions (all repo types)

1. **Logo and title.** Prefer a centered header: logo, `<h1>` title and a one-line tagline, each centered.
   Exemplar: https://github.com/awalsh128/vscode-keep-sorted

   ```html
   <p align="center">
     <img src="images/logo.png" alt="<project name> logo" width="128" height="128">
   </p>

   <h1 align="center"><project name></h1>

   <p align="center">
     <one-line tagline, linking the thing it wraps>
   </p>
   ```

   The badge row follows, centered the same way. Use this even with no logo (omit the first block). Fall back
   to a plain `# Title` with an inline `<img ... height="60" align="center">` only when the repo's README
   already uses that style and the user hasn't asked to change it, and for personal tooling. If no logo
   exists, add a one-line note and offer to create one. On a yes, read `references/logo.md`, write the
   placeholder SVG to `assets/logo.svg`, wire it in, and say it is a placeholder. Never put a placeholder or
   broken image in the README without a yes.

2. **Badge row** under the title. Add only badges verifiable from the repo: a workflow file exists (CI),
   `LICENSE` exists, a release tag exists. Include the registry version badge (npm, Marketplace) when the
   package is published, and the Codecov badge when a workflow runs `codecov/codecov-action` (see the type's
   reference for snippets and checks). Suggest, don't insert, a registry or coverage badge that doesn't apply
   yet. Badges are not mandatory; with no CI, omit and say so. Two badges must never show the same label: when
   several badges would (e.g. CI on `main` and CI on `staging`, or two workflows both named "CI"), give each a
   distinct label naming what sets it apart (`main`, `staging`, `release`), via the shields.io `label`
   parameter or the workflow badge's `?branch=` query plus `label`, and put the differentiator in the alt text
   too.
3. **One-paragraph description.** What it does and for whom, with links to key dependencies. No history or
   philosophy.
4. **Emoji feature bullets.** Directly under the description: 3-5 one-line bullets, each with a distinct
   emoji. This is the one deliberate emoji exception and it replaces a separate Features section. Personal
   tooling skips it. Elsewhere, emoji only where they carry information a reader scans for (⚠️ Caveats, status
   markers); never decorate every heading.
5. **Sponsor badge** after the bullets, on by default, for solo-owner projects (skipped for personal tooling
   and on opt-out). Read `references/sponsor-badge.md` for the snippet and the Sponsors-page check.

6. **Quick Start first.** The shortest working example precedes reference material. Real warnings (e.g. `sudo`
   required) use `> [!IMPORTANT]` / `> [!NOTE]` callouts, right after the sponsor badge.
7. **Tables for options.** Inputs, outputs, settings in tables with name, description, required, default.
8. **Compact.** Aim for about 150 lines. Move overflow (long config reference, FAQ, API detail) to `docs/` or
   an existing doc and link it. Add a Contents list only when the README stays long for a good reason, and
   flag that.
9. **Link out, don't duplicate.** Link Issues, Discussions, FAQ, `CONTRIBUTING`, `SECURITY`, generated API
   docs, Releases (instead of a changelog) and `docs/`, only when they exist and after verifying each link.
   Suggest missing ones in the summary; never invent them.
10. **No tab duplication.** GitHub shows Contributing, License, Code of conduct and Security as tabs. Drop
    those sections when the file exists. The license badge covers License. At most one short closing line
    links to `CONTRIBUTING.md`. If the file is missing, suggest it in the summary; never fake it in the
    README.
11. **Verified, not invented.** Every command, input name and link is checked against the repo. Say plainly
    what you couldn't verify.

## Description and topics

The repository's About box (GitHub description and topics) must say the same thing as the README. In every
mode, once the README content is settled, read `references/about-box.md` and compare the live values with the
README. Write / Revise ask before editing the live repo; Audit edits nothing.

## Standard layout

Every type except personal tooling uses this frame. Templates below only define the middle and what is
type-specific.

1. Centered logo, title (project name) and tagline
2. Badge row (centered under the header)
3. Description paragraph (the tagline is not a substitute for it)
4. Emoji feature bullets (replace any Features section)
5. Sponsor badge, then any callout warnings
6. **Middle sections** from the type's template
7. At most one closing line linking `CONTRIBUTING.md`, if it exists

## Templates

Classify, then read only the matching file for its middle sections and type-specific rules. Drop sections that
don't apply; never pad.

| Repo type                                              | Read                             |
| ------------------------------------------------------ | -------------------------------- |
| GitHub Action (has `action.yml`)                       | `references/github-action.md`    |
| Library or package published to a registry             | `references/library.md`          |
| VS Code extension (`engines.vscode` in `package.json`) | `references/vscode-extension.md` |
| Dotfiles, scripts, site, prototype, anything else      | `references/personal-tooling.md` |

## Finishing

Done when every convention above is applied (or reported pass/fail in Audit), every command and link is
verified or flagged unverified, and the About box is compared with the README.

- Write to `README.md` at the repo root (Audit mode writes nothing). Leave committing to the user's ask. For
  large revisions, show a summary before overwriting.
- End with a short summary: what changed, what couldn't be verified, the description and topics result
  (applied, declined or proposed), and suggestions (registry/coverage badge snippets, logo offer, Sponsors
  setup, missing CONTRIBUTING/FAQ/docs).
