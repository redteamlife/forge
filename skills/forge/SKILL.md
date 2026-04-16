---
name: forge
description: Keep AI-assisted coding disciplined with bounded tasks, hard stops, review gates, and clear team workflow. Use when you want FORGE to bootstrap docs/forge, execute the next task safely, and coordinate work across solo or team repos.
---

# FORGE

Use this skill when the user wants FORGE-style governance as a reusable skill-based workflow rather than a large prompt or document set.

FORGE is best treated as:

- stable workflow logic in skills
- project-specific state in repository docs
- optional external enforcement in CI and hooks

## Quick Routing

- For creating or refreshing FORGE project docs, use `bootstrap/`.
- For selecting and implementing the next bounded task, use `execute-task/`.
- For scope and quality review before completion, use `critique/`.
- For checklist-based security review, use `security-review/`.
- For definition-of-done and evidence checks, use `evaluation/`.
- For reading and updating reusable lessons, use `memory/`.
- For private/public tool release workflows, use `tool-workflow/`.
- For multi-developer coordination rules, branch discipline, and task claiming, read `references/team-mode.md`.

## Operating Model

Keep the runtime contract lean:

1. Read only the minimum project-local files needed for the current step.
2. Preserve bounded-task checkpoints at all times. If the project explicitly permits batch or auto behavior, that only means the agent may continue to the next task after finishing the current one, updating task state, and creating the required Conventional Commit.
3. Stop on ambiguity, missing prerequisites, architecture conflict, or unresolved security concerns.
4. Record evidence and memory updates in deterministic project-local files.

## Token Discipline

Default to low-token behavior:

- keep working responses terse and task-focused
- do not restate repo docs or repeat the task unless needed for a decision
- prefer direct implementation over explanatory narration
- summarize blockers in a few short points instead of long prose
- load additional references only when the current step actually needs them
- do not read every checklist or template when only one section is relevant
- avoid file-by-file changelog output unless the user asks for it

## Team Mode

When a repository is worked on by multiple developers or multiple IDE agents at the same time:

- require feature branches rather than direct work on shared branches
- require task claiming before implementation begins
- require explicit `file_scope` for executable tasks
- prefer append-only evidence and memory records over rewriting shared summaries
- require CI enforcement and protected branch merging for completed task work

Read these shared references only when needed:

- `references/skill-pack-overview.md`
- `references/doc-minimums.md`
- `references/forge-to-skills-mapping.md`
- `references/team-mode.md`
- `references/token-efficiency.md`

Use templates from `assets/templates/` only when scaffolding or migrating a project into this skill-based flow.
