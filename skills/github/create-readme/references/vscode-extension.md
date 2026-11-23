# VS Code extension README

Applies to repos with a `package.json` that has `engines.vscode`. Exemplar:
https://github.com/awalsh128/vscode-keep-sorted

Uses the standard layout in `SKILL.md`, with these differences at the top.

## Header (required for this type)

Even with no logo, do not start with a plain `# Title`. Use exactly this shape, top to bottom: centered logo,
centered `<h1>`, then a centered badge row. The tagline (or the description paragraph) follows as normal
Markdown. Exemplar: https://github.com/awalsh128/vscode-regex-explain

```html
<p align="center">
  <img src="images/logo.png" alt="<project name> logo" width="128" height="128">  <!-- omit if no logo; see logo convention -->
</p>

<h1 align="center"><project name></h1>

<p align="center">
  <a href="https://marketplace.visualstudio.com/items?itemName=<publisher>.<name>"><img src="https://vsmarketplacebadges.dev/version/<publisher>.<name>.svg?label=Version" alt="Version"></a>
  <a href="https://marketplace.visualstudio.com/items?itemName=<publisher>.<name>"><img src="https://vsmarketplacebadges.dev/downloads/<publisher>.<name>.svg?label=Marketplace%20downloads" alt="Marketplace downloads"></a>
  <a href="https://open-vsx.org/extension/<publisher>/<name>"><img src="https://img.shields.io/open-vsx/dt/<publisher>/<name>?label=Open%20VSX%20downloads" alt="Open VSX downloads"></a>
  <a href="https://github.com/<owner>/<repo>/actions/workflows/ci.yml"><img src="https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

<tagline or description paragraph, linking the thing it wraps>
```

The three registry lines (Version, Marketplace downloads, Open VSX downloads) are conditional on publication;
see "VSCE badges" below. Drop any that don't apply rather than leaving them in.

- **Centering:** use `<p align="center">` with `<a><img></a>` pairs, not Markdown badge syntax, because
  Markdown images can't be centered. Give every image alt text; it doubles as the badge label.
- **Paths:** a monorepo points the logo at the extension package's `images/` folder
  (`packages/<ext>/images/logo.png`), and the badge row still describes the extension.
- **VSCE badges (insert once the extension is published):** take `<publisher>` and `<name>` from the
  extension's `package.json`, and check the Marketplace page
  (`https://marketplace.visualstudio.com/items?itemName=<publisher>.<name>`) returns 200 first.
  - **Marketplace Version** and **Marketplace downloads**: the two `vsmarketplacebadges.dev` badges above.
  - **Open VSX downloads**: add it only when the extension is published to Open VSX (the repo has a publish
    workflow using `ovsx`, or `https://open-vsx.org/extension/<publisher>/<name>` returns 200).
  - Labels must differ: "Version", "Marketplace downloads", "Open VSX downloads". Add Open VSX version too
    only with a distinct label such as "Open VSX".
  - Not yet published: suggest the snippets in the summary instead of inserting them.
- **Other badges:** CI when verifiable (CI per branch, labeled via the shields.io form in `SKILL.md`, when
  more than one). Add one Codecov badge, for the default branch (`main` or `master`) only, when a workflow
  uploads coverage to Codecov.
- **Display name:** take the title and logo alt text from the extension's `displayName` in `package.json`,
  exactly as written. The Marketplace requires a unique display name, so it may differ from the repo slug, the
  npm package name or the prose name (for example `Regex Explain Lab` for `regex-explain`). Never change it to
  match the slug, and don't report the difference as an inconsistency. In a monorepo, the extension package's
  `displayName` names the extension, while the root title may name the repository. Where the README refers to
  the extension as an installable thing (Quick Start, Marketplace search), use the `displayName`; in prose
  about the underlying library or the repo, the plain name is fine. A repo README title that disagrees with
  `displayName` for another reason (for example a stray `VSCode` prefix) is still worth flagging, and fixing
  is the user's call.
- **About description:** the GitHub description doesn't need the display name, but if it uses one, it uses the
  `displayName`.
- **Description:** add a sentence on what the extension leaves alone, if it matters.
- **Bullets and demos:** the hero GIF goes directly under the emoji bullets; other demos follow
  `references/demos.md`. Use vsce-demo to produce the GIFs for this type. With five or more GIFs, also load
  the vsce-demo skill and read its README placement reference for the split and registry caveats.
- **Sponsor badge:** centered, and preceded by `<!-- prettier-ignore -->` when the repo uses Prettier.

## Middle sections

1. **Quick Start:** installation, then the first thing to do with it. This comes first. See "Installation"
   below for what the install step covers.
2. **Settings:** a table from `contributes.configuration` (name, description, default).
3. **Advanced Usage:** only what the commands and settings don't already explain.

If publication on the Marketplace can't be confirmed, say so in the summary rather than asserting the install
ID.

## Installation

An extension is not limited to VS Code. It runs in any editor built on the VS Code extension host, such as
Cursor, VSCodium and Windsurf, so write the install step for the editors the user's readers actually use, not
for VS Code alone. The Marketplace is for Microsoft's own products; those forks read the Open VSX Registry
instead, so which editors can install by search depends on where the extension is published.

- **VS Code:** Marketplace search by display name, or `code --install-extension <publisher>.<name>`. Only when
  the Marketplace page is confirmed.
- **Forks (Cursor, VSCodium, Windsurf and similar):** search by display name in the editor's Extensions view,
  or use the editor's own CLI (`cursor --install-extension`, `codium --install-extension`). Include this only
  when the extension is published to Open VSX (see "VSCE badges"). Check the editor's CLI name rather than
  assuming it.
- **Not on the registry an editor reads:** install the `.vsix` from the GitHub release with
  `--install-extension <file>.vsix`, and say which editors that covers.
- Keep it short: a line or two per editor, in one list, not a section per editor.

### LLM features packaged with the extension

When `contributes` in `package.json` ships LLM features, installing the extension is not enough to use them,
so the install step also says what else the reader must do. Look for `chatParticipants`, `languageModelTools`,
`mcpServerDefinitionProviders`, and any bundled instructions, prompts or agent skills files. For each that is
present:

- **Prerequisites:** the chat or model provider the feature needs (for example a chat extension or an API key
  setting from `contributes.configuration`), and the minimum editor version from `engines.vscode`.
- **Enabling:** whether it registers itself on install or must be turned on, and where (a setting name, a
  command from `contributes.commands`).
- **Per-editor differences:** a feature the extension registers through a VS Code API may not exist in a fork,
  or may need manual setup there (for example an MCP server entry in that editor's own config file). Say so
  for each editor listed above, only for what you can verify in the repo or the extension's docs. If you can't
  verify a fork, say it is untested rather than implying it works.
- **Don't invent:** every setting, command and file name comes from `package.json` or the repo, and an LLM
  feature with no verifiable install path goes in the summary as a question for the user.

Keep this inside the Quick Start install step when it is a line or two; give it its own short section (see
Notes) when it has more than that.

## Notes

- Check every command and setting name against `contributes` in `package.json`.
- An MCP server or agent integration gets its own short section when it needs more than a line or two of setup
  beyond installing the extension (see "Installation").
- The Marketplace icon in `package.json` must be a PNG. If the README uses an SVG logo, mention that the icon
  is separate.
