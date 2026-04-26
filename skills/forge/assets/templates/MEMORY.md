# Memory

```FORGE-memory
max_entries: 50
entry_types:
  - bug-pattern
  - architecture
  - workflow
  - security
  - consolidated
```

## Entries

Use this compact entry shape:

```yaml
- date: YYYY-MM-DD
  type: workflow
  task: example-task
  actor:
  branch:
  summary: Short reusable lesson.
  detail:
```

Load the most recent five entries first. Load older entries only when their
`type`, `task`, component, or failure mode matches the current task.

_No entries yet._

## Maintenance Notes

- Keep entries brief, factual, and reusable.
- In team mode, include `task`, `actor`, and `branch` in new entries.
- Prefer patterns and failure modes over PR-specific storytelling.
- When adding entry 51, consolidate the oldest 25 entries into one
  `type: consolidated` summary entry before appending the new entry.
