# AI Execution Configuration

```FORGE-config
FORGE_mode: Mid
execution_mode: manual
batch_size: 2
ci_enforcement: disabled
```

## Purpose

Define the AI-facing operating constraints for this project so execution remains bounded, auditable, and aligned with project documentation.

## Scope

### In

- Tasks explicitly listed in `TASKS.yaml`
- Work aligned with approved architecture and documented constraints
- Documentation updates required to complete or validate approved tasks
- Review and evaluation activities required by `FORGE.md`

### Out

- Undocumented or speculative feature work
- Changes that bypass required review, evaluation, or commit discipline
- Work on restricted branches if branch policy disallows it
- Actions that violate project or organizational security policy

## Constraints

- Follow `FORGE.md` as the execution authority for workflow behavior.
- Execute only bounded task work selected from `TASKS.yaml`.
- Respect documented architecture, trust boundaries, and deployment assumptions.
- Stop on missing prerequisites, failed validation, or ambiguous requirements.
- Maintain deterministic documentation and commit updates for completed work.

## Non-Goals

- Autonomous project-wide refactoring without task authorization
- Undocumented architecture redesign
- Silent policy exceptions
- Combining unrelated tasks into a single implementation pass

## Architecture Alignment

- Validate each task against `ARCHITECTURE.md` before implementation.
- If the task introduces architectural change, require documented rationale and approval per mode.
- Record unresolved architectural uncertainty in `ARCHITECTURE_EXPLORATION.md` when required by mode.

## Testing Expectations

- Follow `TEST_STRATEGY.md` for test scope and enforcement.
- Do not mark tasks complete without the required validation evidence for the active mode.
- Record deviations, limitations, or deferred coverage explicitly.

## Evaluation Requirements

- Apply `EVALUATION.md` gates before task completion.
- Include security and release-readiness checks as required by mode.
- Keep incomplete tasks in `incomplete` status until gates are satisfied or formally escalated.

## Commit Discipline

- Enforce commit-per-task behavior unless the active mode or project policy specifies a stricter rule.
- Use the structured commit message format defined in `FORGE.md`.
- Do not bundle unrelated task work in a single commit.

## Escalation Policy

Escalate and stop execution when:

- Scope or requirements are unclear
- Required documents are missing or contradictory
- Security or trust-boundary concerns are identified
- Evaluation gates fail and no approved remediation path exists
- Branch or commit policy cannot be satisfied
