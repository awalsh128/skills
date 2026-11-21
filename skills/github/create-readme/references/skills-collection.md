# Skills or plugin collection README

Applies to repos that publish agent skills or a plugin (`skills/**/SKILL.md`, `.claude-plugin/plugin.json`,
`marketplace.json`). Exemplar: https://github.com/awalsh128/skills

Uses the standard layout in `SKILL.md`, including the centered header, badge row, emoji bullets and sponsor
badge. This is not personal tooling: other people install it.

- **Badges:** CI or validate workflow, license, and a release badge only once a release tag exists.
- **Description:** what the skills do for the reader, not "that I use". No first person.

## Middle sections

1. **Quick Start:** the plugin install commands from `.claude-plugin/` (marketplace add, then install) and any
   cross-agent installer the repo documents. Take names from `plugin.json` and `marketplace.json`, and the
   minimum agent version from the repo if it states one. End with one example prompt.
2. **Skills:** a table of group, skill and a short "when to use it", linking each `SKILL.md`. Keep each cell
   to a phrase. Do not copy the full frontmatter `description`; it drifts. If the repo has a script that
   checks the table, run it.
3. **Layout:** a short tree of the skill folder shape. Allowed here because the layout is the contract for
   contributors.

## Checks

- Every linked `SKILL.md` exists and the table has one row per skill folder.
- Install commands match `plugin.json` `name` and the marketplace name, verified, not remembered.
