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

## How To Refresh Existing Docs With The Skill

Ask the installed `forge` skill to refresh only the affected governance files, for example:

```text
Use the forge skill and refresh the existing docs/forge team-mode files for the coordination-branch claiming model. Preserve current project-specific content and only update what is needed.
```

That should update the existing docs rather than regenerate unrelated files.
