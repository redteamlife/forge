# AI Execution Configuration

```FORGE-config
forge_version: 1.6.0
FORGE_mode: Lightweight
execution_mode: manual
collaboration_mode: solo
task_source: local
agent_context_profile: lite
security_profile: baseline
solo_branch_flow: task-branches
release_branch: main
response_style: terse
ci_enforcement: disabled
application_docs: false
```

## Purpose

Govern development of the FORGE skill pack itself. Bounded tasks with evidence live on `dev`; `main` receives squash promotions only and never contains `docs/forge/`.

## Constraints

- All development happens on `dev` (or task branches off `dev`); never commit directly to `main`.
- Promote to `main` only via `scripts/forge-promote.sh` (squash merge that strips `docs/forge/`); a CI guard on `main` rejects any `docs/forge/` content.
- Run `python3 verify-repo.py` before any commit that touches `skills/forge/`.
- Keep canonical skill content in `skills/forge/`; keep root install docs and scripts aligned with it.
- Respect SKILL.md size budgets enforced by `verify-repo.py`.
- The course PDF and other `*.pdf` files are reference material and stay untracked.
