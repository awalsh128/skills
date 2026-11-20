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

- **One line width, 110, from one place.** EditorConfig `max_line_length` is the source: Prettier reads it as
  `printWidth` and the EditorConfig extension applies it as the ruler. Tools that ignore EditorConfig (Ruff's
  `line-length`) get their own 110; that is the only copy to keep in sync.
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
2. **Find the defaults.** If the `dev-powerpack-exemplars` skill is available, use it for the common and
   language templates of this stack; they are the defaults, and they change, so don't work from memory.
   Otherwise use `references/editor-files.md`.
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

## Lessons learned

Mistakes from consolidating an existing repo's configs; check for them when merging.

- **Don't repeat a value the config file already supplies.** `prettier.printWidth` in `settings.json`
  duplicates `.prettierrc` or EditorConfig, which win anyway. A per-language `formatOnSave` that restates the
  global one adds nothing; the `[python]` block needs only `editor.defaultFormatter`.
- **Recommending the EditorConfig extension without a `.editorconfig` does nothing.** Add the file or drop the
  recommendation.
- **`proseWrap` can't live in EditorConfig.** When everything else comes from `.editorconfig`, put Prettier
  options in the `prettier` key of `package.json` instead of a one-line `.prettierrc`.
- **`proseWrap: always` reflows every Markdown file once, and it escapes `_`, `*` and `<` in old prose.** That
  can turn latent breakage (stray `*` in LaTeX, odd imports) into build errors. Build before and after,
  compare the errors against the pre-change tree, fix real ones, and commit the reflow with the config change
  only if the user wants a single commit.
- **Prettier 3 already skips what `.gitignore` lists.** Keep `.prettierignore` to tracked generated output
  (generated pages and data) and anything `.gitignore` covers only partly, such as `resources/_gen/`. If a
  generated file isn't Prettier-clean, ignore it, or `format:check` fails on every regeneration.
- **The Ruff formatter doesn't rewrap comments, docstrings or long strings.** Enable `E501` at the same 110 so
  the editor flags them.
- **ShellCheck needs a binary, not just the extension.** Have the setup script link the system `shellcheck` or
  install one into a git-ignored tools folder, and point `shellcheck.executablePath` at that link so both
  cases behave the same. Check a pinned wrapper package's postinstall behaviour first; some download the
  binary on first run, not at install. A comment that begins `# shellcheck` is parsed as a directive (SC1073),
  so word prose comments differently.

## Cursor

Cursor reads `.vscode/extensions.json` and `settings.json` as VS Code does, but installs from Open VSX, not
the Microsoft Marketplace. Extensions that Microsoft restricts to its own builds (Pylance, C# Dev Kit, Remote
extensions) won't install there, so `references/extensions.md` marks them. When the user runs Cursor, use the
listed alternative or leave them out, and say which.
