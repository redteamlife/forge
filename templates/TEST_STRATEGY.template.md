# Test Strategy

## Purpose

Define testing expectations and enforcement levels for project work executed under FORGE.

## Testing Philosophy

- Testing should reduce uncertainty for the selected task.
- Validation depth should match risk, impact, and active FORGE mode.
- Tests and checks should be repeatable and attributable to task outcomes.
- Known gaps must be recorded explicitly.

## Unit Test Expectations

- Define unit-level expectations for task-relevant logic.
- Prefer deterministic cases that capture expected behavior and edge cases.
- Record when unit tests are not applicable and why.

## Integration Expectations

- Define integration validation requirements for cross-component changes.
- Validate interfaces, data contracts, and failure modes where applicable.
- Record environmental assumptions and limitations.

## Mode-Specific Enforcement

### Lightweight

- Minimum validation required to support task completion confidence.
- Evidence may be concise but must be recorded.

### Mid

- Task-relevant tests or equivalent validations are required.
- Failures must block completion until resolved or escalated.

### Strict

- Formal validation evidence is required per task.
- Test scope must include relevant edge cases and integration impact.

### Full Discipline

- Validation must satisfy Strict requirements plus any organizational controls.
- Exceptions require explicit approval and documented risk acceptance.

## Coverage Considerations

- Coverage targets, if used, should support risk reduction rather than serve as a sole quality indicator.
- Low coverage in high-risk areas requires explicit justification and mitigation.
- Coverage changes should be interpreted alongside review and evaluation outcomes.

## Evidence Recording

- What was validated
- How it was validated
- Result (pass/fail)
- Known limitations or deferred checks
