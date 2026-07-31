---
name: forge-bootstrap
description: Bootstrap or migrate a repository into a FORGE skill-based workflow. Use when generating the initial `docs/forge/` files, reducing a document-heavy FORGE setup into a smaller skill-driven contract, or scaffolding the minimum governance files for a project.
---

# FORGE Bootstrap

Purpose: initialize the smallest project-local FORGE contract with low default context.

## Defaults

- Default `agent_context_profile: lite` (always for enterprise, API, CI, non-interactive, or uncertain environments).
- Generate `CONTEXT.md`, router-style `CLAUDE.md`/`AGENTS.md`, and always-on IDE rules by default.
- For governed profiles, prefer the narrative `AGENTS.md` form (`references/scaffolding.md`).
- Prefer split task and checklist layouts for new `lite`/`standard` projects.
- Keep FORGE explicit. Agent surfaces remind and route.

## Workflow

1. Inspect repo shape, existing FORGE docs, existing agent surfaces, likely task source, and collaboration needs.
2. Elicit setup by presenting each choice as a menu of its available options with one-line descriptions and the recommended default marked — profile, context profile, `task_source`, `security_profile`, `activation_mode`, `application_docs`, optional `repo_flavor`, and clean-main for governed profiles. Do not ask open-ended questions; the user may not know the options. Detect first, ask what you cannot infer, use the harness's multiple-choice UI when available, and confirm the resulting `FORGE-config`. Skip only when the user supplied the config or asked for defaults (then state the defaults). Full catalog: `references/setup-interview.md`.
3. Generate only required docs; preserve existing content. Seed `.gitignore` from `assets/templates/gitignore.starter` (append missing entries; never overwrite).
4. Generate `CONTEXT.md` (`forge_context_budget.py`) and agent surfaces (`forge_generate_agent_surfaces.py`). Governed profiles: see `references/scaffolding.md` (narrative AGENTS.md + scoped Cursor rules).
5. For `repo_flavor: contract-first`, scaffold the contract per `references/scaffolding.md`.
6. For `team-full` + `ci_enforcement`, copy the quality workflow (`references/scaffolding.md`).
7. Run `forge_validate_context.py <repo>`. For `solo-governed`/`team-full`, install FORGE hooks by default unless the user opts out.
8. Print a compact closeout with changed files and next step.

## Minimum Docs

Always create or refresh: `docs/forge/AI.md`, `docs/forge/CONTEXT.md`, the task ledger (`TASKS.index.yaml` plus `docs/forge/tasks/` when split, otherwise `TASKS.yaml`), and the selected root agent surfaces.

Create only when relevant: `ARCHITECTURE.md` (design boundaries), `TEAM.md` (multi-actor), security checklists (copy `general.md` plus relevant surfaces from `<skill-root>/assets/security-checklists/`, or compose a monolithic file with real items — never an empty index; repair index-only scaffolds on refresh per `references/doc-minimums.md`), `MEMORY.index.yaml` plus `memory/` (or `MEMORY.md`), `EVALUATION.md` (gates), `SETUP.md` (enforcement/onboarding), `docs/` human-facing docs when `application_docs: true`, and `docs/forge/cross-project/` only on explicit request.

## Agent Surfaces

- `lite` `CLAUDE.md`: router text only; fail validation on include bombs.
- `standard` `CLAUDE.md`: may include `@./docs/forge/AI.md` only.
- `full` `CLAUDE.md`: may include selected docs; surface must say it is high-context.
- `AGENTS.md` may be narrative even when `CLAUDE.md` is a router; narrative must not include `@docs/forge/*` in lite mode.
- Prefer scoped Cursor rule files over one large rule file (`references/scaffolding.md`).
- Other IDE hooks follow the same profile logic.
- Always-on surfaces route; they do not inline policy from large docs.

## Hard Stops

Stop when bootstrap would overwrite project-specific docs without a migration path, the user has not authorized team/CI/hook/cross-project setup, the selected task source cannot be identified and the choice changes generated state, or generated lite surfaces would auto-load large docs or fail include-bomb validation.

## Output

Read references only when needed: `references/doc-minimums.md`, `references/scaffolding.md`, `references/team-mode.md`, `../references/agent-flavors.md`, `../references/repo-flavors.md`, `../references/devsecops-gates.md`, `../references/application-docs.md`, `../references/cross-project.md`.

Use `<skill-root>/assets/scripts/forge_migrate_context.py` for older projects.
