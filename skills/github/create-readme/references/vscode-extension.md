# VS Code extension README

Applies to repos with a `package.json` that has `engines.vscode`. Exemplar:
https://github.com/awalsh128/vscode-keep-sorted

Uses the standard layout in `SKILL.md`, with these differences at the top.

## Header (required for this type)

Even with no logo, do not start with a plain `# Title`. Use exactly this shape:

```html
<p align="center">
  <img src="images/logo.png" alt="<project name> logo" width="128">  <!-- omit the img line if no logo; see logo convention -->
</p>
<h1 align="center"><project name></h1>
<p align="center"><tagline, linking the thing it wraps></p>
```

- **Badges:** put the row in `<p align="center">`. CI and license when verifiable; Marketplace
  version/downloads and Open VSX are suggested as snippets (publisher and ID from `package.json`).
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
