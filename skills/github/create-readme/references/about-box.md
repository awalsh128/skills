# Description and topics

The repository's About box (GitHub description and topics) is what search and the profile page show, so it
must say the same thing as the README. Do this in every mode, after the README content is settled.

1. Read the current values: `gh repo view <owner>/<repo> --json description,repositoryTopics`.
2. **Description.** One sentence, at most about 120 characters, stating what the project does in the same
   terms as the README description paragraph: same project name, same purpose, no claim the README doesn't
   make. No emoji, no badges, no trailing "for X and Y and Z" lists. Inconsistent means it describes a
   different or outdated purpose, names a feature the README doesn't, or is empty.
3. **Topics.** Suggest 5-10. GitHub requires lowercase letters, digits and hyphens, at most 50 characters each
   and 20 in total. Include:
   - the repo type: `github-actions` (Action), `vscode-extension` (VS Code extension), the registry for a
     published package (`npm-package`, `pypi-package`), `cli` for a command-line tool;
   - the main language (`typescript`, `python`, `go`, `cpp`);
   - the domain terms a person would search for, taken from the README description and feature bullets (`apt`,
     `caching`, `semantic-release`).

   Prefer GitHub's featured topic spelling (`github-actions`, not `gh-actions`). Every topic must be backed by
   the README or the code; flag existing topics that aren't, and README key concepts with no topic.

4. Show the current and proposed description and topics side by side.
   - **Write / Revise:** ASK before changing anything; it edits the live repository. On a yes, apply with
     `gh repo edit <owner>/<repo> --description "<text>" --add-topic <a>,<b> --remove-topic <c>`, then rerun
     the step 1 command to confirm.
   - **Audit:** report pass/fail for the description and topics with the proposed values. Edit nothing.
   - `gh` missing or not authenticated: give the `gh repo edit` command in the summary and say the check
     didn't run.
