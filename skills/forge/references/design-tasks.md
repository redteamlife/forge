# FORGE Design Tasks

Non-trivial design, architecture, or workflow decisions are recorded as a
`task_type: design` task with a companion document. This keeps rationale
governed and reviewable without forcing execution semantics onto work that
produces a decision, not a code change.

## Convention

- The document lives at `docs/forge/designs/TASK-<id>-<slug>.md`.
- The ledger task carries `task_type: design` and is tracked by `review_state`,
  not execution gates:
  `draft → in-review → changes-requested → accepted`.
- Design tasks are **exempt from the `gates:` block**. `review_state` is their
  signal; `forge_next_gate.py` returns a design-task exemption for them.
- `status: complete` means the *document* is authored; acceptance is
  `review_state: accepted`. Do not mark a design accepted while it is still
  under review.
- Keep an index at `docs/forge/designs/README.md` (ordered link list) so the
  set is navigable and publishable via the application-docs handbook export.

## When to use

- A change spans multiple skills/assets, or is hard to reverse.
- A decision benefits from an external/adversarial review round before
  implementation.
- An architecture decision that also warrants an ADR when `application_docs` is
  enabled (the ADR is the durable record; the design task is the working one).

## Lifecycle

1. `forge-plan` records the design task and drafts the document (`draft`).
2. Circulate for review; set `in-review`. Reviewer findings → `changes-requested`;
   incorporate and re-circulate.
3. On sign-off, set `review_state: accepted` and `status: complete`, then plan
   the bounded implementation tasks the design names.

Implementation tasks spawned from a design ARE normal tasks: they carry
execution gates and, when they touch CI or repository controls, a security
review.
