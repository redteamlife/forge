# GitHub Setup

Use this when the project is hosted on GitHub and `ci_enforcement` should be enabled.

## Repo Files

- Copy the FORGE skill's bundled `assets/ci/` directory into the target project as `ci/` (e.g. `cp -R <skill-root>/assets/ci ./ci`, where `<skill-root>` is the installed FORGE skill directory such as `~/.claude/skills/forge`).
- Copy `ci/workflows/forge-governance.yml` from the just-copied `ci/` tree into `.github/workflows/`.

## Local Hooks

- Run `bash <skill-root>/assets/scripts/install-forge-hooks.sh` (or `powershell -File <skill-root>/assets/scripts/install-forge-hooks.ps1` on Windows) against the target repo to install `pre-commit`, `commit-msg`, and `pre-push` hooks idempotently from the skill's bundled `assets/ci/hooks/`.
- Or install manually: copy `ci/hooks/pre-commit` into `.git/hooks/pre-commit` and `ci/hooks/commit-msg` into `.git/hooks/commit-msg` (and optionally `pre-push`) after the `ci/` directory is in place.
- Alternative: `git config core.hooksPath ci/hooks` makes the committed hooks authoritative so updates travel with the repo. Trade-offs: still one `git config` per clone, and it disables everything in `.git/hooks/`. Either way, hooks are advisory — CI (the governance workflow plus `release-branch-guard.yml` for clean-main repos) is the durable backstop.

## Task Source

- For `task_source: github`, use issue assignment and labels as the team claim ledger.
- Keep local task files only as planning snapshots when GitHub Issues are authoritative.
- Prefer read-only tokens for issue-state checks.
- Use a human account or user-scoped token for assignment when assignee means engineer ownership.
- Link each PR to the issue it closes or advances.

## Security Profile Assets

Copy only the assets the configured `security_profile` calls for, from the skill's `assets/ci/workflows/security/` into `.github/workflows/` (templates from `assets/templates/`). Record what was enabled in `docs/forge/SETUP.md`; never record a control as configured if the file was copied but the feature is off.

- `repo-fortress`: `scorecard.yml`; `SECURITY.md` template plus enable private vulnerability reporting (Settings -> Code security); `CODEOWNERS` template for security-sensitive paths derived from ARCHITECTURE.md Trust Boundaries.
- `ci-security` (adds): `codeql.yml` (with `codeql-config.yml`) or `semgrep.yml` — pick per project, both is usually noise; `dependency-review.yml`; `dependabot.yml` template; enable secret scanning + push protection.
- `full-devsecops` (adds): `osv-scanner.yml`, `sbom.yml`; `zap-baseline.yml` only for deployable web services with a staging URL the project is authorized to scan.

Enforcement: after scans produce results, add them as required via ruleset "Require code scanning results" so unresolved findings block PRs.

## Branch Protection

Prefer repository rulesets over classic branch protection rules: they target branches and tags, support path/size-based push blocking, bypass permissions, and org-level management. Use the OpenSSF Scorecard tiers as the maturity ladder and record the current tier in `docs/forge/SETUP.md`:

1. prevent force pushes and branch deletion
2. require 1 approving review; require branches up to date; require approval of latest push
3. require at least 1 status check
4. require 2 approving reviews; require Code Owners review
5. dismiss stale reviews on new commits; include administrators

For the integration branch:

- Require pull requests before merge.
- Require status checks to pass before merging.
- Add `FORGE Governance Checks` as a required check.
- Require branches to be up to date before merging.
- Document the merge semantics the repo uses for integration closeout, for example merge commit, squash merge, or fast-forward-only.
- Run `bash ci/scripts/verify-team-closeout.sh --task <task-id> --target integration` before opening the feature PR when practical.

For the release branch:

- Require pull requests before merge unless the team has a documented release automation path.
- Require status checks to pass before merging.
- Limit who can promote integrated work if the project needs stronger release control.
- Decide who runs the post-promotion release reconciliation step that moves tasks from `integrated` to `complete`.
- Record how claim release metadata is written when tasks move from active branch work to integrated or complete state.

For coordination-branch team mode:

- Consider protecting `forge-state` from casual direct pushes.
- If only automation or maintainers should update claim state directly, document that rule explicitly.
