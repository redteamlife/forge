# FORGE Validators

Read this only when configuring or troubleshooting CI.

## Scripts

- `validate-commit-format.sh`: validates Conventional Commit shape and FORGE trailers.
- `validate-task-state.sh`: checks task status from `FORGE-task` trailers against the configured local task ledger.
- `validate-team-task-metadata.sh`: requires team claim, branch, file-scope, and release metadata.
- `validate-file-scope.sh`: checks changed files against task `file_scope`.
- `validate-evidence-artifacts.sh`: checks evaluation and memory artifacts when policy requires them.
- `validate-evaluation-currency.sh`: requires task-state transitions and evaluation evidence in the same commit.
- `validate-memory-bounds.sh`: keeps `MEMORY.md` within declared bounds.
- `validate-security-profile.sh`: verifies claimed security controls have setup evidence.
- `verify-team-closeout.sh`: local helper for task-branch closeout before integration or release.

## Task Ledgers

Local task validators use `forge_task_resolver.py`:

1. Prefer `docs/forge/TASKS.index.yaml`.
2. Load the selected `docs/forge/tasks/<id>.yaml` when referenced.
3. Fall back to `docs/forge/TASKS.yaml`.

Issue-backed task sources should validate assignment, labels, branch, and PR/MR links through the hosting platform.

## Team Mode

When `collaboration_mode: team`, CI expects:

- `ci_enforcement: enabled`
- task `file_scope`
- claim metadata
- branch alignment
- claim release metadata for `integrated` or `complete` tasks

PRs targeting `integration_branch` require task status `implemented`, `integrated`, or `complete`.

PRs targeting `release_branch` require task status `integrated` or `complete`.
