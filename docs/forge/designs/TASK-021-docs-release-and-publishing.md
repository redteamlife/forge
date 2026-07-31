# Design v2: Release-Gated Documentation, CHANGELOG, and Portable Publishing

Status: revised after external review (v1 critique: changes required). All
blocking findings verified against the repo and incorporated. review_state:
changes-incorporated — awaiting acceptance before TASK-022 begins.

## Problem

Four separable concerns, kept separate here (the review's framing): documentation
structure, freshness policy, format export, and release/version orchestration.

1. **Doc freshness has no cumulative backstop.** Per-task triggers maintain
   *changed* docs (execute/critique/evaluation already do this); nothing catches
   cumulative consistency, navigation, ownership, and expiry drift across a
   release. The fix is a release-time backstop, NOT a replacement cadence — both
   run.
2. **No CHANGELOG and no versioning/release standard for user projects**, though
   this repo runs that flow by hand.
3. **Docs are not portable** to a GitLab project wiki (primary) or an
   Obsidian/markdown vault.
4. **Publishing is a security boundary** (added in v2): exporting a
   `confidential` doc to a broadly-visible wiki is a data leak; classification
   must gate publication.

Reuse, do not rebuild: the `application_docs` content set and its maintenance-
trigger model.

## Target mechanics (verify exact behavior at implementation time)

- **Obsidian**: a vault is just a folder of Markdown; standard relative links
  work; frontmatter renders as properties. It does NOT require numbered folders
  or wikilinks. Near-lossless target.
- **GitLab wiki**: a `<project>.wiki.git` repo; `home.md` landing, `_sidebar.md`
  nav; current GitLab *does* support wiki-page frontmatter and renders it in a
  metadata box (recognizing `title`). Preserve frontmatter; do not assume it
  must be stripped. (Confirm current rendering at implementation time.)

## Decisions

### D1. Target-neutral canonical form (revised)

Canonical docs are authored once in a form that privileges neither consumer:

- semantic folder paths (`overview/`, `system/`, `operations/`, ...), NOT
  numbered folders — baking order into filenames causes mass renames and noisy
  history on reorder
- YAML frontmatter (D2)
- standard relative Markdown links
- an ordered link list in the handbook `README.md` as the **navigation
  manifest** (single source of order)

Location and shape are configured, not hardcoded:

```yaml
application_docs: true
docs_root: docs/handbook        # configurable; not docs/<AppName>/
docs_format: flat | handbook    # flat = migration default; handbook for new projects
```

Exporters add target-specific ordering or link forms from the README manifest.

### D2. Small core frontmatter schema + extensions (revised)

Standardize a small core with enums; permit `x-*` extension keys; do not make
essential fields arbitrarily configurable.

Core: `title, doc_type, slug, owners, created, updated, status, tags,
sensitivity, review_in_days`. `updated` + `review_in_days` drive a staleness
report ("review due"); the release gate surfaces overdue docs.

### D3. Deterministic exporter, no home-grown YAML, no new CLI (revised)

Invoke via skill-relative Python (FORGE has no standalone CLI):
`python3 <skill-root>/assets/scripts/forge_docs_export.py --target {gitlab-wiki|obsidian} ...`

Frontmatter handling: **preserve the block textually**; parse only a strict,
documented set of scalar keys needed for routing (`sensitivity`,
`review_in_days`, `updated`, `title`, `slug`). No general YAML parser is written
or required in the user repo (the pack's own tooling uses PyYAML, but the
exporter must run without it). This resolves the v1 stdlib-vs-rich-YAML
contradiction.

Exporter must cover (from review): slug normalization + collision detection,
case-insensitive filesystem collisions, duplicate filenames across folders,
heading/anchor links, attachments/images, Mermaid fences, deleted-page
synchronization, existing `_sidebar.md`/`home.md` handling, reproducible output
ordering, post-transform link validation, and a generated output manifest
(source commit/version + per-file output hashes). Destination safety: refuse to
overwrite unmanaged files; for Obsidian, write only into a managed subtree
(marker file) and never touch `.obsidian/` or unrelated notes.

- **obsidian**: near-identity into the managed subtree; preserve frontmatter and
  folders; standard links.
- **gitlab-wiki**: emit a tree for `<project>.wiki.git` — slugs from paths,
  `_sidebar.md` + `home.md` from the README manifest, preserve frontmatter
  (optional visible owner/review summary only when configured; never duplicate
  metadata in both frontmatter and body by default), rewrite internal links to
  wiki slugs. Idempotent; `--dry-run` prints the mapping.

The script produces trees; it never pushes to a remote.

### D4. Sensitivity gates publication — fail closed (new, security-critical)

`sensitivity` controls export, not just describes it:

```yaml
docs_publish_targets:
  gitlab-wiki: { max_sensitivity: internal }
  obsidian:    { max_sensitivity: confidential }
```

The exporter refuses to emit any doc whose classification exceeds the target's
`max_sensitivity`. Missing or unknown classification is treated as the most
restrictive (fail closed) unless an explicit project policy sets otherwise.
Stripping `sensitivity` while still exporting the content is forbidden.
**TASK-023 requires a security review.**

### D5. Release change surface = a release manifest (new)

"Docs matching the release" needs a deterministic baseline. Produce a release
manifest on the **integration branch** (before promotion strips governance
state):

```yaml
version:
previous_version:
source_commit:
included_tasks:        # tasks integrated since previous_version
generated_at:
docs_export_manifest:  # path/hash of the export output
```

Clean-main interaction: because `forge-promote.sh` snapshots and tags without
integration history, the manifest MUST be generated pre-promotion where task
history exists, then carried as evidence.

### D6. Release topology matrix — forge-ship selects, does not implement one flow

| Repository shape | Authoritative release action |
|---|---|
| Normal | merge/tag per project policy |
| Clean-main | `forge-promote.sh --tag` |
| Private/public tool | `forge-tool-workflow` / publish scripts |
| Multi-package monorepo | possibly multiple versions/tags |

`forge-ship` reads the configured strategy and delegates; it does not hardcode a
bump/tag sequence.

### D7. Versioning/changelog are configured, not universal (revised)

```yaml
release_management: semver | calver | tag-only | external | disabled
version_source:     VERSION | package.json | pyproject.toml | tag | external
changelog:          keep-a-changelog | provider-generated | external | disabled
```

No universal `VERSION` file — many projects already carry a version in
`package.json`/`pyproject.toml`/tags. Conventional-Commit types **suggest**
changelog sections (feat→Added/Changed, fix→Fixed, `!`→Changed/Removed/Security)
but do not mechanically determine them; a human curates.

### D8. Release as two stages — Prepare then Publish (new)

**Prepare** (authoritative, pre-tag): select version; update the configured
version source; curate `CHANGELOG.md` (move Unreleased → version); validate
triggered + expired docs; generate export + manifest (D3/D5); run checks; commit
release preparation.

**Publish**: promote/merge per topology (D6); create tag; push branch/tag with
explicit authorization; publish provider release notes from the changelog;
publish or hand off the wiki output; record release evidence.

A tag-triggered workflow is too late to gate an invalid changelog (the tag
already exists). Pre-tag validation in Prepare is authoritative; tag-triggered
automation only publishes afterward. TASK-024 ships a **provider-neutral
validator** with thin GitHub and GitLab examples (GitLab primary), not a single
ambiguous `release.yml`.

## Accepted answers to v1 open questions

Flat is the compatibility default, handbook recommended for new projects (D1).
Canonical form is target-neutral, not Obsidian-shaped (D1). GitLab frontmatter
is preserved (D3). forge-ship auto-validates and generates configured exports in
Prepare but never writes outside the repo or publishes without authorization
(D3/D8). Schema is a small enum core plus `x-*` extensions (D2). Navigation is
the ordered README manifest, not numbered folders (D1).

## Implementation plan (bounded; sequence matters)

1. TASK-022: `docs_root`/`docs_format` config + target-neutral handbook layout +
   core frontmatter schema + staleness report. **Scope note (from review):**
   also touches bootstrap, `application-docs.md`, execute-task, critique,
   evaluation, generated surfaces, validators, migration, and fixtures — not
   just templates.
2. TASK-023: `forge_docs_export.py` (gitlab-wiki + obsidian) with the full
   engineering checklist and **D4 fail-closed classification gating**. Requires
   a security review.
3. TASK-024: CHANGELOG template + `references/release-management.md`
   (SemVer/CalVer, version_source, CC→section *suggestions*) + provider-neutral
   release validator with GH/GL examples.
4. TASK-025: `forge-ship` Prepare/Publish split (D8) + topology selection (D6) +
   release manifest (D5) + doc-minimums/README alignment.

## Process note

The review flagged that a design task marked `complete` with gates passed is not
the same as *accepted*. FORGE's design-task model conflates "authored" with
"accepted." Small follow-up: add an optional `review_state`
(draft|in-review|changes-requested|accepted) to design tasks. Applied here
manually pending that.

## Non-goals

- Auto-pushing to a wiki remote or hosted docs site (produce, don't push).
- Generating doc content from code.
- Replacing per-task doc triggers (this adds a release backstop).
- A standalone `forge-docs` CLI (use skill-relative Python).
