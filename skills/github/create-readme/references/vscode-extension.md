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
  <a href="https://github.com/<owner>/<repo>/blob/main/LICENSE"><img src="https://img.shields.io/github/license/<owner>/<repo>" alt="License"></a>
</p>

<tagline or description paragraph, linking the thing it wraps>
```

The three registry lines (Version, Marketplace downloads, Open VSX downloads) are conditional on publication; see
"VSCE badges" below. Drop any that don't apply rather than leaving them in.

- **Centering:** use `<p align="center">` with `<a><img></a>` pairs, not Markdown badge syntax, because Markdown
  images can't be centered. Give every image alt text; it doubles as the badge label.
- **Paths:** a monorepo points the logo at the extension package's `images/` folder
  (`packages/<ext>/images/logo.png`), and the badge row still describes the extension.
- **VSCE badges (insert once the extension is published):** take `<publisher>` and `<name>` from the extension's
  `package.json`, and check the Marketplace page (`https://marketplace.visualstudio.com/items?itemName=<publisher>.<name>`)
  returns 200 first.
  - **Marketplace Version** and **Marketplace downloads**: the two `vsmarketplacebadges.dev` badges above.
  - **Open VSX downloads**: add it only when the extension is published to Open VSX (the repo has a publish
    workflow using `ovsx`, or `https://open-vsx.org/extension/<publisher>/<name>` returns 200).
  - Labels must differ: "Version", "Marketplace downloads", "Open VSX downloads". Add Open VSX version too
    only with a distinct label such as "Open VSX".
  - Not yet published: suggest the snippets in the summary instead of inserting them.
- **Other badges:** CI and license when verifiable (CI per branch, labeled, when more than one). Add the Codecov
  badge when a workflow uploads coverage to Codecov.
- **Description:** add a sentence on what the extension leaves alone, if it matters.
- **Bullets:** keep the demo link or GIF together with the emoji bullets.
- **Sponsor badge:** centered, and preceded by `<!-- prettier-ignore -->` when the repo uses Prettier.

## Middle sections

1. **Quick Start:** install (Marketplace search by display name, or
   `code --install-extension <publisher>.<name>`) and the first thing to do with it. This comes first.
2. **Settings:** a table from `contributes.configuration` (name, description, default).
3. **Advanced Usage:** only what the commands and settings don't already explain.

If publication on the Marketplace can't be confirmed, say so in the summary rather than asserting the install
ID.

## Notes

- Check every command and setting name against `contributes` in `package.json`.
- An MCP server or agent integration gets its own short section.
- The Marketplace icon in `package.json` must be a PNG. If the README uses an SVG logo, mention that the icon
  is separate.
