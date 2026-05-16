---
name: forge-bootstrap
description: Bootstrap or migrate a repository into a FORGE skill-based workflow. Use when generating the initial `docs/forge/` files, reducing a document-heavy FORGE setup into a smaller skill-driven contract, or scaffolding the minimum governance files for a project.
---

# FORGE Bootstrap

Purpose: initialize the smallest project-local FORGE contract with low default context.

## Defaults

- Default `agent_context_profile: lite` unless explicitly selected otherwise.
- For enterprise, API, Bedrock, CI, non-interactive, or uncertain environments, use `lite`.
- Generate `docs/forge/CONTEXT.md`.
- Generate compact router-style `CLAUDE.md`, `AGENTS.md`, and always-on IDE rules.
- Prefer split task and checklist layouts for new `lite` and `standard` projects.
- Keep FORGE explicit. Agent surfaces remind and route.

Recognize these bootstrap options when the user asks for them in natural language or CLI-shaped text:

- context profile: `lite`, `standard`, or `full`
- no Claude includes
- split tasks
- split checklists
- split memory

FORGE does not require a shell CLI. Use the skill workflow and bundled scripts.

## Context Profiles

`lite`:

- no `@./docs/forge/` includes in `CLAUDE.md` or `AGENTS.md`
- read `AI.md`, `CONTEXT.md`, compact task index, one selected task, and task-relevant source only
- read `TEAM.md`, `ARCHITECTURE.md`, `MEMORY.md`, `SECURITY_CHECKLISTS.md`, `SETUP.md`, and `EVALUATION.md` only on demand

`standard`:

- may include only `@./docs/forge/AI.md`
- all other FORGE docs remain on demand

`full`:

- may include multiple selected FORGE docs
- label generated agent surfaces as high-context

## Workflow

1. Inspect repo shape, existing FORGE docs, existing agent surfaces, likely task source, and collaboration needs.
2. Choose bootstrap profile: `solo-simple`, `solo-governed`, or `team-full`.
3. Choose context profile. Default to `lite`.
4. Choose `task_source`: `local`, `github`, `gitlab`, or `external`.
5. Choose optional `repo_flavor` only when it changes behavior: `contract-first` or `tooling`.
6. Choose `security_profile`: `baseline`, `repo-fortress`, `ci-security`, or `full-devsecops`.
7. Generate only required docs and preserve project-specific existing content.
8. Generate `docs/forge/CONTEXT.md` using `<skill-root>/assets/scripts/forge_context_budget.py` when available.
9. Generate agent surfaces using `<skill-root>/assets/scripts/forge_generate_agent_surfaces.py` when available.
10. Run `<skill-root>/assets/scripts/forge_validate_context.py <repo>` when available.
11. For `solo-governed` and `team-full`, install FORGE hooks when the user wants local enforcement or the profile requires it.
12. Print a compact closeout with changed files and next setup step.

## Minimum Docs

Always create or refresh:

- `docs/forge/AI.md`
- `docs/forge/CONTEXT.md`
- task ledger: `TASKS.index.yaml` plus `docs/forge/tasks/` when split tasks are selected, otherwise `TASKS.yaml`
- selected root agent surfaces

Create only when relevant:

- `ARCHITECTURE.md` for design boundaries, interfaces, deployment, or cross-module behavior
- `TEAM.md` for multiple developers or agents, claims, branch policy, or reviewer routing
- `security-checklists/` or `SECURITY_CHECKLISTS.md` for checklist-based security review
- `MEMORY.index.yaml` plus `memory/`, or compatibility `MEMORY.md`, for reusable lessons
- `EVALUATION.md` for explicit completion gates
- `SETUP.md` for local hooks, hosted CI, branch protection, or onboarding
- `docs/` human-facing application docs only when `application_docs: true`
- `docs/forge/cross-project/` only on explicit cross-project requests

## Agent Surfaces

- `lite` `CLAUDE.md`: router text only; fail validation on include bombs.
- `standard` `CLAUDE.md`: may include `@./docs/forge/AI.md` only.
- `full` `CLAUDE.md`: may include selected bootstrapped docs and must say it is high-context.
- `AGENTS.md`, Cursor, Copilot, Windsurf, and Codex hooks should follow the same profile logic.
- Always-on surfaces should say what to read next; they should not inline project policy from large docs.

## Hard Stops

Stop when:

- bootstrap would overwrite project-specific docs without a migration path
- the user has not authorized team, CI, hook, or cross-project setup
- the selected task source cannot be identified and the choice changes generated state
- generated lite surfaces would auto-load large docs
- validation reports a lite include bomb

## Output

Read references only when needed:

- repo and doc minimums: `references/doc-minimums.md`
- team behavior: `references/team-mode.md`
- agent surfaces: `../references/agent-flavors.md`
- repo flavors: `../references/repo-flavors.md`
- DevSecOps gates: `../references/devsecops-gates.md`
- application docs: `../references/application-docs.md`
- cross-project coordination: `../references/cross-project.md`

Use `<skill-root>/assets/scripts/forge_migrate_context.py` for older projects when practical.
