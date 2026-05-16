---
name: forge-execute-task
description: Execute one bounded FORGE task from repository-local governance docs. Use when reading `docs/forge/` state, selecting the next incomplete task, enforcing task scope, checking alignment, implementing changes, and stopping on ambiguity or failed gates.
---

# FORGE Execute Task

Purpose: execute one governed FORGE task with minimal context.

## Use When

- the user asks to start, build, implement, execute, or continue governed work
- project-local FORGE docs or a configured issue tracker define bounded tasks
- a lifecycle alias such as `forge-build` routes here

## Do Not Use When

- repo is not bootstrapped and needs `forge-bootstrap`
- the user only wants review, security review, evaluation, release reconciliation, or planning
- task cannot be bounded to one checkpoint

## Default Reads

1. `docs/forge/CONTEXT.md` if present.
2. `docs/forge/AI.md`.
3. `docs/forge/TASKS.index.yaml` when present, otherwise `docs/forge/TASKS.yaml` or the configured issue tracker.
4. Exactly one selected task file or issue.
5. Files in task `file_scope`.

Do not read all FORGE docs or every task. Read `TEAM.md`, `ARCHITECTURE.md`, `MEMORY.md`, `SECURITY_CHECKLISTS.md`, `SETUP.md`, and `EVALUATION.md` only when required.

## Workflow

1. Confirm branch safety, worktree state, and project-local prerequisites.
2. Parse `AI.md` for `collaboration_mode`, `task_source`, `solo_branch_flow`, `repo_flavor`, `security_profile`, and context profile.
3. Select or claim exactly one task from the authoritative task source.
4. Read only that task's details.
5. Start with declared `file_scope`; if missing, inspect the smallest relevant index.
6. If implementation requires files outside `file_scope`, note why before expanding.
7. Check branch, team, architecture, contract, and security constraints.
8. Implement the smallest safe change.
9. Run relevant checks.
10. Update task state and evidence.
11. Commit if requested or required by project policy.
12. Stop unless the project explicitly allows continuing after checkpoint.

## Task Sources

- `local`: prefer `TASKS.index.yaml` plus `docs/forge/tasks/<id>.yaml`; fall back to `TASKS.yaml`.
- `github`: use GitHub Issues as authoritative state when configured and authenticated.
- `gitlab`: use GitLab Issues as authoritative state when configured and authenticated.
- `external`: use only the configured MCP, CLI, or human-provided reference.

Issue-backed tasks use issue assignment, labels, comments, and PR/MR links as the primary ledger. Repo-local task files are planning snapshots unless policy says otherwise.

## Scope Rules

- Implement only the selected task.
- Honor `file_scope`.
- Honor `contract_files` for APIs, schemas, wire formats, clients, and integration boundaries.
- If another active task owns a needed contract file, stop for sequencing.
- If `application_docs: true`, update only the human-facing docs triggered by the task.
- In team mode, claim before implementation and reconcile against the authoritative ledger before state transitions.
- In solo governed mode, do not work on `release_branch` or promote without explicit human instruction.

## Hard Stops

Stop when:

- task scope is unclear
- required FORGE docs or task source are missing
- authorization, authentication, or operator identity is missing
- branch policy or task claim conflicts
- the task would exceed declared `file_scope` without justified expansion
- an integration-boundary change lacks the relevant contract file
- another active task owns a required contract file
- architecture or security uncertainty is unresolved
- checks fail without a user-approved exception
- task state cannot be reconciled
- independent review is required and the same agent is being asked to complete it
- solo governed mode would merge or promote into `release_branch` without human instruction
- commit history would include AI attribution or agent branding

## Rationalizations To Reject

| Rationalization | FORGE response |
|---|---|
| "This is small enough to skip task state." | Small work still needs bounded scope and a checkpoint. |
| "I can touch nearby files while I am here." | Only selected task scope is allowed. |
| "I will update docs after code works." | Triggered docs and contracts move with the task. |
| "I can start the next task while tests run." | Next-task work waits for validation, state, evidence, and commit. |
| "The scanner will catch it." | Security uncertainty requires explicit review or escalation. |

## Evidence Required

- selected task id or issue
- changed files and scope-expansion notes, if any
- validation commands run or blocker
- updated task source when state changes
- required docs, contracts, ADRs, XPDs, or evaluation entries when triggered
- Conventional Commit for completed solo task work, or PR/MR-ready state in team mode

## On-Demand References

- branch and team policy: `../references/team-mode.md`
- repo flavor policy: `../references/repo-flavors.md`
- application doc triggers: `../references/application-docs.md`
- skill-pack rationale: `references/skill-pack-overview.md`
