# Design: Release-Gated Documentation, CHANGELOG, and Portable Publishing

Status: proposed (TASK-021). For external review before implementation.

## Problem

Three coupled gaps, from maintainer review plus a portability requirement:

1. **Docs drift because updates are per-task only.** FORGE's `application_docs`
   updates a doc when a task trigger fires, but nothing confirms the doc set is
   current at release. The desired cadence is release-gated, not per-commit.
2. **No CHANGELOG and no versioning/release standard for user projects.** The
   skill pack ships neither a CHANGELOG template nor a semver/release-cut flow,
   even though this repo runs that flow by hand every release. Conventional
   Commits are enforced; nothing maps them to a changelog or a version bump.
3. **Docs are not portable.** The maintainer wants the doc set publishable as a
   GitLab project wiki (primary) and exportable to an Obsidian/markdown vault.

What already exists (do not rebuild): the `application_docs` content set
(tool-overview, architecture-overview, threat-model, developer-guide,
interfaces-and-protocols, deployment-playbook, incident-runbook, ADRs) and its
maintenance-trigger model wired into execute/critique/evaluation.

## Target mechanics (verify exact behavior at implementation time)

- **Obsidian**: vault = folder of markdown; YAML frontmatter renders as
  first-class properties; numbered folders sort naturally; `[[wikilinks]]`
  native (standard markdown links also work). Near-lossless target.
- **GitLab wiki**: a separate `<project>.wiki.git` repo; `home.md` is the
  landing page; `_sidebar.md` defines nav; YAML frontmatter is NOT rendered as
  properties (appears as raw text); page slug derives from filename/path.
  Lossy target — frontmatter and folder-number prefixes must be transformed.

## Decisions

### D1. One canonical handbook, Obsidian-shaped, down-converted on publish

Canonical docs live in `docs/<AppName>/` authored in the rich format: numbered
concern folders (`00 - Overview/`, `01 - System Documentation/`, ...), a
`README.md` index, and full frontmatter. This is the source of truth because it
is the richest form — you can down-convert to GitLab wiki but cannot recover
stripped frontmatter. Obsidian is effectively the canonical form; publishing is
transformation, never re-authoring.

Upgrade the shipped `application_docs` templates from flat `docs/*.md` with
minimal frontmatter to this handbook layout. Backward compatibility: the
exporter also accepts the existing flat layout (numbering optional).

### D2. Rich frontmatter with staleness metadata

Adopt the maintainer's frontmatter schema:
`title, doc_type, slug, owners, created, updated, status, tags, sensitivity,
review_in_days`. `updated` + `review_in_days` enable a staleness check
("review due") — the mechanism that makes "always up to date" enforceable
rather than aspirational. A validator/report flags docs past their review
window; the release gate (D4) surfaces them.

### D3. Deterministic export pipeline: `forge_docs_export.py`

New bundled script (stdlib only), `--target {gitlab-wiki|obsidian}`:

- **obsidian**: copy the canonical tree into a vault path; preserve frontmatter
  and folders; normalize internal links to a form Obsidian resolves. Near
  identity.
- **gitlab-wiki**: emit a tree ready to commit to `<project>.wiki.git` —
  slugify page names (strip `NN - ` prefixes), generate `_sidebar.md` ordered by
  the folder numbering, generate/rename `home.md` from the README/overview,
  strip YAML frontmatter into a small visible header block
  (`> Owners: … · Updated: … · Status: …`), and rewrite internal links to wiki
  slugs. Idempotent; `--dry-run` lists the mapping.

Publishing (git push to the wiki remote) stays a documented human/CI step — the
script produces the tree; it does not push, matching FORGE's "scripts produce,
humans/CI publish" stance.

### D4. Release gate in `forge-ship` (not per-commit)

A release-preparation step, invoked when cutting a release:

- confirm application docs matching the release's change surface are current;
  surface any doc past its `review_in_days` window (D2)
- require a CHANGELOG update: move `Unreleased` entries under the new version
- conduct the version bump + tag + release notes (D5)
- regenerate the wiki/vault export (D3) so published docs match the tag

Per-commit doc triggers stay as they are; this gate is the release-cadence
backstop the maintainer asked for. Manual mode leaves it to explicit ship
requests; it is never forced on ordinary commits.

### D5. CHANGELOG + semver as first-class standards

- Ship a Keep-a-Changelog `CHANGELOG.md` template and a
  `references/release-management.md` covering SemVer, the
  Conventional-Commit-type -> changelog-section mapping (feat -> Added,
  fix -> Fixed, etc.), and the cut/tag/notes flow (the one this repo already
  runs by hand — codify it).
- Optional `release.yml` CI workflow asset: on tag, verify the CHANGELOG has a
  matching version entry and publish release notes from it.
- A project `VERSION` convention mirrored in the changelog, with a validator
  check (the pattern already proven for the pack itself).

## Open questions for review

1. **Canonical layout default.** Make the numbered-handbook + rich frontmatter
   the default `application_docs` output, or keep flat as default and offer the
   handbook as an opt-in `docs_format: handbook`? (Aesthetic/scope preference,
   not standards — maintainer's call.)
2. **Wiki frontmatter handling.** Strip to a visible header block, or drop
   entirely? Header preserves owner/updated visibly in GitLab; dropping is
   cleaner but loses metadata for wiki-only readers.
3. **Export scope.** Should `forge-ship` run the export automatically on
   release, or only produce it on explicit `forge-docs export`? Auto keeps the
   wiki in lockstep with tags; explicit avoids surprising git-tree output.
4. **Single vs multi-target frontmatter.** Is the maintainer's schema fixed, or
   should `doc_type`/`sensitivity`/`tags` be configurable per project?
5. **Numbered-folder ordering vs. explicit manifest.** Numbering gives free
   ordering but bakes sequence into folder names. Prefer a `nav`/manifest file
   instead, or keep numbering?

## Implementation plan (bounded tasks, if accepted)

1. TASK-022: rich-frontmatter schema + handbook layout for `application_docs`
   templates + staleness (`review_in_days`) report/validator.
2. TASK-023: `forge_docs_export.py` (gitlab-wiki + obsidian) with fixtures
   (frontmatter strip, sidebar generation, link/slug rewrite, dry-run).
3. TASK-024: CHANGELOG template + `references/release-management.md` (SemVer,
   CC->changelog mapping) + optional `release.yml` workflow.
4. TASK-025: `forge-ship` release gate wiring (docs-current + changelog +
   version/tag + export) + doc-minimums/README alignment.

## Non-goals

- Auto-pushing to the wiki remote or a hosted docs site (produce, don't push).
- A docs generator that authors content from code; the content model exists.
- Replacing per-task doc triggers; this adds a release backstop, not a rewrite.
