# Changelog

All notable changes to this repository will be documented in this file.

## [Unreleased]

## [1.8.1] - 2026-07-26

### Fixed

- `validate-generated-docs.sh` now fails when a `dev_only_paths` entry is missing from the release-branch-guard workflow's `DEV_ONLY_PATHS` env, converting the documented duplication into a drift check.
- `forge-promote.sh` creates an unborn release branch on first promotion (the normal clean-main starting state) and refuses to promote over a release HEAD that lacks the new `Promoted-From` trailer — i.e. direct commits on the release branch — unless `--force` is passed.

### Changed

- Bumped the default generated `forge_version` to `1.8.1`.
- Design notes: agent-surface `docs/forge/` links intentionally dangle on a default clean-main release branch (the generated fallback line explains the state); `AI.md` documents common surface-path candidates for `dev_only_paths`.

## [1.8.0] - 2026-07-25

### Added

- Added the clean-main model as a first-class flow: optional `dev_only_paths` in FORGE-config drives the release-branch guards (`block-forge-in-main.sh`, `pre-push`), the new snapshot-based `assets/scripts/forge-promote.sh`, and the new `release-branch-guard.yml` workflow asset; bootstrap asks governed profiles whether the release branch stays free of governance files and documents the solo `integration_branch: dev` variant.
- Added a clean-main fallback line to generated agent surfaces so routers never dangle on a release branch with `docs/forge/` stripped; surface exclusion from the release branch is opt-in via `dev_only_paths`, not the default.
- Added `skills/forge/VERSION` for version discoverability, with a verify-repo check keeping it in sync with the generated `forge_version` and the newest CHANGELOG entry.
- Documented `git config core.hooksPath ci/hooks` as an optional hook-installation mode with its trade-offs; CI remains the durable backstop.

### Changed

- Bumped the default generated `forge_version` to `1.8.0`.

## [1.7.0] - 2026-07-25

### Added

- Added narrative `AGENTS.md` agent surface with scoped Cursor rules and stack detection (`forge_generate_agent_surfaces.py --narrative --scoped-rules`).
- Added contract-first scaffolding (`forge_scaffold_contract.py`) with OpenAPI, protobuf, and GraphQL starter templates plus an OpenAPI drift-check workflow.
- Added profile-gated DevSecOps assets: GitHub workflows for OpenSSF Scorecard, CodeQL (with tuning config), Semgrep dual-scan, dependency review, OSV-Scanner, SBOM generation/analysis, and ZAP baseline under `assets/ci/workflows/security/`; GitLab parity jobs in `assets/ci/gitlab/security.gitlab-ci.yml`; `SECURITY.md`, `dependabot.yml`, and `CODEOWNERS` templates; per-profile setup guidance in `assets/ci-setup/`.
- Added a quality CI workflow (`forge-quality.yml`) for team-full with CI enforcement.
- Added regression fixtures in `verify-repo.py` for generated-docs validation (checklist layouts, profile-aware SETUP checks) and YAML parsing of all bundled CI assets.

### Fixed

- Bootstrap can no longer produce an index-only `SECURITY_CHECKLISTS.md` pointing at a missing `security-checklists/` directory: bootstrap must copy `general.md` plus relevant surface checklists (or compose a monolithic file with real items), the compatibility template is now a router valid only with the split directory, and existing index-only scaffolds are repaired on refresh.
- `validate-generated-docs.sh` now rejects unusable checklist layouts (missing `general.md`, itemless checklist files, wrappers referencing a missing directory, elevated `security_profile` with no layout), validates `SETUP.md` sections per `security_profile`, accepts `todo` in the legacy ledger, and no longer requires `TEST_STRATEGY.md` or legacy Strict-era files that doc minimums say not to generate.
- Aligned `ARCHITECTURE.md` (`## Overview`) and `TEAM.md` (Integration Flow, Review And Merge, Task Closeout) templates with validator expectations.
- `AI.md` template no longer defaults solo profiles to team branch topology; coordination/integration branches are commented out with per-profile guidance, and task templates document the valid status set with `complete` as the only terminal status.
- Repaired broken reference paths in the plan, build, critique, evaluation, and cross-project skills; synchronized install/verify file lists across `verify-repo.py`, `verify-install.sh`, and `install.ps1`.

### Changed

- Bumped the default generated `forge_version` to `1.7.0`.
- Sharpened the root skill trigger description within its size budget.
- Existing repos with an incomplete checklist scaffold repair by re-running `forge-bootstrap` (refresh); the security-review skill also falls back to the installed pack's checklists and flags the scaffold when project-local checklists are unusable.

## [1.6.0] - 2026-05-15

### Added

- Added `agent_context_profile` and generated `docs/forge/CONTEXT.md` to make default agent reads explicit and budgeted.
- Added split local task templates with `TASKS.index.yaml` plus per-task files under `docs/forge/tasks/`.
- Added split memory templates with `MEMORY.index.yaml` plus topic files under `docs/forge/memory/`.
- Added deterministic context helper scripts for context budgets, agent-surface generation, context migration, context validation, and split-task resolution.
- Added multi-surface context validation for `CLAUDE.md`, `AGENTS.md`, Cursor, Copilot, Windsurf, and Codex hook surfaces.
- Added size-budget verification for high-frequency skill files, generated templates, and always-on agent surfaces.

### Changed

- Bumped the default generated `forge_version` to `1.6.0`.
- Reworked generated agent surfaces to router-style guidance that avoids default `docs/forge/*` include bombs.
- Reduced default context usage across high-frequency FORGE skills by making `CONTEXT.md`, the task index, and one selected task the normal read path.
- Shrunk generated `AI.md`, `TEAM.md`, and CI documentation, moving optional details into split references and topic files.
- Updated CI validators and hooks to support split local task ledgers while preserving `TASKS.yaml` compatibility.
- Clarified that FORGE installs as a skill pack; bundled scripts are run by skill-relative path rather than requiring a standalone `forge` shell command.

## [1.5.0] - 2026-05-07

### Added

- Added optional `forge-cross-project` coordination for multi-repo projects, with authority/peer/downstream roles, `docs/forge/cross-project/` templates, XPD decision records, contract docs, inbox proposals, sister-repo pointers, and install/verification coverage.
- Added FORGE skill-anatomy and lifecycle-map guidance, plus lifecycle alias skills for plan, build, review, and ship flows.
- Added rationalization guards and evidence exits to core operational skills so agents have clearer stop and proof conditions.

### Changed

- Bumped the default generated `forge_version` to `1.5.0`.

## [1.4.0] - 2026-04-30

### Changed

- Bundled the FORGE governance assets inside the skill pack itself so installs via `skills add` are self-sufficient. The `ci/` tree (hooks, validators, workflow template, org-policy template) moved from the repo root to `skills/forge/assets/ci/`, and the git-hook installer scripts moved from `scripts/install-forge-hooks.{sh,ps1}` to `skills/forge/assets/scripts/install-forge-hooks.{sh,ps1}`. CI-setup guides, bootstrap, and root docs now point at `<skill-root>/assets/ci/` and `<skill-root>/assets/scripts/`. The hook-installer's relative `../ci/hooks` path is preserved (both directories are still siblings under `assets/`), so the installer continues to work without code changes. Direct-clone consumers who referenced repo-root `ci/` or `scripts/install-forge-hooks.*` need to update to the new paths.
- Bumped the default generated `forge_version` to `1.4.0`.

## [1.3.0] - 2026-04-28

### Added

- Optional `application_docs: true` flag in `AI.md` enables a human-facing `docs/` tree (separate from `docs/forge/`) with overview, architecture, threat model, developer guide, interfaces, deployment, runbook, and ADR templates. Default `false`.
- `assets/application-docs/` cleaned template set with minimal frontmatter (`title`, `owners`, `status`, `updated`); profile-aware subset is generated by `forge-bootstrap`.
- `references/application-docs.md` defines the audience split, profile-aware default subset, and maintenance trigger map (which task types update which docs).
- Maintenance triggers wired into `forge-execute-task` (in-scope check), `forge-critique` (missing-update flag, ADR proposal for significant decisions), and `forge-evaluation` (in-change-set requirement).
- `task_type: architecture-decision` triggers an expected ADR when `application_docs: true`.
- `ci/scripts/validate-security-profile.sh` enforces that a stronger `security_profile` is backed by concrete `SETUP.md` evidence, fails closed when sections are missing or blank, and verifies SAST claims have a workflow or recorded tool.
- `ci/scripts/validate-evaluation-currency.sh` requires task-state transitions and `EVALUATION.md` evidence to land in the same commit, not split across the PR.
- `ci/scripts/validate-memory-bounds.sh` fails closed when `MEMORY.md` exceeds its declared `max_entries`, forcing consolidation before new entries can land.
- `scripts/install-forge-hooks.sh` and `scripts/install-forge-hooks.ps1` install the FORGE git hooks idempotently with `.bak` of any non-FORGE hook found.
- `forge-bootstrap` runs the hook installer automatically for `solo-governed` and `team-full` profiles and records the outcome in `SETUP.md`.
- Profile-aware `SETUP.md` generation via `<!-- FORGE-section: <profile> -->` markers so baseline projects do not carry DevSecOps boilerplate.
- Hard-stop wiring for `requires_independent_review` in `forge-execute-task` and `forge-evaluation`; the implementing agent cannot self-evaluate when the flag is set.

### Changed

- Trimmed `repo_flavor` enum to `contract-first` and `tooling`; the `minimal` and `issue-tracker-heavy` values are dropped because they restated `task_source`.
- Reorganized `forge-bootstrap` workflow into explicit **Detect / Generate / Follow-up** phases.
- Consolidated speculative memory entry types: `parallelism-incident` and `tracker-workflow` are replaced by a single `coordination-incident` type.

## [1.2.0] - 2026-04-28

### Added

- Added optional `repo_flavor` routing guidance for `contract-first` and `tooling` repositories.
- Added `agent-flavors` guidance for `AGENTS.md`, `CLAUDE.md`, Cursor rules, Copilot instructions, Codex hooks, and Windsurf rules.
- Added contract artifact guidance for OpenAPI, protobuf, GraphQL, generated clients, schemas, and other integration-boundary files.
- Added optional task traceability fields for issue provider, issue IID, issue URL, plan refs, PR/MR URLs, contract files, and independent review.
- Added team role split, integration boundary, tracker access, and token-scope setup guidance.
- Added memory incident types `contract-conflict` and `coordination-incident` for reusable interface and parallel-work failure lessons.
- Added `security_profile` guidance for baseline, repo-fortress, ci-security, and full-devsecops gate levels.
- Added DevSecOps checklist assets for repository governance, CI security, supply chain, and continuous delivery security.

### Changed

- Bumped the default generated `forge_version` to `1.2.0`.
- Updated execute, critique, evaluation, and security-review gates for contract-first and external source-of-truth workflows.
- Updated reusable agent surfaces so they respect configured task sources and declared contract files.
- Expanded setup and security-review guidance for branch protection, CODEOWNERS, security policy, SAST, DAST, SCA, SBOM, provenance, and cleanup evidence.

## [1.1.0] - 2026-04-26

### Added

- Added `task_source` configuration with `local`, `github`, `gitlab`, and `external` task ledger modes.
- Added bootstrap guidance for choosing task tracking during setup and detecting authenticated GitHub/GitLab CLIs.
- Added issue-backed team coordination guidance for GitHub and GitLab repositories.
- Added structured memory entry guidance with `max_entries` consolidation behavior.
- Added a local `pre-commit` hook that blocks local `TASKS.yaml` changes without matching `EVALUATION.md` evidence.

### Changed

- Bumped the default generated `forge_version` to `1.1.0`.
- Updated team-mode execution guidance to prefer GitHub/GitLab issue assignment and labels over `forge-state` when issue-backed task sources are selected.
- Updated evidence validation so task-state changes or `FORGE-task` trailers require `EVALUATION.md` in the same PR when CI enforcement is enabled.
- Updated install scripts so verification runs automatically after install.
- Updated setup docs to include the new hook, task-source configuration, and issue-backed coordination model.

## [1.0.0] - 2026-04-15

### Added

- A full skills-first FORGE release under `skills/forge/` with focused subskills for `forge-bootstrap`, `forge-execute-task`, `forge-critique`, `forge-security-review`, `forge-evaluation`, `forge-memory`, and `forge-tool-workflow`.
- Root install, uninstall, verification, and migration helpers for easier public distribution and local setup.
- Vercel `npx skills add` compatible repo layout using `skills/forge/`.
- Reusable agent/editor onboarding assets under `skills/forge/assets/agent-surfaces/`.
- Modular security checklist assets under `skills/forge/assets/security-checklists/`.
- Team-mode coordination support with claim metadata, coordination branch flow, integration/release branch flow, and release reconciliation guidance.
- Team-mode CI validation for branch-aware task states and task claim metadata.
- Packaging verification workflow for the public skills repo layout.

### Changed

- FORGE moved from a document-template-first model to a skills-first model.
- The canonical FORGE runtime contract now lives in the skill pack rather than a generated `docs/forge/FORGE.md`.
- The public repo layout was flattened so install docs, migration docs, and verification helpers live at the repo root.
- Tool scaffolding now seeds minimal `docs/forge/` files from the canonical skill assets instead of copying a retired template generator.
- Root onboarding docs were rewritten around how people actually use FORGE in practice: bootstrap, review the docs, then tell the agent to start working.
- README and quickstart docs now explain FORGE in a more human, usage-first way with natural prompt examples and "start working" prompts people can paste directly into an agent.
- The main README now explains major FORGE features, subskills, security review, customizable checklists, and the private-dev/public-release tool workflow in more human terms.
- The default `forge_version` in generated `AI.md` is now `1.0.0`.
- FORGE response guidance was tightened to reduce token overhead with terser working updates, fixed response shapes, and less reasoning narration.
- Bootstrap guidance now explicitly avoids echoing generated file contents and routine planning commentary back into chat.
- Commit policy now explicitly forbids AI attribution and tool-marketing lines such as “Generated by Claude” or “Coded with Cursor”.
- The skills repo now publishes a stronger marketing-facing description for the public `forge` skill listing.
- The verification workflow was renamed to `verify-forge-skills.yml`.

### Removed

- The old root `templates/` directory and `GENERATE_PROJECT_DOCS.md` workflow.
- The old `forge-skills-based/` wrapper directory in favor of root-level install/docs helpers plus `skills/forge/`.
- Duplicated root agent-surface files that are now packaged only in the reusable skill assets.

## [0.1.1] - 2026-03-15

### Changed

- `forge-publish.sh` and `forge-publish.ps1` now warn on missing `release_dir` ignores during dry runs and automatically add the ignore entry during real open-source publishes.
- Documented FORGE version examples now use `0.1.1`.
- Open-source tool scaffolding and workflow docs now support `publish_strategy`, defaulting new collaborative projects to `preserve-history`.
- Open-source publish scripts now support both `snapshot-force-push` and `preserve-history`.
- `forge-sync-public` now records `public_sync.last_imported_public_commit` and imports files through explicit `sync_map` rules instead of blunt path rewriting.
- `preserve-history` publish now blocks if public `main` contains merged non-release commits that were not first imported into private dev.

### Added

- Added an open-source collaboration proposal covering `publish_strategy`, public PR intake, and history-preserving public publishing for community-driven tool projects.
- Added `forge-sync-public.sh` and `forge-sync-public.ps1` for importing merged public PRs back into the private dev repo as intake work.

## [0.1.0] - 2026-03-15

### Added

- Cross-platform tool workflows with `scripts/forge-tool-init.sh`, `scripts/forge-tool-init.ps1`, `scripts/forge-publish.sh`, and `scripts/forge-publish.ps1`.
- Optional CI validation for generated docs with `ci/scripts/validate-generated-docs.sh`.
- Optional CI validation for task file-scope enforcement with `ci/scripts/validate-file-scope.sh`.
- Governance protection to keep `docs/forge` from being merged into `main`, via `ci/scripts/block-forge-in-main.sh`, `ci/hooks/pre-push`, and `ci/workflows/forge-governance.yml`.
- `forge_version` support in the FORGE config block.
- `file_scope` support in task definitions and templates.
- `task_type` support and typed security checklist templates.
- `TOOL_WORKFLOW.template.md` and `forge.yaml.template` for tool-development and publishing flows.
- A repo `.gitignore` entry for local Claude settings.

### Changed

- Rewrote `README.md` and `GETTING_STARTED.md` for clearer onboarding and beginner accessibility.
- Clarified FORGE template behavior around Mid mode and automatic generation rules.
- Added an invariants block to the FORGE execution template.
- Restructured the memory template for easier retrieval and reuse across sessions.
