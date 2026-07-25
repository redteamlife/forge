# Security Checklists

This file is an index over `docs/forge/security-checklists/`. Do not load every checklist by default.

This index is only valid when `docs/forge/security-checklists/general.md` exists. If that directory or file is missing, the scaffold is incomplete: repair it by copying `general.md` (always) plus the task-relevant surface checklists from the FORGE skill pack's `assets/security-checklists/` into `docs/forge/security-checklists/`, preserving any project-specific checklist additions.

For normal implementation tasks, do not read security checklists unless the selected task or changed files create a security-relevant surface.

For security review:

1. Read `docs/forge/CONTEXT.md` if present.
2. Read the selected task.
3. Read `docs/forge/security-checklists/general.md`, then only the surface checklists relevant to the change.
4. Record each applicable item as `pass`, `n/a`, or escalated in `docs/forge/EVALUATION.md`.

Projects that prefer a single file may replace this index with a monolithic checklist composed from the same assets (General plus relevant surface sections, as `- [ ]` items). Never keep this index without the split directory.
