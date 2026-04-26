# GitLab Setup

Use this when the project is hosted on GitLab and `ci_enforcement` should be enabled.

## Repo Files

- Copy the repository `ci/` directory into the target project.
- Translate or wrap the FORGE validation scripts in `.gitlab-ci.yml` jobs.

## Local Hooks

- Install `ci/hooks/pre-commit` into `.git/hooks/pre-commit`.
- Install `ci/hooks/commit-msg` into `.git/hooks/commit-msg`.
- Optionally install the provided `pre-push` hook if the project uses it.

## Task Source

- For `task_source: gitlab`, use issue assignment and labels as the team claim ledger.
- Keep `docs/forge/TASKS.yaml` only as a planning snapshot when GitLab Issues are authoritative.

## Protected Branches And Merge Rules

For the integration branch:

- Require merge requests instead of direct pushes.
- Require the FORGE validation pipeline to pass before merge.
- Require the source branch to be up to date with target policy as appropriate.
- Document the merge semantics the repo uses for integration closeout, for example merge commit, squash merge, or fast-forward-only.
- Run `bash ci/scripts/verify-team-closeout.sh --task <task-id> --target integration` before opening the merge request when practical.

For the release branch:

- Require merge requests or a documented release automation path instead of ad hoc direct pushes.
- Require the release validation pipeline to pass before merge if the project uses one.
- Decide who runs the post-promotion release reconciliation step that moves tasks from `integrated` to `complete`.
- Record how claim release metadata is written when tasks move from active branch work to integrated or complete state.

For coordination-branch team mode:

- Consider protecting `forge-state` from casual direct pushes.
- Document who is allowed to publish task claims and how conflicts are resolved.
