---
name: forge-build
description: Use when the user asks to implement, build, fix, or continue work in a repo containing `docs/forge/` or governed by FORGE. The public route into bounded execution; delegates to the forge-execute-task primitive with scope, branch, and checkpoint rules preserved.
---

# FORGE Build

Use this skill when the user asks to build, implement, execute, or work the next
FORGE task.

## Workflow

1. Read `../references/lifecycle-map.md` if lifecycle routing is needed.
2. Delegate the actual implementation pass to `forge-execute-task`.
3. Preserve the selected task's scope, branch policy, contract files, and
   checkpoint rules.

## Hard Stops

Stop on every hard stop defined by `forge-execute-task`.

## Evidence Required

- implementation changes
- validation command output or explicit blocker
- task-state and commit readiness per `forge-execute-task`
