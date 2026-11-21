---
name: project-setup
description:
  Use when the user asks to set up, scaffold or bootstrap a new or untooled project's editor and formatting
  baseline for VS Code or Cursor (extensions, .vscode settings, EditorConfig, Prettier at 110 columns, husky
  format check), or says "project-setup". Not for CI workflows (use github-cicd), release flow, READMEs,
  adding one tool to a configured repo (use dev-powerpack-exemplars), or language code style.
---

# project-setup

Give a new project the same editor and formatting baseline the user uses everywhere, so a fresh clone formats
the same way in VS Code, Cursor and the pre-commit hook. The baseline is opinionated: follow it even where
common advice differs, but let a repo's existing config win over it.

## Baseline

- **One line width, 110, from one place.** EditorConfig `max_line_length` is the source: Prettier reads it as
  `printWidth` and the EditorConfig extension applies it as the ruler. Tools that ignore EditorConfig (Ruff's
  `line-length`) get their own 110; that is the only copy to keep in sync.
- **Prettier owns formatting**, with `trailingComma: es5` and `proseWrap: always`, plus
  `prettier-plugin-padding-lines`.
- **EditorConfig** for the rest: UTF-8, LF, spaces, final newline, trimmed whitespace.
- **Format on save** with Prettier as the default formatter, so the hook rarely has anything to say.
- **husky pre-commit** runs the format check, so unformatted code can't land.
- **The lock file stays in sync.** The same hook checks that the lock file matches `package.json`, so a
  dependency edited in by hand can't be committed without its lock entry and then fail `npm ci` in CI.

## Steps

1. **Detect.** Read what exists before writing: `.vscode/`, `.cursor/`, `.editorconfig`, `.prettierrc*`,
   `.husky/`, ESLint config, and the manifest that names the stack (`package.json`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `*.csproj`). Cursor and VS Code share `.vscode/`; `.cursor/` only tells you which
   one the user runs. If the stack isn't evident (empty repo), ask what it will be instead of guessing.
2. **Find the defaults.** If the `dev-powerpack-exemplars` skill is available, use it for the common and
   language templates of this stack; they are the defaults, and they change, so don't work from memory.
   Otherwise use `references/editor-files.md`.
3. **Write or merge.** Read `references/lessons.md` first: it lists mistakes to check for when merging, and
   the Cursor differences. Never overwrite. Merge `recommendations` and settings keys into existing files, and
   report any key where the repo disagrees (for example a `printWidth` of 80) rather than changing it. Add
   `max_line_length = 110` to `.editorconfig` and `[110]` to `editor.rulers` if the template lacks them.
4. **Recommend extensions.** Build `.vscode/extensions.json` from `references/extensions.md`: the two
   always-on entries, then only the ones the detected stack and configs justify. Keep it to about 3-6 entries,
   since a long list is noise the user dismisses.
5. **Node projects: Prettier and husky.** Add `prettier`, `prettier-plugin-padding-lines` and `husky` as dev
   dependencies, the `format` and `format:check` scripts, `"prepare": "husky"`, and a `.husky/pre-commit` that
   runs `npm run format:check` and `npm ci --dry-run --ignore-scripts`, which fails when the lock file is out
   of sync with `package.json`. Add dependencies with `npm install`, never by editing `package.json`, and
   commit the lock file with it. Take every version from `npm view <package> version`, never from memory: a
   remembered `^1.0.0` of a plugin that only has `0.1.0` breaks `npm install`. For other stacks, don't add a
   Node toolchain unprompted; set the language's formatter in `.vscode/settings.json` (ruff, gofmt, rustfmt)
   and ask whether they want husky anyway.
6. **Verify.** Run `npm install` and `npm run format:check`. A first run on an existing repo reports many
   files: say so, offer a `.prettierignore` for generated output, and keep the bulk reformat in its own
   commit, separate from the setup commit, so the history stays readable.
7. **Report.** One line per file: created, merged (and what changed) or skipped (and why). List repo
   disagreements you left alone, and anything unverified. Leave committing and pushing to the user's ask.

Done when every baseline item above is present or reported as a disagreement, and `format:check` has run (or
the report says why not).
