# Models and token budget

The goal is a low-token agent: a script does it if a script can, and a model gets the smallest input that lets
it decide. Tiers map to models in `scripts/config.py`; ask `drift.py tier <name>`, and name no model yourself.

| Work                                                 | Done by          | Tier                         | Input it sees                                                |
| ---------------------------------------------------- | ---------------- | ---------------------------- | ------------------------------------------------------------ |
| Discovery, classification, check, report aggregation | Scripts          | none                         | n/a                                                          |
| PR title, branch, label and body                     | Script           | none                         | n/a                                                          |
| Mechanical fixes (pins, reflow, a renamed file)      | Script, no agent | none                         | n/a                                                          |
| Applying a template that needs adapting              | Applier          | `balanced`                   | The one template, the one repo's relevant files, the finding |
| Review of a PR                                       | Reviewer         | `balanced`, `deep` if unsure | The diff and the check output only                           |
| Triage of an ambiguous finding                       | Subagent         | `fast`                       | The finding and the one file                                 |

Escalate, don't default up. `deep` is never the default.

## Measure before tuning

Log each subagent call, then read the totals per tier at the end of a run:

```sh
python3 <skill dir>/scripts/drift.py tokens log --run <id> --tier balanced --input 1200 --output 150
python3 <skill dir>/scripts/drift.py tokens summary --run <id>
```

Change the tier mapping on those numbers, not on guesses.
