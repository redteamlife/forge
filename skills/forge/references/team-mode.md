# FORGE Team Mode

Use this reference only when multiple developers or agents work in the same repo.

## Minimum Contract

- Work from feature branches, never shared long-lived branches.
- Claim one task before editing implementation files.
- Publish claims in the configured task source.
- Require explicit `file_scope` for executable tasks.
- Record actor and branch on the task or issue.
- Use PR/MR-based merge with CI enforcement.

## Task Source

`task_source` in `docs/forge/AI.md` selects the authoritative ledger:

- `local`: `TASKS.index.yaml` plus task files, or legacy `TASKS.yaml`, published through the coordination branch
- `github`: GitHub Issues, using assignment and labels
- `gitlab`: GitLab Issues, using assignment and labels
- `external`: Jira, Linear, or another tracker through MCP, CLI, or human workflow

For serious GitHub or GitLab multi-agent work, prefer issue-backed coordination. The hosting platform is the lock and audit ledger.

## Required Task Fields

Executable tasks should include:

- `status`
- `file_scope`
- `claimed_by`
- `claimed_by_email`
- `agent`
- `claimed_at`
- `claim_commit`
- `branch`
- `claim_released_by` and `claim_released_at` after integration or completion
- `contract_files` when shared interface artifacts are involved
- issue or PR/MR links when an external tracker is authoritative

## Minimum Workflow

1. Fetch the authoritative task source.
2. Claim one task and publish the claim.
3. Create or update the recorded feature branch.
4. Implement only within declared `file_scope` and contract-boundary rules.
5. Treat non-authoritative task snapshots as informational while implementing.
6. Run critique, security review when needed, and evaluation.
7. Reconcile with the authoritative task source before state transitions.
8. Open PR/MR to the integration branch.
9. Merge only after CI and required review pass.
10. Release/promote only through project policy and recorded acceptance.

## Read More Only When Needed

- claiming, identity, and coordination branch details: `team-claiming.md`
- integration, release, and closeout details: `team-release.md`
- GitHub, GitLab, and external tracker details: `team-trackers.md`
- role split and contract boundary details: `team-contracts.md`
