# FORGE Team Trackers

Use this reference when GitHub, GitLab, Jira, Linear, or another tracker is the task ledger.

## GitHub And GitLab

For `task_source: github` or `task_source: gitlab`:

- issue assignment is the primary claim
- labels represent task state where project policy defines them
- comments can record branch and PR/MR links
- repo-local task files are planning snapshots unless project policy says otherwise
- validate issue assignment, labels, branch, and PR/MR links before state transitions

Prefer issue-backed coordination for serious multi-agent work on hosted repos.

## External Trackers

For `task_source: external`, use only the configured MCP, CLI, or human-provided reference.

Do not invent repo-local tasks as authoritative state.

## Token And Identity Safety

Use least privilege that still supports project policy:

- read-only project/service tokens for state verification
- human account or user-scoped token when assignment means human ownership
- bot assignment only when policy explicitly permits bot ownership
