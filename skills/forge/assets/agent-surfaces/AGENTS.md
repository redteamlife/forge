# Repo Agent Guide

This repository uses FORGE governance.

- use the installed `forge` skill explicitly for governed work
- if the `forge` skill is not installed or not available in this agent, stop and tell the user FORGE must be installed before governed work continues
- bootstrap `docs/forge/` first if the governance docs do not exist yet
- default read order:
  1. `docs/forge/AI.md`
  2. `docs/forge/CONTEXT.md` if present
  3. `docs/forge/TASKS.index.yaml` or `docs/forge/TASKS.yaml`
  4. only the selected task
  5. task-relevant source files only
- do not load all `docs/forge/*` files at session start
- read `TEAM.md`, `ARCHITECTURE.md`, `MEMORY.md`, `SECURITY_CHECKLISTS.md`, `SETUP.md`, and `EVALUATION.md` only when relevant
- execute one bounded task at a time from the configured `task_source`
- if `task_source` is GitHub, GitLab, or external, treat that tracker as authoritative and use local task files only as planning snapshots unless project policy says otherwise
- honor declared `contract_files` and update shared API/schema/client contracts with the task that changes them
- in team repos, follow `docs/forge/TEAM.md` and CI enforcement when team rules are relevant
- keep working responses terse and implementation-focused; avoid restating repo context unless needed for a decision
