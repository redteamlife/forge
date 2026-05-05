---
name: forge-ship
description: Route FORGE shipping requests through integration, release reconciliation, claim release, and completion evidence checks.
---

# FORGE Ship

Use this skill when the user asks to ship, release, merge, reconcile, or close
out FORGE-governed work.

## Workflow

1. Read `docs/forge/AI.md`, `docs/forge/TEAM.md`, and the authoritative task
   source.
2. Confirm critique, security review, and evaluation are complete.
3. Confirm integration acceptance before marking `integrated`.
4. Confirm release acceptance before marking `complete`.
5. Record claim release, PR/MR, release PR, or release commit metadata when
   project policy requires it.
6. Do not merge or promote into `release_branch` without explicit permission in
   governed solo or team workflows.

## Hard Stops

Stop when review gates are incomplete, release acceptance is not observable, or
the requested merge/promotion violates branch policy.

## Evidence Required

- merged PR/MR, release PR, release commit, or explicit human acceptance
- updated task state
- claim release metadata when team mode applies
