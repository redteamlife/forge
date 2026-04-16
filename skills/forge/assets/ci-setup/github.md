# GitHub Setup

Use this when the project is hosted on GitHub and `ci_enforcement` should be enabled.

## Repo Files

- Copy the repository `ci/` directory into the target project.
- Copy `ci/workflows/forge-governance.yml` into `.github/workflows/`.

## Local Hooks

- Install `ci/hooks/commit-msg` into `.git/hooks/commit-msg`.
- Optionally install the provided `pre-push` hook if the project uses it.

## Branch Protection

For the integration branch:

- Require pull requests before merge.
- Require status checks to pass before merging.
- Add `FORGE Governance Checks` as a required check.
- Require branches to be up to date before merging.

For the release branch:

- Require pull requests before merge unless the team has a documented release automation path.
- Require status checks to pass before merging.
- Limit who can promote integrated work if the project needs stronger release control.
- Decide who runs the post-promotion release reconciliation step that moves tasks from `integrated` to `complete`.

For coordination-branch team mode:

- Consider protecting `forge-state` from casual direct pushes.
- If only automation or maintainers should update claim state directly, document that rule explicitly.
