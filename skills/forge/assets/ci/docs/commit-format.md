# FORGE Commit Format

FORGE commits use Conventional Commits. The subject line and the no-AI-attribution
rule are enforced by the `commit-msg` hook.

```text
<type>[optional scope]: <description>

[optional body]

[optional FORGE-task: <task-id>]
```

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`,
`build`, `ci`, `perf`, `revert`.

## FORGE trailers are optional

Gate outcomes live in the task file's `gates:` block (machine-readable and
verifiable) — not in the commit. Do not hand-assert gate state in a commit
trailer.

- `FORGE-task: <id>` — optional but useful: a durable commit->task link that
  survives ledger trimming (`git log --grep=<id>`). The `task/<id>` branch name
  already carries the same link.
- `FORGE-mode:` — optional; if present, it must be a valid mode value. It
  duplicates `docs/forge/AI.md` and is usually unnecessary noise.
- `FORGE-gate:` — removed. It was never verified and duplicated the task-file
  `gates:` record.

Trailers, when used, appear in the footer separated from the body by a blank
line. Do not include AI attribution, assistant branding, or tool-marketing text.
