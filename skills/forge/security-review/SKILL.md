---
name: security-review
description: Apply FORGE checklist-based security review to a task. Use when selecting a task-specific security checklist, reviewing trust-boundary and sensitive-data impact, and producing explicit pass, n-a, or escalated outcomes for each item.
---

# FORGE Security Review

Use this skill after implementation and before completion.

## Workflow

1. Read the task's `task_type` from `docs/forge/TASKS.yaml` if available.
2. Apply the General checklist plus the relevant surface-specific sections in `docs/forge/SECURITY_CHECKLISTS.md`.
3. If the project was bootstrapped from the shared assets, use only the sections relevant to the active change rather than reading every possible checklist.
4. Require an explicit outcome for every item: `pass`, `n/a`, or escalated.
5. If any unresolved concern remains, stop before evaluation.

## Notes

- Free-form narrative is not enough by itself.
- Prefer recording results in `docs/forge/EVALUATION.md`.
- Keep the review crisp and machine-checkable where possible.
- If `docs/forge/SECURITY_CHECKLISTS.md` is missing for a team workflow that expects it, stop and ask for it to be created rather than inventing ad hoc criteria.
- Shared baseline assets live under `assets/security-checklists/` in the installed skill pack; bootstrap may compose a smaller project-local checklist from those assets.
