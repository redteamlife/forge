This repository uses FORGE governance for agent-assisted development.

When working here:

- use the installed `forge` skill for governed work
- if the `forge` skill is not installed or available in this session, stop and tell the user FORGE must be installed before governed work continues
- bootstrap `docs/forge/` before implementation if the docs are missing
- read `docs/forge/AI.md`, then `docs/forge/CONTEXT.md` if present
- read `docs/forge/TASKS.index.yaml` or `docs/forge/TASKS.yaml`, then only the selected task
- do not load all `docs/forge/*` files at session start
- read team, architecture, memory, setup, evaluation, and security checklist docs only when relevant
- execute one bounded task at a time
- use the configured `task_source`; GitHub/GitLab/external trackers are authoritative when selected
- honor declared `contract_files` and update shared API/schema/client contracts with the task that changes them
- in team mode, follow `docs/forge/TEAM.md`, declared `file_scope`, and CI-backed PR workflow
- Follow `progress_policy` in `docs/forge/AI.md` (default compact); do not announce routine reads, searches, edits, commands, checks, or which skill/tool you are about to use — emit checkpoint lines, blockers, and one terminal summary.
