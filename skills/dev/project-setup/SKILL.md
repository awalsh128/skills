---
name: project-setup
description:
  Set up the editor and formatting baseline of a new or untooled project for VS Code or Cursor - recommended
  extensions, .vscode settings, EditorConfig, Prettier at a 110 column line width, and a husky pre-commit
  format check. Use only when the user asks to set up, scaffold or bootstrap a project's editor or tooling, to
  recommend extensions or common configs for a project, or says "project-setup". Not for CI workflows (use
  github-cicd), release flow, READMEs, adding one specific tool to an already configured repo (use
  dev-powerpack-exemplars), or language code style.
---

# project-setup

Give a new project the same editor and formatting baseline the user uses everywhere, so a fresh clone formats
the same way in VS Code, Cursor and the pre-commit hook. The baseline is opinionated: follow it even where
common advice differs, but let a repo's existing config win over it.

## Baseline

- **One line width, 110, everywhere.** Prettier `printWidth`, `editor.rulers` and EditorConfig
  `max_line_length` all say 110. Three places drifting apart is the usual failure, so set them together.
- **Prettier owns formatting**, with `trailingComma: es5` and `proseWrap: always`, plus
  `prettier-plugin-padding-lines`.
- **EditorConfig** for the rest: UTF-8, LF, spaces, final newline, trimmed whitespace.
- **Format on save** with Prettier as the default formatter, so the hook rarely has anything to say.
- **husky pre-commit** runs the format check, so unformatted code can't land.

## Steps

1. **Detect.** Read what exists before writing: `.vscode/`, `.cursor/`, `.editorconfig`, `.prettierrc*`,
   `.husky/`, ESLint config, and the manifest that names the stack (`package.json`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `*.csproj`). Cursor and VS Code share `.vscode/`; `.cursor/` only tells you which
   one the user runs. If the stack isn't evident (empty repo), ask what it will be instead of guessing.
2. **Find the defaults.** Prefer the live templates in `~/repos/gh-dev-powerpack/templates/` (`core/common`
   for `.editorconfig` and `.prettierrc.json`, `languages/<stack>` for the rest, such as `node/.vscode/`).
   Read them every time; don't work from memory, as they change. If that folder is missing, use
   `references/editor-files.md`.
3. **Write or merge.** Never overwrite. Merge `recommendations` and settings keys into existing files, and
   report any key where the repo disagrees (for example a `printWidth` of 80) rather than changing it. Add
   `max_line_length = 110` to `.editorconfig` and `[110]` to `editor.rulers` if the template lacks them.
4. **Recommend extensions.** Build `.vscode/extensions.json` from `references/extensions.md`: the two
   always-on entries, then only the ones the detected stack and configs justify. Keep it to about 3-6 entries,
   since a long list is noise the user dismisses.
5. **Node projects: Prettier and husky.** Add `prettier`, `prettier-plugin-padding-lines` and `husky` as dev
   dependencies, the `format` and `format:check` scripts, `"prepare": "husky"`, and a `.husky/pre-commit` that
   runs `npm run format:check`. Take every version from `npm view <package> version`, never from memory: a
   remembered `^1.0.0` of a plugin that only has `0.1.0` breaks `npm install`. For other stacks, don't add a
   Node toolchain unprompted; set the language's formatter in `.vscode/settings.json` (ruff, gofmt, rustfmt)
   and ask whether they want husky anyway.
6. **Verify.** Run `npm install` and `npm run format:check`. A first run on an existing repo reports many
   files: say so, offer a `.prettierignore` for generated output, and keep the bulk reformat in its own
   commit, separate from the setup commit, so the history stays readable.
7. **Report.** One line per file: created, merged (and what changed) or skipped (and why). List repo
   disagreements you left alone, and anything unverified. Don't commit or push unless asked.

## Cursor

Cursor reads `.vscode/extensions.json` and `settings.json` as VS Code does, but installs from Open VSX, not
the Microsoft Marketplace. Extensions that Microsoft restricts to its own builds (Pylance, C# Dev Kit, Remote
extensions) won't install there, so `references/extensions.md` marks them. When the user runs Cursor, use the
listed alternative or leave them out, and say which.
