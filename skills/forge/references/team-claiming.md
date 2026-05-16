# FORGE Team Claiming

Use this reference for task claims, identity, and local coordination branches.

## Claim Protocol

1. Fetch the latest authoritative task source before selecting work.
2. Select only a task whose dependencies are complete and whose latest shared state is unclaimed.
3. For `task_source: local`, record actor identity, email, agent/runtime, and feature branch in the local task ledger.
4. Commit and push the local claim to the coordination branch before implementation starts.
5. For issue-backed task sources, assign the issue, add an `in-progress` label, and comment with the branch when useful.
6. If another actor holds the claim, do not proceed.
7. If `file_scope` overlaps heavily with another active task, stop and split or resequence.
8. If claim publication fails because state changed, refresh and retry from latest state.

## Coordination Branch

Use a shared branch such as `forge-state` only when `task_source: local`.

- local task claims are published there first
- `forge-state` is the authoritative local task ledger
- feature branches carry implementation work
- feature-branch task snapshots are informational and may be stale
- fetch the coordination branch before claiming or transitioning state

## Identity

Claims should identify the human operator, not only the agent product.

- `claimed_by`: project policy or `git config user.name`
- `claimed_by_email`: `git config user.email`
- `agent`: runtime such as `codex` or `claude`

If identity cannot be determined, stop instead of inventing a placeholder.

## Reconciliation

Reconcile against the authoritative task source:

- before claiming
- before moving a task to `implemented`, `integrated`, or `complete`
- when resolving claim conflicts or blocked transitions

Ordinary feature-branch ledger drift is expected and should not block implementation by itself.
