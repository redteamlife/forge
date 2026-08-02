---
name: forge-execute-task
description: Execute one bounded FORGE task from repository-local governance docs. The primitive behind `forge-build`. Use when reading `docs/forge/` state, selecting the next incomplete task, enforcing task scope, implementing, running review gates, and stopping on ambiguity or failed gates.
---

# FORGE Execute Task

Execute one governed task with minimal context. A checkpoint is not complete until its review gates have run and outcomes are recorded.

## Use When

- the user asks to start, build, implement, or continue governed work
- bounded FORGE tasks exist locally or in the configured tracker, or `forge-build` routes here

## Do Not Use When

- the repo needs `forge-bootstrap`; the user only wants review/evaluation/planning; or the work cannot be bounded to one checkpoint

## Default Reads

`docs/forge/CONTEXT.md` (if present), `docs/forge/AI.md`, the task index (`TASKS.index.yaml`, else `TASKS.yaml` or the configured tracker), exactly one selected task, and the files in its `file_scope`. Read other docs (TEAM, ARCHITECTURE, SETUP, checklists, EVALUATION) only when a step needs them.

## Workflow

1. Confirm branch safety, worktree state, and project-local prerequisites.
2. Parse `AI.md` for `collaboration_mode`, `task_source`, `solo_branch_flow`, `execution_mode`, `repo_flavor`, `security_profile`, and context profile.
3. Select or claim exactly one task; read only that task's details.
4. When memory docs exist, read `MEMORY.index.yaml` plus the relevant topic file before the alignment check (`forge-memory` read pattern).
5. Start with declared `file_scope`; note why before any expansion.
6. Check branch, team, architecture, contract, and security constraints.
7. Implement the smallest safe change; run relevant checks.
8. Run the review gates via `forge-review` (critique always; security per change surface/`security_profile`; evaluation is a full gate when `EVALUATION.md` exists, else recorded in-task). Record in the `gates:` block: `critique: pass|fail` · `security: pass|n/a|escalated` · `evaluation: pass|handoff-required|fail`.
9. Record a memory entry only when a reusable lesson exists: `memory: entry|no-relevant-lesson|store-unavailable`.
10. Update task state and evidence.
11. Commit per project policy (Conventional Commit, no AI attribution).
12. Stop or continue per `execution_mode`; `requires_independent_review` is an unconditional stop.

`<skill-root>/assets/scripts/forge_next_gate.py <task-file>` prints the next required gate.

Output (fallback if `../references/checkpoint-output.md` is not loaded): follow `progress_policy` (default `compact`) — one line per checkpoint (`TASK-<id> complete|blocked|handoff-required | …`), blockers always state check + evidence + need, and one terminal `Done: … Refs: … Remaining: …` summary. No per-task recaps; the task file and commit are the record.

Task sources — `local`: `TASKS.index.yaml` plus `docs/forge/tasks/<id>.yaml`, else `TASKS.yaml`. `github`/`gitlab`: issues are authoritative; local task files are planning snapshots. `external`: only the configured MCP, CLI, or human-provided reference.

## Scope Rules

- Implement only the selected task; honor `file_scope` and `contract_files`.
- If `application_docs: true`, update only the human-facing docs triggered by the task.
- In team mode, claim before implementation and reconcile before state transitions.
- In solo governed mode, never work on or promote to `release_branch` without human instruction.

## Hard Stops

Stop when:

- task scope is unclear, or required FORGE docs, task source, auth, or operator identity are missing
- branch policy or task claim conflicts, or task state cannot be reconciled
- the task would exceed declared `file_scope` without justified expansion
- an integration-boundary change lacks the relevant contract file, or another active task owns it
- architecture or security uncertainty is unresolved
- checks fail without a user-approved exception
- a review gate fails or records `escalated` / `handoff-required`
- independent review is required and the same agent is being asked to complete it
- solo governed mode would merge or promote into `release_branch` without human instruction
- commit history would include AI attribution or agent branding

## Rationalizations To Reject

| Rationalization | FORGE response |
|---|---|
| "This is small enough to skip task state." | Small work still needs bounded scope and a checkpoint. |
| "I can touch nearby files while I am here." | Only selected task scope is allowed. |
| "I will update docs after code works." | Triggered docs and contracts move with the task. |
| "Gates can run at the end of the session." | Gates run per checkpoint, before the commit. |
| "The scanner will catch it." | Security uncertainty requires explicit review or escalation. |

## Evidence Required

- selected task id/issue; changed files and scope-expansion notes; validation run or blocker
- `gates:` outcomes for the checkpoint (critique, security, evaluation, memory)
- updated task source when state changes
- required docs/contracts/ADRs/XPDs when triggered; Conventional Commit (solo) or PR/MR-ready state (team)

On-demand references: `../references/checkpoint-output.md`, `../references/execution-modes.md`, `../references/team-mode.md`, `../references/repo-flavors.md`, `../references/application-docs.md`.
