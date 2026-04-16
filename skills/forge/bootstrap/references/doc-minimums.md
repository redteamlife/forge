# Bootstrap Doc Minimums

Use the smallest project-local governance set that still supports bounded execution.

## Solo Default

Required:

- `docs/forge/AI.md`
- `docs/forge/TASKS.yaml`

Recommended:

- `docs/forge/ARCHITECTURE.md` when architecture constraints materially matter
- `docs/forge/EVALUATION.md` when explicit completion gates are needed
- `docs/forge/MEMORY.md` when the project benefits from reusable lessons

## Team Default

Add these from the start when multiple developers or agents will work in parallel:

- `docs/forge/TEAM.md`
- `docs/forge/SECURITY_CHECKLISTS.md`
- explicit `file_scope` on executable tasks
- task claim metadata in `TASKS.yaml`
