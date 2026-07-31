---
name: forge-ship
description: Use when the user asks to merge, release, promote, reconcile, or close out work in a repo containing `docs/forge/` or governed by FORGE. Not for per-task commits; those complete inside forge-execute-task.
---

# FORGE Ship

Use this skill when the user asks to ship, release, merge, reconcile, or close
out FORGE-governed work.

## Workflow

1. Read `docs/forge/CONTEXT.md` if present, then `docs/forge/AI.md`.
2. Read the selected task from `TASKS.index.yaml`, its task file, `TASKS.yaml`, or the configured issue tracker.
3. Read `TEAM.md` only when `collaboration_mode: team` or branch/release policy requires it.
4. Confirm critique, security review, and evaluation are complete.
5. Confirm integration acceptance before marking `integrated`.
6. Confirm release acceptance before marking `complete`.
7. Record claim release, PR/MR, release PR, or release commit metadata when
   project policy requires it.
8. Do not merge or promote into `release_branch` without explicit permission in
   governed solo or team workflows.
9. When `dev_only_paths` is configured (clean-main model), promote with
   `<skill-root>/assets/scripts/forge-promote.sh -m "release: <summary>" [--tag vX.Y.Z]`
   from the integration branch — never merge into `release_branch` directly.
   The script snapshots the integration tree and strips `dev_only_paths`.

## Hard Stops

Stop when review gates are incomplete, release acceptance is not observable, or
the requested merge/promotion violates branch policy.

## Evidence Required

- merged PR/MR, release PR, release commit, or explicit human acceptance
- updated task state
- claim release metadata when team mode applies
