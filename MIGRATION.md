# FORGE Skills Migration

Use this guide when a repository was already bootstrapped with an older version of the FORGE skill pack and you want to adopt newer rules without starting over.

## Principle

Do not delete and regenerate `docs/forge/` wholesale unless the project is still empty.

Prefer targeted updates that preserve:

- project-specific task lists
- architecture notes
- evaluation evidence
- memory history
- local conventions already captured by the team

## Adopting Coordination-Branch Team Mode

If the project already has `docs/forge/` and you want the newer team-mode claiming model:

1. Update `docs/forge/AI.md`
    - set `collaboration_mode: team`
    - set `task_source: local`, `github`, `gitlab`, or `external`
    - set `coordination_branch: forge-state` or your chosen branch
    - set `integration_branch: develop` or your chosen staging branch
    - set `release_branch: main` or your chosen promotion branch
    - set `ci_enforcement: enabled`

2. Update or create `docs/forge/TEAM.md`
   - add the coordination branch
   - add the claim publishing rule
   - add the branch/PR alignment rule
   - define the closeout contract so `implemented`, `integrated`, and `complete` are treated as separate checkpoints
   - define how claims are released when tasks reach `integrated` or `complete`

3. Update `docs/forge/TASKS.yaml`
   - allow team-mode statuses including `implemented` and `integrated`
   - add `claimed_by_email`, `agent`, and `claim_commit` to active and future tasks
   - add `claim_released_by` and `claim_released_at` for tasks that are already `integrated` or `complete`
   - ensure executable tasks have `file_scope`

4. Update or create `docs/forge/SETUP.md`
   - record merge semantics for integration and release promotion
   - record whether the closeout helper or a documented manual procedure is used before integration
   - record how release reconciliation moves tasks from `integrated` to `complete`

5. Create the coordination branch
   - for example: `forge-state`
   - publish the updated `TASKS.yaml` there before new claims begin

   Skip this step when `task_source` is `github` or `gitlab`; issue assignment and labels are the authoritative claim ledger.

6. Keep implementation on feature branches
   - claim first on the coordination branch
   - then implement on the task feature branch
   - treat the feature-branch copy of `TASKS.yaml` as informational only during implementation
   - before opening the feature PR, run `bash ci/scripts/verify-team-closeout.sh --task <task-id> --target integration` or the documented equivalent
   - merge feature branches into the integration branch first
   - when a task becomes `integrated`, record `claim_released_by` and `claim_released_at`
   - reconcile with `forge-state` when changing task state to `implemented`, `integrated`, or `complete`

## Adopting Contract-First Rules

For repos with OpenAPI, protobuf, GraphQL, generated clients, schemas, or other
shared interface files:

1. Add `repo_flavor: contract-first` to `docs/forge/AI.md`.
2. Add contract files and ownership rules to `docs/forge/ARCHITECTURE.md`.
3. Add `contract_files` to executable tasks that may touch the integration boundary.
4. Update `docs/forge/TEAM.md` with role split and sequencing rules when frontend/backend or service boundaries are shared.

## Refreshing Agent Surfaces

If a repo already has `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`,
`.github/copilot-instructions.md`, `.codex/hooks.json`, or `.windsurf/rules/`,
refresh only the FORGE routing lines. Preserve project-specific local rules.

## Installing Git Hooks On An Existing Repo

For repos that already have FORGE docs but did not install the local hooks:

```bash
bash scripts/install-forge-hooks.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-forge-hooks.ps1
```

The installer is idempotent. Any non-FORGE hook found at the same path is
backed up to `<name>.bak` before the FORGE hook is installed. Re-run safely
to upgrade. Solo-governed and team-full bootstraps run this automatically
from 1.3.0 onward; older repos can adopt it without re-bootstrapping.

## Adopting Application Docs

For repos that want a human-facing `docs/` tree (overview, architecture,
threat model, developer guide, interfaces, deployment, runbook, ADRs)
alongside the agent-facing `docs/forge/`:

1. Add `application_docs: true` to the `FORGE-config` block in `docs/forge/AI.md`.
2. Ask the installed `forge` skill to bootstrap the human-facing docs into
   the repo `docs/` directory. The default subset is profile-aware:
   - always: `tool-overview.md`, `developer-guide.md`, `adr/`
   - `solo-governed` and `team-full` add: `architecture-overview.md`,
     `interfaces-and-protocols.md`, `deployment-playbook.md`,
     `incident-runbook.md`
   - `security_profile: repo-fortress` and stronger add: `threat-model.md`
3. Fill `owners:` and `updated:` in each generated frontmatter.
4. Distinguish the two architecture docs:
   - `docs/forge/ARCHITECTURE.md` is **agent-facing** constraints and
     contract files.
   - `docs/architecture-overview.md` is the **human-facing** system
     explanation.
5. Tag tasks that represent significant architectural decisions with
   `task_type: architecture-decision` so `forge-execute-task` and
   `forge-evaluation` expect a new `docs/adr/NNNN-<slug>.md`.

The maintenance trigger map (which task types update which docs) lives in
the installed skill at `references/application-docs.md`.

## Adopting DevSecOps Gates

For repos that want stronger security enforcement:

1. Add `security_profile: repo-fortress`, `ci-security`, or `full-devsecops` to `docs/forge/AI.md`.
2. Update `docs/forge/SETUP.md` with the controls that are actually configured.
3. Add the relevant checklist sections to `docs/forge/SECURITY_CHECKLISTS.md`.
4. Record evidence for configured scans and gates in `docs/forge/EVALUATION.md`.
5. Treat missing expected controls as setup findings rather than passing them silently.

## How To Refresh Existing Docs With The Skill

Ask the installed `forge` skill to refresh only the affected governance files, for example:

```text
Use the forge skill and refresh the existing docs/forge team-mode files for the coordination-branch claiming model. Preserve current project-specific content and only update what is needed.
```

That should update the existing docs rather than regenerate unrelated files.
