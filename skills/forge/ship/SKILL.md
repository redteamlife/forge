---
name: forge-ship
description: Use when the user asks to merge, release, promote, reconcile, or close out work in a repo containing `docs/forge/` or governed by FORGE. Not for per-task commits; those complete inside forge-execute-task.
---

# FORGE Ship

Use this skill to reconcile and release FORGE-governed work. Task-level closeout
(critique/security/evaluation, task state) happens in `forge-execute-task`; ship
handles integration, the release, and closeout evidence.

## Reads

`docs/forge/CONTEXT.md` (if present), `docs/forge/AI.md`, the task(s) being
shipped, and `TEAM.md` only in team mode or when branch policy requires it.
Release behavior is configured: `release_management`, `version_source`,
`changelog`, the release topology (below), and `application_docs`/export config.

## Release is two stages

A tag is too late to gate an invalid changelog or stale docs, so validation is
authoritative in Prepare, before any tag exists.

### Prepare (authoritative, pre-tag)

1. Confirm each shipped task's gates are complete and it is integrated.
2. Select the next version from `release_management` + `version_source`; update
   that source (never invent a `VERSION` file when the project carries its
   version elsewhere).
3. Curate `CHANGELOG.md`: move `Unreleased` entries under the new version
   (`references/release-management.md`; commit types suggest sections, a human
   curates).
4. Validate docs and changelog: `forge_release_check.py --version <v>
   [--docs-root <docs_root> --changelog <file>]`. It fails on a missing
   changelog entry or docs past their review window (`forge_docs_staleness.py`).
5. If `application_docs` and export targets are configured, regenerate exports to
   an in-repo staging path with `forge_docs_export.py` (fail-closed on
   classification). Never write outside the repo during Prepare.
6. Run project checks. Record a release manifest (version, previous_version,
   content_commit, included_tasks) as evidence.
7. Commit release content, then generated evidence (keep the manifest's
   `content_commit` acyclic — it names the content commit, not the evidence
   commit).

### Publish

8. Release per the configured topology:
   - normal repo: merge/tag per project policy
   - clean-main (`dev_only_paths` set): `<skill-root>/assets/scripts/forge-promote.sh -m "release: <v>" --tag v<v>` from the integration branch — never merge into `release_branch` directly
   - tool project: `forge-tool-workflow` / publish scripts
   - multi-package monorepo: not yet supported — stop and ask
9. Push branch/tag with explicit authorization; publish provider release notes
   from the changelog; publish or hand off the wiki/vault export (external-vault
   writes require authorization).
10. Record release evidence and move shipped tasks to `complete`.

## Hard Stops

Stop when a shipped task's gates are incomplete, `forge_release_check.py` fails,
release acceptance is not observable, the merge/promotion violates branch policy,
multiple independent version sources are detected (multi-package unsupported), or
a doc export fails classification.

## Evidence Required

- release manifest (version, previous_version, content_commit, included_tasks)
- updated changelog entry and bumped version source
- release check result; export manifest when docs are published
- merged PR/MR, release commit/tag, or explicit human acceptance
- claim release metadata in team mode
