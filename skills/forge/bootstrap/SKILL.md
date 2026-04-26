---
name: forge-bootstrap
description: Bootstrap or migrate a repository into a FORGE skill-based workflow. Use when generating the initial `docs/forge/` files, reducing a document-heavy FORGE setup into a smaller skill-driven contract, or scaffolding the minimum governance files for a project.
---

# FORGE Bootstrap

Use this skill to create or refresh the smallest viable project-local files needed by the FORGE skill pack.

## Goal

Generate lean project state, not a maximal document set.

Treat bootstrap as choosing an explicit setup profile, not as dumping generic templates.

Prefer these profiles:

- `solo-simple`: minimal repo-local governance for one operator working directly with per-task checkpoints
- `solo-governed`: one operator, but each governed task runs on its own task branch and the agent must not merge to `release_branch` without explicit human instruction
- `team-full`: multi-human or multi-agent coordination with claims, branch discipline, and full team-ready repo docs, followed by an explicit choice about copying repo agent surfaces and CI scaffolding

Prefer this minimum:

- `docs/forge/AI.md`
- `docs/forge/TASKS.yaml`
- `docs/forge/ARCHITECTURE.md` when architecture constraints materially matter
- `docs/forge/EVALUATION.md` when explicit completion gates are needed
- `docs/forge/MEMORY.md` when the project benefits from reusable lessons
- `docs/forge/TEAM.md` when multiple developers or agents will work in parallel
- `docs/forge/SECURITY_CHECKLISTS.md` when `forge-security-review` will be used, composed from the relevant files in `assets/security-checklists/`
- `docs/forge/SETUP.md` when local hooks or hosted CI enforcement should be tracked explicitly
- `AGENTS.md` at repo root — always; instructs OpenAI Codex and other agents to read the forge docs before working
- `CLAUDE.md` at repo root — always; uses `@./docs/forge/` includes so Claude Code auto-loads the forge docs on every session

Add more docs only if the project's risk, complexity, or compliance needs justify them.

## Workflow

1. Read `references/doc-minimums.md`.
2. Read `references/team-mode.md` when the repo will be shared by multiple developers or agents.
3. Inspect the repo shape and infer likely language, framework, and risk profile.
4. Determine the bootstrap profile from explicit user intent when possible.
5. If the user wants bootstrap but does not specify the profile and the choice would materially change branch, CI, or collaboration behavior, ask one compact question that offers `solo-simple`, `solo-governed`, or `team-full`.
6. Propose or generate the smallest set of governance docs that supports the chosen profile.
7. If the repo already has FORGE docs, prefer targeted updates over full regeneration so project-specific edits are preserved.
8. In `solo-governed`, emit explicit config and policy cues, not only narrative prose:
   - set `collaboration_mode: solo`
   - set `solo_branch_flow: task-branches`
   - keep `release_branch` as the real protected branch, for example `main`
   - do not use wildcard branch patterns such as `task/*` as `integration_branch`
   - do not imply a team-style coordination branch unless the project explicitly wants one
9. In `solo-governed`, include task-branch policy and an explicit rule that the agent must not merge into `release_branch` without human instruction.
10. In `team-full`, include coordination-branch, task-claiming, branch policy, and integration closeout rules from the start rather than adding them later.
11. When generating `docs/forge/SECURITY_CHECKLISTS.md`, select only the relevant shared checklist assets rather than copying every possible checklist into the project.
12. In `team-full`, bootstrap the full team-ready repo docs first.
13. After bootstrapping `team-full`, ask one explicit follow-up question: whether the user wants the agent to also copy the reusable agent-surface files and CI scaffolding into the target repo now, or leave those steps manual.
14. If the user chooses manual setup for those repo-level assets, generate explicit next-step guidance instead of copying them.
15. If the project uses GitHub or GitLab, generate explicit next-step setup guidance for local hooks, CI assets, and branch protection rather than assuming the team already knows how to wire them.
16. Keep templates concise and project-specific.
17. After all `docs/forge/` files are written, generate `AGENTS.md` at the repo root. List only the docs that were actually bootstrapped, in reading order, with a one-line description of each. Use the repo directory name as the title. Instruct the agent to read them before doing any work.
18. After writing `AGENTS.md`, generate `CLAUDE.md` at the repo root. Use `@./docs/forge/<file>` include syntax for each bootstrapped doc in the same reading order. Add a one-line repo title heading above the includes.
19. Do not generate application code.

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
  - `Changed: <docs created or updated, including AGENTS.md and CLAUDE.md>.`
  - `Next: <next task or setup step>.`
- Do not explain the purpose of every generated file unless the user asks.
