---
name: forge-bootstrap
description: Bootstrap or migrate a repository into a FORGE skill-based workflow. Use when generating the initial `docs/forge/` files, reducing a document-heavy FORGE setup into a smaller skill-driven contract, or scaffolding the minimum governance files for a project.
---

# FORGE Bootstrap

Use this skill to create or refresh the smallest viable project-local files needed by the FORGE skill pack.

## Goal

Generate lean project state, not a maximal document set.

Prefer this minimum:

- `docs/forge/AI.md`
- `docs/forge/TASKS.yaml`
- `docs/forge/ARCHITECTURE.md` when architecture constraints materially matter
- `docs/forge/EVALUATION.md` when explicit completion gates are needed
- `docs/forge/MEMORY.md` when the project benefits from reusable lessons
- `docs/forge/TEAM.md` when multiple developers or agents will work in parallel
- `docs/forge/SECURITY_CHECKLISTS.md` when `forge-security-review` will be used, composed from the relevant files in `assets/security-checklists/`
- `docs/forge/SETUP.md` when local hooks or hosted CI enforcement should be tracked explicitly

Add more docs only if the project's risk, complexity, or compliance needs justify them.

## Workflow

1. Read `references/doc-minimums.md`.
2. Read `references/team-mode.md` when the repo will be shared by multiple developers or agents.
3. Inspect the repo shape and infer likely language, framework, and risk profile.
4. Propose or generate the smallest set of governance docs that supports bounded execution.
5. If the repo already has FORGE docs, prefer targeted updates over full regeneration so project-specific edits are preserved.
6. In team mode, include coordination-branch, task-claiming, and branch policy docs from the start rather than adding them later.
7. When generating `docs/forge/SECURITY_CHECKLISTS.md`, select only the relevant shared checklist assets rather than copying every possible checklist into the project.
8. If the project uses GitHub or GitLab, generate explicit next-step setup guidance for local hooks, CI assets, and branch protection rather than assuming the team already knows how to wire them.
9. Keep templates concise and project-specific.
10. Do not generate application code.

## Output Style

- Favor short, high-signal docs over exhaustive boilerplate.
- Preserve deterministic headings and field names.
- Keep instructions compatible with both skill-aware and document-first agents.
- Generate only the docs the project actually needs; do not inflate the repo with optional governance files by default.
- Keep generated narrative compact and factual so future sessions do not pay token cost for unnecessary prose.
- Do not narrate routine inspection or planning steps such as "I'm checking" or "I have enough context" unless a blocker or scope decision appears.
- Do not echo generated file contents back into chat unless the user asked to review them.
- Bootstrap closeout should be compact:
  - `Done: <what was bootstrapped>.`
  - `Changed: <docs created or updated>.`
  - `Next: <next task or setup step>.`
- Do not explain the purpose of every generated file unless the user asks.
