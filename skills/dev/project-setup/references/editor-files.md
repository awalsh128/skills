# Fallback editor files

Use these only when the `dev-powerpack-exemplars` skill isn't available. They match the powerpack's Node
templates at the time of writing, with 110 columns set everywhere.

`.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 110

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab

[*.{py,cs,java,kt,rs}]
indent_size = 4
```

`.prettierrc.json`

```json
{
  "printWidth": 110,
  "trailingComma": "es5",
  "proseWrap": "always",
  "plugins": ["prettier-plugin-padding-lines"]
}
```

`.prettierignore`

```text
node_modules/
dist/
out/
coverage/
package-lock.json
```

`.vscode/settings.json`

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.rulers": [110],
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "files.trimTrailingWhitespace": true
}
```

`.husky/pre-commit`

```sh
npm run format:check
```

`package.json` additions

```json
{
  "scripts": {
    "prepare": "husky",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

Dependencies go in with `npm install --save-dev prettier prettier-plugin-padding-lines husky`, so npm picks
versions that exist. `format:check` over the whole repo is fine for small repos; if the hook gets slow, switch
it to `lint-staged` and say so.
