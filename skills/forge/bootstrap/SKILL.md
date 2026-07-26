---
name: forge-bootstrap
description: Bootstrap or migrate a repository into a FORGE skill-based workflow. Use when generating the initial `docs/forge/` files, reducing a document-heavy FORGE setup into a smaller skill-driven contract, or scaffolding the minimum governance files for a project.
---

# FORGE Bootstrap

Purpose: initialize the smallest project-local FORGE contract with low default context.

## Defaults

- Default `agent_context_profile: lite`. Use `lite` for enterprise, API, Bedrock, CI, non-interactive, or uncertain environments.
- Generate `docs/forge/CONTEXT.md`, compact router-style `CLAUDE.md`/`AGENTS.md`, and always-on IDE rules by default.
- For `solo-governed`/`team-full`, prefer the narrative `AGENTS.md` form (see `references/scaffolding.md`).
- Prefer split task and checklist layouts for new `lite`/`standard` projects.
- Keep FORGE explicit. Agent surfaces remind and route.

Recognize these bootstrap options in natural language or CLI-shaped text: context profile (`lite`/`standard`/`full`), no Claude includes, split tasks, split checklists, split memory, narrative front door, contract-first scaffold, quality CI workflow. The last three route to `references/scaffolding.md`.

## Context Profiles

- `lite`: no `@./docs/forge/` includes in `CLAUDE.md` or `AGENTS.md`. Auto-read only `AI.md`, `CONTEXT.md`, task index, one selected task, and task-relevant source. Large docs are on demand.
- `standard`: may include only `@./docs/forge/AI.md`; everything else on demand.
- `full`: may include multiple selected FORGE docs; label surfaces high-context.

## Workflow

1. Inspect repo shape, existing FORGE docs, existing agent surfaces, likely task source, and collaboration needs.
2. Choose bootstrap profile (`solo-simple`/`solo-governed`/`team-full`), context profile (default `lite`), `task_source` (`local`/`github`/`gitlab`/`external`), optional `repo_flavor` (`contract-first`/`tooling` only when it changes behavior), and `security_profile` (`baseline`/`repo-fortress`/`ci-security`/`full-devsecops`).
3. Generate only required docs; preserve project-specific existing content.
4. Generate `docs/forge/CONTEXT.md` (`forge_context_budget.py`) and agent surfaces (`forge_generate_agent_surfaces.py`). For `solo-governed`/`team-full`, follow `references/scaffolding.md` (narrative AGENTS.md + scoped Cursor rules).
5. For `repo_flavor: contract-first`, scaffold the contract per `references/scaffolding.md`.
6. For `team-full` with `ci_enforcement: enabled`, copy the quality workflow per `references/scaffolding.md`.
7. Run `forge_validate_context.py <repo>`. For `solo-governed`/`team-full`, install FORGE hooks when the user wants local enforcement.
8. Print a compact closeout with changed files and next setup step.

## Minimum Docs

Always create or refresh: `docs/forge/AI.md`, `docs/forge/CONTEXT.md`, the task ledger (`TASKS.index.yaml` plus `docs/forge/tasks/` when split, otherwise `TASKS.yaml`), and the selected root agent surfaces.

Create only when relevant: `ARCHITECTURE.md` (design boundaries), `TEAM.md` (multi-actor), security checklists (copy `general.md` plus relevant surfaces from `<skill-root>/assets/security-checklists/`, or compose a monolithic file with real items — never an empty index; repair index-only scaffolds on refresh per `references/doc-minimums.md`), `MEMORY.index.yaml` plus `memory/` (or `MEMORY.md`), `EVALUATION.md` (gates), `SETUP.md` (enforcement/onboarding), `docs/` human-facing docs when `application_docs: true`, and `docs/forge/cross-project/` only on explicit request.

## Agent Surfaces

- `lite` `CLAUDE.md`: router text only; fail validation on include bombs.
- `standard` `CLAUDE.md`: may include `@./docs/forge/AI.md` only.
- `full` `CLAUDE.md`: may include selected docs; surface must say it is high-context.
- `AGENTS.md` may be narrative even when `CLAUDE.md` is a router; narrative must not include `@docs/forge/*` in lite mode.
- Prefer scoped Cursor rule files over one large rule file (`references/scaffolding.md`).
- Cursor, Copilot, Windsurf, and Codex hooks follow the same profile logic.
- Always-on surfaces route; they do not inline policy from large docs.

## Hard Stops

Stop when bootstrap would overwrite project-specific docs without a migration path, the user has not authorized team/CI/hook/cross-project setup, the selected task source cannot be identified and the choice changes generated state, generated lite surfaces would auto-load large docs, or validation reports a lite include bomb.

## Output

Read references only when needed: `references/doc-minimums.md` (doc minimums), `references/scaffolding.md` (narrative AGENTS.md, contract-first, quality CI), `references/team-mode.md` (team behavior), `../references/agent-flavors.md`, `../references/repo-flavors.md`, `../references/devsecops-gates.md`, `../references/application-docs.md`, `../references/cross-project.md`.

Use `<skill-root>/assets/scripts/forge_migrate_context.py` for older projects when practical.
