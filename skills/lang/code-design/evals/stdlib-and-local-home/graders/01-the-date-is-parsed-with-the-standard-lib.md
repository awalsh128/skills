---
type: llm
focus: trace
weight: 2
---

The date is parsed with the standard library (datetime.date.fromisoformat or strptime and isocalendar) and the
file is read with the csv module; no regular expression or manual string splitting parses the date or the CSV
rows
