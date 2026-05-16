# FORGE Team Release

Use this reference for integration, release, and closeout checkpoints.

## State Meanings

- `implemented`: feature branch contains task work, task-scoped Conventional Commit exists, and the branch is ready for review.
- `integrated`: feature branch was accepted into the integration branch and the active claim was released.
- `complete`: integrated work was accepted on the release branch or otherwise formally accepted by explicit team policy.

Do not treat work on a feature branch as completion by itself.

## Release Reconciliation

Use one of these signals before moving a task to `complete`:

- human confirms promotion or formal acceptance
- release PR/MR into `release_branch` is merged and recorded
- fetched `release_branch` contains the task merge or release commit

If no signal is available, leave the task as `integrated`.

## Branch Roles

- `coordination_branch`: local governance state and task ledger when `task_source: local`
- `integration_branch`: staging branch where feature work converges
- `release_branch`: production or release branch

Agents should not target the release branch directly from feature branches.

Merged feature branches should be deleted after integration acceptance unless project policy keeps them briefly.

## Closeout Evidence

When a task reaches `integrated` or `complete`, record:

- `claim_released_by`
- `claim_released_at`
- PR/MR link or release evidence when available
- release PR/MR or release commit when applicable

Run the closeout helper or an equivalent validation before opening or merging PR/MR work.
