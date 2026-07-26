# Bootstrap Doc Minimums

Use the smallest project-local governance set that still supports bounded execution.

## Solo Default

Required:

- `docs/forge/AI.md`
- `docs/forge/CONTEXT.md`
- task ledger: `TASKS.index.yaml` plus `docs/forge/tasks/`, or legacy `TASKS.yaml`

Recommended:

- `docs/forge/ARCHITECTURE.md` when architecture constraints materially matter
- `docs/forge/EVALUATION.md` when explicit completion gates are needed
- `docs/forge/MEMORY.md` when the project benefits from reusable lessons
- root `AGENTS.md` and `CLAUDE.md` when the repo should remind agents how to route into FORGE

Use this for `solo-simple`.

## Solo Governed

Use the solo-governed profile when one operator still wants branch discipline and human-controlled merges.

Required:

- `docs/forge/AI.md`
- `docs/forge/CONTEXT.md`
- task ledger: `TASKS.index.yaml` plus `docs/forge/tasks/`, or legacy `TASKS.yaml`

Recommended:

- `docs/forge/ARCHITECTURE.md` when architecture constraints materially matter
- `docs/forge/EVALUATION.md` when explicit completion gates are needed
- `docs/forge/MEMORY.md` when the project benefits from reusable lessons
- `docs/forge/SETUP.md` when branch protection or human review handoff needs to be recorded
- root `AGENTS.md` and `CLAUDE.md` when the repo should remind agents how to route into FORGE

Additional expectations:

- set `collaboration_mode: solo`
- set `solo_branch_flow: task-branches`
- keep `release_branch` as the real protected branch, usually `main`
- keep `integration_branch` equal to the release branch or omit any special integration flow unless the project truly has one
- work from task branches rather than directly from `release_branch`
- do not use wildcard branch patterns such as `task/*` as `integration_branch`
- do not merge into `release_branch` without explicit human instruction

## Security Checklists

When checklist-driven security review is enabled (any bootstrap that creates a checklist surface, and always for `repo-fortress`, `ci-security`, or `full-devsecops`):

- prefer the split layout `docs/forge/security-checklists/` for new `lite` and `standard` projects
- always copy `general.md` from `<skill-root>/assets/security-checklists/`
- copy only the surface checklists relevant to the project (for example `api.md`, `frontend.md`, `data-storage.md`); copying the full modular set is acceptable for multi-surface applications because agents load only task-relevant files
- write the `SECURITY_CHECKLISTS.md` index template only alongside the split directory, never by itself
- if the project prefers a single monolithic `SECURITY_CHECKLISTS.md`, compose it from the same assets with real `- [ ]` items (General plus relevant surfaces); never leave an index with no split directory and no items

For `repo-fortress`, `ci-security`, and `full-devsecops`, also offer the matching provider assets (workflows under `<skill-root>/assets/ci/workflows/security/` or `assets/ci/gitlab/security.gitlab-ci.yml`, plus `SECURITY.md`/`dependabot.yml`/`CODEOWNERS` templates) per `assets/ci-setup/github.md` or `assets/ci-setup/gitlab.md`. Copy only what the profile calls for; record enabled controls in `SETUP.md` and never record a control that is not actually on.

Repair and refresh:

- if an existing repo has `SECURITY_CHECKLISTS.md` referencing a missing `security-checklists/` directory (an index-only scaffold), repair by copying `general.md` plus relevant surface checklists into `docs/forge/security-checklists/`
- preserve project-specific checklist additions and local security decisions; never overwrite them silently
- report exactly which checklist files were added or left untouched in the closeout

## Team Default

Add these from the start when multiple developers or agents will work in parallel:

- `docs/forge/TEAM.md`
- `docs/forge/security-checklists/` or compatibility `SECURITY_CHECKLISTS.md`
- explicit `file_scope` on executable tasks
- task claim metadata in the configured task source
- copy repo agent-surface files when the user wants persistent repo reminders
- copy CI assets when the user wants hosted enforcement from the start
- add contract files, role split, and integration-boundary rules when `repo_flavor: contract-first`
- add issue/MR or issue/PR traceability when `task_source` is GitHub, GitLab, or external
- generate the human-facing `docs/` tree (overview, developer guide, ADRs, plus the profile-appropriate subset of architecture, threat model, interfaces, deployment, runbook) when `application_docs: true`
