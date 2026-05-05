---
name: forge-review
description: Route FORGE review requests through critique, security review, and evaluation gates without treating CI as a complete review.
---

# FORGE Review

Use this skill when the user asks to review a FORGE task, PR, MR, branch, or
completed implementation.

## Workflow

1. Run `forge-critique` for scope, architecture, docs, contracts, and task
   metadata.
2. Run `forge-security-review` when the change surface or project policy
   requires security review.
3. Run `forge-evaluation` only after critique and required security review are
   complete.
4. Keep findings first and evidence-backed.

## Hard Stops

Stop when critique finds blockers, security review has unresolved concerns, or
evaluation evidence is incomplete.

## Evidence Required

- critique result
- security-review result or explicit n/a rationale
- evaluation gate result
