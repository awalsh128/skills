---
name: create-readme
description:
  Write, revise or audit a GitHub repository README.md to the user's own opinionated conventions (logo, badge
  row, emoji feature bullets, sponsor badge, compact structure chosen by repo type), and keep the repository's
  GitHub description and topics consistent with it. Use only when the task is a repository's README.md or its
  GitHub description and topics, meaning the user asks to create, draft, improve, fix, modernize, shorten or
  check one, says "create-readme", or asks whether a README follows their standards. Not for API docs,
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

1. **Logo.** If one exists, put it in the title (inline `<img ... height="60" align="center">`, or centered
   above in a `<p align="center">`). If missing, add a one-line note and offer to create one. On a yes, read
   `references/logo.md`, write the placeholder SVG to `assets/logo.svg`, wire it in, and say it is a
   placeholder. Never put a placeholder or broken image in the README without a yes.
2. **Badge row** under the title. Add only badges verifiable from the repo: a workflow file exists (CI),
   `LICENSE` exists, a release tag exists. Include the registry version badge (npm, Marketplace) when the
   package is published, and the Codecov badge when a workflow runs `codecov/codecov-action` (see the type's
   reference for snippets and checks). Suggest, don't insert, a registry or coverage badge that doesn't apply
   yet. Badges are not mandatory; with no CI, omit and say so.
   Two badges must never show the same label: when several badges would (e.g. CI on `main` and CI on
   `staging`, or two workflows both named "CI"), give each a distinct label naming what sets it apart (`main`,
   `staging`, `release`), via the shields.io `label` parameter or the workflow badge's `?branch=` query plus
   `label`, and put the differentiator in the alt text too.
3. **One-paragraph description.** What it does and for whom, with links to key dependencies. No history or
   philosophy.
4. **Emoji feature bullets.** Directly under the description: 3-5 one-line bullets, each with a distinct
   emoji. This is the one deliberate emoji exception and it replaces a separate Features section. Personal
   tooling skips it. Elsewhere, emoji only where they carry information a reader scans for (⚠️ Caveats, status
   markers); never decorate every heading.
5. **Sponsor badge** after the bullets, on by default, for solo-owner projects. A pink for-the-badge badge
   linking to the owner's Sponsors page, with one line of plain text under it:

   ```markdown
   [![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/<owner>)

   If you find this project useful, please consider [sponsoring it](https://github.com/sponsors/<owner>) and
   show some ❤️ for open source maintainers.
   ```

   Exemplar: https://github.com/agent-sh/agnix. In a centered header (VS Code extensions), put the badge in a
   `<p align="center">` block as that README does.

   `<owner>` is the git remote owner. Check the page exists with `gh api users/<owner>/sponsorship` (or
   `orgs/<owner>/sponsorship`); an HTTP 404, or a fetch of the URL that redirects to the profile page, means
   no Sponsors page.
   - Not found: skip the badge; the summary says how to enable GitHub Sponsors.
   - Owner is an org or multi-human project: no badge; the summary notes org Sponsors or a fiscal host, with a
     docs link.
   - Check can't run at all (no `gh`, no network, auth error): include the badge and flag it unverified. A
     definite not-found is never "can't run".
   - The user can opt out. Personal tooling skips it.

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

The repository's About box (GitHub description and topics) is what search and the profile page show, so it
must say the same thing as the README. Do this in every mode, after the README content is settled.

1. Read the current values: `gh repo view <owner>/<repo> --json description,repositoryTopics`.
2. **Description.** One sentence, at most about 120 characters, stating what the project does in the same
   terms as the README description paragraph: same project name, same purpose, no claim the README doesn't
   make. No emoji, no badges, no trailing "for X and Y and Z" lists. Inconsistent means it describes a
   different or outdated purpose, names a feature the README doesn't, or is empty.
3. **Topics.** Suggest 5-10. GitHub requires lowercase letters, digits and hyphens, at most 50 characters each
   and 20 in total. Include:
   - the repo type: `github-actions` (Action), `vscode-extension` (VS Code extension), the registry for a
     published package (`npm-package`, `pypi-package`), `cli` for a command-line tool;
   - the main language (`typescript`, `python`, `go`, `cpp`);
   - the domain terms a person would search for, taken from the README description and feature bullets (`apt`,
     `caching`, `semantic-release`).

   Prefer GitHub's featured topic spelling (`github-actions`, not `gh-actions`). Every topic must be backed by
   the README or the code; flag existing topics that aren't, and README key concepts with no topic.

4. Show the current and proposed description and topics side by side.
   - **Write / Revise:** ASK before changing anything; it edits the live repository. On a yes, apply with
     `gh repo edit <owner>/<repo> --description "<text>" --add-topic <a>,<b> --remove-topic <c>`, then rerun
     the step 1 command to confirm.
   - **Audit:** report pass/fail for the description and topics with the proposed values. Edit nothing.
   - `gh` missing or not authenticated: give the `gh repo edit` command in the summary and say the check
     didn't run.

## Standard layout

Every type except personal tooling uses this frame. Templates below only define the middle and what is
type-specific.

1. Title (project name) with logo
2. Badge row
3. Description paragraph
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

- Write to `README.md` at the repo root (not in audit mode). Don't commit unless asked. For large revisions,
  show a summary before overwriting.
- End with a short summary: what changed, what couldn't be verified, the description and topics result
  (applied, declined or proposed), and suggestions (registry/coverage badge snippets, logo offer, Sponsors
  setup, missing CONTRIBUTING/FAQ/docs).
