# Lessons and Cursor

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
