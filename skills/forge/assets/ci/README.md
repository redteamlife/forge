# FORGE CI Enforcement

This directory contains optional pipeline and hook artifacts that validate FORGE workflow outputs outside the agent.

Use this README as an index. Read only the setup topic you need.

## Quick Map

- Commit message format: `docs/commit-format.md`
- Validator behavior: `docs/validators.md`
- GitHub setup: `../ci-setup/github.md`
- GitLab setup: `../ci-setup/gitlab.md`
- Governance storage patterns: `docs/governance-patterns.md`

## Main Checks

- Conventional Commit plus FORGE trailers.
- Local task state matches the configured task ledger.
- Team-mode task metadata is complete.
- Evidence artifacts are updated when task state changes.
- File changes stay within declared `file_scope`.
- Security profile claims have setup evidence.

## Directory

```text
ci/
├── hooks/
├── scripts/
├── workflows/
└── policy/
```

Scripts support split local tasks through `scripts/forge_task_resolver.py`, preferring `docs/forge/TASKS.index.yaml` plus `docs/forge/tasks/` and falling back to legacy `docs/forge/TASKS.yaml`.

## Requirements

- `bash`
- `git`
- `python3` with `pyyaml`

The CI layer validates governance artifacts. It does not replace critique, security review, evaluation, or implementation review.
