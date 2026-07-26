---
name: forge-build
description: Route FORGE build requests to bounded task execution while preserving task source, branch, file-scope, and checkpoint rules.
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
