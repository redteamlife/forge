---
name: forge
description: Governed workflow for AI-assisted coding on a real repo. Triggers: bounded tasks, file scope, task ledgers, claim-before-implement, evidence trails, critique/review/security gates, or multi-agent/multi-repo coordination. Use on any mention of "FORGE", `docs/forge/`, or governed development, or when agents drift outside scope. Not for one-off edits or unstructured review.
---

# FORGE

FORGE is an explicit workflow for bounded work: one task, clear scope, hard stops, evidence, and clean checkpoints.

Use it for governed implementation, planning, review, shipping, coordination, or context-safe bootstrap.

## Routing

- Bootstrap or migrate docs: `forge-bootstrap`
- Plan lifecycle work: `forge-plan`
- Build/implement a task: `forge-build` or `forge-execute-task`
- Review work: `forge-review`
- Ship, release, or close out: `forge-ship`
- Critique scope and assumptions: `forge-critique`
- Run security review: `forge-security-review`
- Check done/evidence: `forge-evaluation`
- Read/update lessons: `forge-memory`
- Manage private/public tool releases: `forge-tool-workflow`
- Coordinate multi-repo shared-contract work: `forge-cross-project`

Read references only when the current task requires them:

- team and branches: `references/team-mode.md`
- repo flavors: `references/repo-flavors.md`
- agent surfaces: `references/agent-flavors.md`
- DevSecOps gates: `references/devsecops-gates.md`
- app docs: `references/application-docs.md`
- lifecycle map: `references/lifecycle-map.md`
- skill anatomy: `references/skill-anatomy.md`
- context and token discipline: `references/token-efficiency.md`

## Operating Model

1. Read the minimum project-local context needed for the current step.
2. Prefer `docs/forge/CONTEXT.md` when present; otherwise use conservative `lite` defaults.
3. Read `docs/forge/AI.md`, the compact task index or configured task source, one selected task, and task-relevant source files.
4. Do not load all FORGE docs, all tasks, all memory, or all security checklists at startup.
5. Preserve one bounded checkpoint at a time: implementation, evidence, task state, and commit or PR/MR handoff.
6. Stop on ambiguity, missing prerequisites, architecture conflict, unsafe operations, unresolved security concerns, or failed gates.
7. Keep FORGE explicit. Agent surfaces route; they do not make it always-on by default.

## Team Mode

When multiple developers or agents work in parallel:

- use feature branches rather than direct work on shared branches
- claim one task before implementation
- require explicit `file_scope` for executable tasks
- prefer issue assignment and labels when GitHub or GitLab is authoritative
- use append-only evidence and memory records where possible
- require CI and protected-branch merging

## Output Discipline

Default to terse, implementation-focused responses:

- working update: `Status: <done/doing/blocker>. Next: <next step>.`
- task closeout: `Done: <result>. Changed: <files or areas>. Next: <next step or none>.`
- blocker: `Blocked: <fact>. Need: <decision or missing prerequisite>.`

Avoid repeated recap, file-content echoes, and routine narration unless clarity prevents a bad decision.
