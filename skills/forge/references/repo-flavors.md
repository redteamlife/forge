# FORGE Repo Flavors

Use this reference only when the repository shape changes which FORGE docs or
checks should be loaded.

`repo_flavor` is optional. Most projects do not need it. Set it only when one
of the flavors below materially changes generated docs or task-selection
behavior. The default repo shape (a normal local or issue-backed project) is
captured by `task_source` alone.

## Contract-First

Use when shared interface artifacts define the implementation boundary.

Examples:

- OpenAPI or AsyncAPI
- protobuf
- GraphQL schema
- generated client configuration
- database migration or data contract files

Rules:

- declare `contract_files` in `ARCHITECTURE.md` or executable task metadata
- API, client, schema, wire-format, and integration-boundary changes must update
  the relevant contract in the same task, PR, or MR
- if another active task owns the required contract file, stop for sequencing

Contract-first is repo-local by default. When the contract owner and consumers
span multiple repositories, use `forge-cross-project` in addition to this
flavor rather than overloading `repo_flavor`.

## Cross-Project Coordination

Cross-project coordination is an opt-in workflow, not a `repo_flavor` value.
Use it when multiple repositories need shared authority, XPDs, inbox proposals,
or peer/downstream review gates for authority-owned contracts.

- keep repo-local work governed by the configured `task_source`
- keep cross-project state under `docs/forge/cross-project/` in the authority repo
- record only compact routing hints in peer or downstream agent surfaces
- do not apply cross-project rules to normal `team-full` repos unless the user
  explicitly asks for them

## Tooling

Use for private/public tool repositories and release-surface publishing.

- read `forge-tool-workflow`
- keep private planning/evaluation/memory in the development repo
- publish only intended release artifacts to the public repo
