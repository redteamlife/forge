# Changelog

All notable changes to this repository will be documented in this file.

## [Unreleased] - 2026-03-15

This section captures the changes currently on `dev` relative to `main`.

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

### Notes

- No existing changelog or release-notes file was present before this addition.
- If these changes are merged to `main` as a release, rename this section to the release version and date.
