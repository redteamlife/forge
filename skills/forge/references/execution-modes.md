# FORGE Execution Modes

`execution_mode` in `docs/forge/AI.md` controls checkpoint pacing. It never
changes rigor: every checkpoint in every mode runs the full review gates and
records `gates:` outcomes before its commit.

## Modes

### `manual` (default)

Stop after each completed checkpoint (gates + evidence + task state + commit).
The default for all profiles and the right choice for new users.

### `batch`

Continue up to `batch_size` checkpoints in one run (`batch_size` in the
FORGE-config block; required for batch). Eligibility per next task:

- task independence: no overlap with the just-completed task's `file_scope` or
  `contract_files`, and no dependency on un-integrated work
- branch topology: in solo-governed (`solo_branch_flow: task-branches`), finish
  the current task branch first — merge it, or hand it off and start the next
  task from the integration branch. Do not stack task branches unless the
  project documents stacking. With `solo_branch_flow: direct`, continue on the
  working branch.
- team mode: release/re-claim per task and reconcile the authoritative ledger
  between checkpoints; claim conflicts end the run.

### `auto`

Batch without a fixed count: continue until the ledger has no eligible task.
Permitted only when org policy allows it (`auto_mode_permitted` in
`forge-org-policy`); projects under a policy that forbids it treat `auto` as
`batch` with `batch_size: 1` and say so.

## Stops in every mode

- any execute-task hard stop, failed gate, `escalated`, or `handoff-required`
- a task declaring `requires_independent_review: true` — unconditional stop;
  no mode may self-continue past it
- ledger exhaustion or no eligible independent task
- claim conflict or un-reconcilable task state

## Per-run overrides

"Do not stop until done" and similar kickoff phrases are a per-run override
interpreted as `batch` bounded by the run's stated scope. They do not change
the configured `execution_mode`; only a human editing `AI.md` does.
