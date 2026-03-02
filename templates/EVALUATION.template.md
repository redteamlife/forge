# Evaluation

## Purpose

Define the gates that determine whether a task is complete and ready for commit or release progression.

## Definition of Done

A task is done only when:

- The selected task scope is implemented without unrelated work
- Required documentation updates are completed
- Critique pass is completed
- Security review pass is completed
- Required testing/validation is completed per `TEST_STRATEGY.md`
- Commit-per-task discipline is satisfied

## Mode-Specific Gates

### Lightweight

- Task scope verified
- Basic review completed
- Required validation evidence recorded

### Mid

- Lightweight gates
- Architecture alignment confirmed
- Security review completed
- Evaluation evidence recorded

### Strict

- Mid gates
- Formal review criteria from `REVIEW_GUIDE.md` applied
- Architecture and exploration artifacts updated when relevant
- Release-readiness checks completed as applicable

### Full Discipline

- Strict gates
- Organizational governance checks completed as required
- Exceptions documented with approval and risk acceptance

## Security Validation Requirements

- Trust boundary impact assessed
- Sensitive data handling reviewed where applicable
- Permission or privilege changes reviewed
- Security assumptions documented
- Unresolved concerns block completion and require escalation

## Performance Considerations

- Identify whether the task has performance impact
- Define required validation for performance-sensitive changes
- Record results, limitations, and follow-up actions

## Release Readiness Checks

- Documentation consistency across required files
- Task status accuracy in `TASKS.yaml`
- No known blocking defects for the selected task
- Commit message format compliance
- Branch policy compliance

## Evaluation Record Template

### Task ID


### Gate Results

- Scope:
- Critique:
- Security:
- Testing/Validation:
- Documentation:
- Commit Discipline:

### Outcome

- Pass / Fail:
- Notes:
