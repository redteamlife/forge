# Security Review: checkpoint-output protocol (TASK-030)

Required because TASK-030 modifies a validator (`validate-generated-docs.sh`)
and workflow-governance surfaces (the generated agent surfaces + root skill).

## Change surface

Documentation and instruction changes: a new `progress_policy` config field, a
protocol reference, an inline fallback in `execute-task`, and a positive-invariant
fixture. No executable behavior, network, credential, or repository-control
change. The validator addition only classifies a config value and emits a note.

## Findings

- **No new trust boundary.** `progress_policy` affects output verbosity only; it
  cannot relax a gate, scope rule, or hard stop. Gates and stops are unchanged.
- **Governance not weakened.** The surface migration replaces "always terse"
  with "defer to `progress_policy` (default compact)". Default behavior is
  unchanged for repos without the field; `detailed` only increases narration —
  it cannot suppress a blocker (the protocol requires blockers always emit
  check + evidence + need).
- **Config validation is fail-open-safe.** An invalid `progress_policy` fails the
  doc validator (surfaced, not silently ignored); the both-fields case emits a
  precedence note. No injection surface (values are matched against a fixed
  enum).
- **Drift guard.** The positive-invariant fixture prevents a future surface from
  silently omitting the deferral, keeping the governance instruction consistent
  across harnesses.

## Residual risk

None material. Verbosity is not a security control; the change cannot cause a
gate, review, or stop to be skipped.

## Outcome

security: pass.
