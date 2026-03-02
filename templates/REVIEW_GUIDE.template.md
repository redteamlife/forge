# Review Guide

## Purpose

Define consistent review criteria for implementation quality, security posture, and architectural alignment.

## Code Review Criteria

- Correctness against task requirements
- Scope adherence to selected task only
- Clarity and maintainability of changes
- Error handling and failure-mode consideration
- Documentation updates where required
- Test alignment with `TEST_STRATEGY.md`

## Security Review Checklist

- Trust boundary impact identified
- Authentication/authorization implications reviewed (if applicable)
- Input validation and output handling reviewed
- Sensitive data handling reviewed
- Privileged operations or permission changes reviewed
- Dependency or integration risk reviewed
- Unsafe assumptions documented and escalated

## Architectural Alignment Checks

- Change matches `ARCHITECTURE.md` responsibilities and boundaries
- Data flow assumptions remain valid
- New coupling or hidden dependencies are identified
- Deployment assumptions remain accurate or are updated
- Architectural deviations are documented and approved

## Refactor Guidance

- Prefer task-bounded refactors that directly support the selected task
- Avoid unrelated cleanup in the same task commit
- Document structural changes that alter maintainability or ownership boundaries
- Escalate broad refactors that exceed task authority or mode limits

## Review Outcome Recording

- Reviewer context (human or agent role)
- Findings summary
- Blocking issues
- Non-blocking improvements
- Final disposition (pass, pass with notes, fail)
