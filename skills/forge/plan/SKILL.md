---
name: forge-plan
description: Route FORGE planning requests to the repo's configured task source, task-shaping docs, and lifecycle guidance without duplicating execution workflow.
---

# FORGE Plan

Use this skill when the user asks to plan, break down, sequence, or prepare
FORGE-governed work.

## Workflow

1. Read `docs/forge/CONTEXT.md` if present, then `docs/forge/AI.md` if present.
2. Identify the authoritative task source: local `TASKS.index.yaml` plus task files, legacy `TASKS.yaml`, GitHub Issues, GitLab Issues, or external tracker.
3. Use `references/lifecycle-map.md` only when lifecycle routing is ambiguous.
4. Shape tasks with bounded scope, file scope, dependencies, contract files,
   and review requirements.
5. Do not implement unless the user explicitly switches to build or
   `forge-execute-task`.

## Hard Stops

Stop when the authoritative task source is unclear, a task cannot be bounded,
or a contract/architecture decision is needed before sequencing.

## Evidence Required

- task entries, issue links, or explicit human-approved task breakdown
