@./docs/forge/AI.md
@./docs/forge/TASKS.yaml

This repository uses FORGE governance.

- use the installed `forge` skill explicitly for governed work
- if the `forge` skill is not installed or not available in this agent, stop and tell the user FORGE must be installed before governed work continues
- bootstrap `docs/forge/` first if the governance docs do not exist yet
- execute one bounded task at a time from `docs/forge/TASKS.yaml`
- in team repos, follow `docs/forge/TEAM.md` and CI enforcement
- keep working responses terse and implementation-focused; avoid restating repo context unless needed for a decision
