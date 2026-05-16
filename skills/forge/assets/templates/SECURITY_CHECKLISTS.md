# Security Checklists

This file is an index. Do not load every checklist by default.

For normal implementation tasks, do not read security checklists unless the selected task or changed files create a security-relevant surface.

For security review:

1. Read `docs/forge/CONTEXT.md` if present.
2. Read the selected task.
3. Read only relevant files from `docs/forge/security-checklists/`.
4. If relevance is unclear, start with `docs/forge/security-checklists/general.md`.

Compatibility fallback:

- If split checklist files do not exist, read only the relevant section of this file.
- Record each applicable item as `pass`, `n/a`, or escalated in `docs/forge/EVALUATION.md`.
