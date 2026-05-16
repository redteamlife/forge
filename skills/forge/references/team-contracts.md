# FORGE Team Contracts

Use this reference when multiple people or agents split work across shared interfaces.

## Role Split

Record only the fields the project needs:

- engineering roles, for example backend, frontend, infrastructure, data, QA
- integration boundary, for example OpenAPI, protobuf, GraphQL, generated client, database migration, or message schema
- contract owners
- sequencing rules for shared interface files

## Contract Files

`contract_files` marks shared interface artifacts that must not drift from implementation.

If a task changes behavior across the boundary, update the contract artifact in the same PR/MR.

If another active task owns the same contract file, stop and resequence instead of creating competing contract changes.

## Shared Artifacts

- `EVALUATION.md` should use append-only task evidence.
- `MEMORY.md` should capture reusable lessons, not full PR narratives.
- `TEAM.md` should define only project-specific branch, claim, review, and CI policy.
- `SETUP.md` should record configured hooks, CI, branch protection, and closeout helper usage.
