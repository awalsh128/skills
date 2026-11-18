# Recommended extensions

Write IDs into `recommendations` in `.vscode/extensions.json`. Add a stack entry only when its trigger is
present. If you are unsure an ID still exists, leave it out and say so in the report.

## Always

| ID                          | Why                                    |
| --------------------------- | -------------------------------------- |
| `esbenp.prettier-vscode`    | Runs Prettier on save                  |
| `editorconfig.editorconfig` | Makes the editor honor `.editorconfig` |

## By trigger

| Trigger                      | ID                             | Cursor note                                           |
| ---------------------------- | ------------------------------ | ----------------------------------------------------- |
| ESLint config present        | `dbaeumer.vscode-eslint`       |                                                       |
| `.github/workflows/` present | `github.vscode-github-actions` |                                                       |
| Shell scripts present        | `timonwong.shellcheck`         |                                                       |
| `Dockerfile` present         | `ms-azuretools.vscode-docker`  |                                                       |
| Python (`pyproject.toml`)    | `charliermarsh.ruff`           | Skip `ms-python.vscode-pylance`; Cursor ships its own |
| Go (`go.mod`)                | `golang.go`                    |                                                       |
| Rust (`Cargo.toml`)          | `rust-lang.rust-analyzer`      |                                                       |
| C# (`*.csproj`)              | `ms-dotnettools.csharp`        | Skip C# Dev Kit; not available on Open VSX            |
| Vitest in `package.json`     | `vitest.explorer`              |                                                       |

Not recommended by default: themes, icon packs, AI assistants and anything personal. They belong in the user's
profile, not the repo.
