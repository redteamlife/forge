# Team Workflow

Use this file only when multiple developers or agents work in the same repository.

## Branch Policy

- Coordination branch: `forge-state`
- Integration branch: `develop`
- Release branch: `main`
- Task source: `local`
- Work on feature branches only.
- Branch naming pattern: `<task-id>/<actor>`
- Do not implement governed tasks directly on protected branches.

## Task Claiming

- Fetch the authoritative task source before claiming.
- Claim one task before implementation.
- For `task_source: local`, claim in the configured local task ledger and push on the coordination branch.
- For `task_source: github` or `gitlab`, claim through issue assignment and labels.
- For `task_source: external`, use the configured tracker workflow.
- Record `claimed_by`, `claimed_by_email`, `agent`, `claimed_at`, `claim_commit`, and `branch`.
- Do not work a task already claimed by another actor.
- Derive owner identity from project policy or local git config.

## Task Ledger Semantics

- `forge-state` is authoritative only for `task_source: local`.
- Issue trackers are authoritative for issue-backed task sources.
- Local task files on feature branches are informational during implementation.
- Reconcile before moving a task to `implemented`, `integrated`, or `complete`.

## File Scope

- Every executable team task must declare `file_scope`.
- If active tasks overlap materially in `file_scope`, resequence or split them.
- Shared interface files belong in `contract_files`.

## Integration Flow

- Feature branches open PRs/MRs into the integration branch.
- `implemented`: task branch is committed and ready for review.
- `integrated`: integration branch accepted the work and the active claim was released.
- `complete`: release branch or explicit team policy accepted the work.
- Do not target the release branch directly from task branches.
- Delete merged task branches unless project policy keeps them briefly.

## Review And Merge

- Complete critique, required security review, and evaluation before merge.
- Record reviewer and validation evidence in `docs/forge/EVALUATION.md`.

## Task Closeout

- Record claim release metadata when a task reaches `integrated` or `complete`.
- Record branch protection and CI setup status in `docs/forge/SETUP.md`.

## Role Split (example)

Replace this with the real split for your project. The key idea: name the
**integration seam** so parallel lanes can work without stepping on each
other.

- **Lane A — Backend / Infra**: API, DB, scheduler, jobs, crypto, CI.
- **Lane B — Frontend / UX**: UI, design system, live state, forms, charts.
- **Integration seam**: `openapi.yaml` (or `schema.proto`, `schema.graphql`).
  Lock contract changes there before touching either side; both lanes
  regenerate from it.

Record contract files in `docs/forge/ARCHITECTURE.md` under
"Contract Artifacts" and on individual tasks under `contract_files`.

Detailed optional procedures may live under `docs/forge/team/`.
