# Design v3: Release-Gated Documentation, CHANGELOG, and Portable Publishing

Status: v2 direction approved by external review; four narrow blockers + minor
items incorporated here. review_state: changes-incorporated — awaiting a
design-level security review (below) and acceptance before TASK-022 begins.

## Problem

Four separable concerns: documentation structure, freshness policy, format
export, and release/version orchestration. Per-task doc triggers already
maintain *changed* docs; the gaps are a cumulative freshness backstop, a
CHANGELOG/versioning standard, portable publishing to GitLab wiki (primary) and
Obsidian, and treating publication as a security boundary. Reuse the existing
`application_docs` content set; do not rebuild it.

## Target mechanics (verify at implementation time)

- **Obsidian**: a vault is a folder of Markdown; standard relative links work;
  frontmatter renders as properties. No numbered folders or wikilinks required.
- **GitLab wiki**: a `<project>.wiki.git` repo; `home.md` landing, `_sidebar.md`
  nav; current GitLab supports wiki frontmatter (recognizes `title`) — preserve
  it.

## Decisions

### D1. Target-neutral canonical form

Author once in a consumer-neutral form: semantic folder paths (`overview/`,
`system/`, `operations/`, …) — never numbered folders (they bake order into
filenames → mass renames); YAML frontmatter (D2); standard relative Markdown
links; an ordered link list in the handbook `README.md` as the single
navigation manifest. Configured, not hardcoded:

```
application_docs: true
docs_root: docs/handbook
docs_format: flat | handbook     # flat = migration default; handbook for new
```

### D2. Frontmatter schema — defined enums, `updated` vs `reviewed_at` (v3)

Two distinct freshness facts (v3 fix): `updated` = content changed;
`reviewed_at` = a human confirmed it is still correct. Staleness keys off
`reviewed_at + review_in_days`, NOT `updated` (a mechanical edit must not reset
the review clock; a no-change review must).

Core keys and enums (defined before implementation):

```
title:        <string>
slug:         <kebab-string>
doc_type:     overview | system | software | interface | operations | troubleshooting | adr
owners:       <list of strings>
created:      YYYY-MM-DD
updated:      YYYY-MM-DD
reviewed_at:  YYYY-MM-DD
review_in_days: <int>
status:       draft | active | deprecated | archived
tags:         <list of strings>
sensitivity:  public | internal | confidential | restricted   # ordered lattice, low->high
```

`x-*` extension keys are permitted. Missing `sensitivity` is treated as
`restricted` (fail closed, D4).

### D3. Deterministic exporter — bounded frontmatter grammar, no new CLI

Invoke via skill-relative Python (FORGE has no standalone CLI):
`python3 <skill-root>/assets/scripts/forge_docs_export.py --target {gitlab-wiki|obsidian} ...`

Frontmatter is preserved textually and passed through. The exporter parses only
a **documented restricted grammar**: single-line scalars and single-line inline
lists (`[a, b]` or `key:` block lists) for exactly `title, slug, doc_type,
owners, status, sensitivity, reviewed_at, review_in_days`. No general YAML
parser; no PyYAML dependency in the user repo. Anything outside the grammar is
preserved but not interpreted. (This also lets D4/summary read `owners`/`status`
— the v2 gap.)

Engineering scope (must cover): slug normalization + collision detection,
case-insensitive filesystem collisions, duplicate filenames across folders,
heading/anchor links, attachments/images, Mermaid fences, deleted-page sync,
existing `_sidebar.md`/`home.md` handling, reproducible output ordering,
post-transform link validation, and an output manifest (source commit/version +
per-file output hashes). Destination safety: refuse to overwrite unmanaged
files.

Destinations (v3 resolves the v2 contradiction):
- **Prepare** (automatic, D8) writes export output only to an in-repo staging
  path.
- **Explicit** invocation may copy to an external Obsidian vault *after
  authorization*, into a managed subtree (marker file); never touch
  `.obsidian/` or unrelated notes.

### D4. Sensitivity gates publication — flat config, fail closed (v3)

Flat config (v3 fix — nested config breaks FORGE's flat readers, and precedent
is `dev_only_paths`/`governed_paths`):

```
docs_publish_targets: gitlab-wiki, obsidian
gitlab_wiki_max_sensitivity: internal
obsidian_max_sensitivity: confidential
sensitivity_excess_behavior: fail | omit    # default fail
```

The exporter compares each doc's `sensitivity` against the target's max on the
ordered lattice (`public < internal < confidential < restricted`).

- `fail` (default): any doc exceeding the target aborts the whole export.
- `omit`: exclude the doc, record the exclusion in the output manifest, and fail
  if any navigation entry or surviving link references an omitted page.
- Missing/unknown `sensitivity` → `restricted` (never publishable by a
  permissive default). Migration of unclassified legacy docs classifies them
  `restricted` or requires manual classification — never auto-publishable.

Stripping `sensitivity` while exporting the content is forbidden.

### D5. Release change surface = a release manifest, acyclic ordering (v3)

Manifest fields:

```
version:
previous_version:
content_commit:        # the immutable commit exported from (NOT the evidence commit)
included_tasks:
docs_export_hashes:    # per-file output hashes
release_timestamp:     # supplied or SOURCE_DATE_EPOCH; excluded from repro hashes
```

Acyclic sequence (v3 fix — v2's `source_commit` could not name the tree that
contained the manifest):

1. Update docs/version/CHANGELOG; commit the release **content**.
2. Export from that immutable content commit.
3. Record the content commit + export hashes in the manifest.
4. Commit generated evidence (manifest/export) separately, if tracked.
5. Promote/tag the evidence commit; the manifest identifies the content commit
   distinctly.

`included_tasks` algorithm by task source: `local` — tasks integrated since the
prior release manifest; `github`/`gitlab` — milestone or explicit release
assignment; `external` — a supplied list.

### D6. Release topology matrix — forge-ship selects, does not implement one

| Repository shape | Authoritative release action |
| --- | --- |
| Normal | merge/tag per project policy |
| Clean-main | `forge-promote.sh --tag` |
| Private/public tool | `forge-tool-workflow` / publish scripts |
| Multi-package monorepo | deferred (see D7) |

### D7. Versioning/changelog configured; multi-package deferred (v3)

```
release_management: semver | calver | tag-only | external | disabled
version_source:     VERSION | package.json | pyproject.toml | tag | external
changelog:          keep-a-changelog | provider-generated | external | disabled
```

No universal `VERSION`. Conventional-Commit types **suggest** changelog sections
(feat→Added/Changed, fix→Fixed, `!`→Changed/Removed/Security); a human curates.
Multi-package (multiple versions/sources in one repo) is explicitly **deferred**
to a follow-up design; v3 models a single version + source. forge-ship stops
with a clear message if it detects multiple independent version sources.

### D8. Release as two stages — Prepare then Publish

**Prepare** (authoritative, pre-tag): select version; update the configured
version source; curate `CHANGELOG.md`; validate triggered + expired docs (via
`reviewed_at`); generate export + manifest to in-repo staging (D3/D5); run
checks; commit release content, then evidence (D5 sequence).

**Publish**: promote/merge per topology (D6); tag the evidence commit; push with
explicit authorization; publish provider release notes from the CHANGELOG;
publish or hand off the wiki output; record release evidence.

A tag-triggered workflow is too late to gate an invalid CHANGELOG; pre-tag
validation in Prepare is authoritative. TASK-027 ships a provider-neutral
validator with thin GitHub and GitLab examples (GitLab primary).

## Design-level security review (requested by review)

Publication is a trust boundary; the following are architectural security
decisions, reviewed here:

- **Classification lattice** `public < internal < confidential < restricted`,
  compared numerically; unknown/missing → `restricted`. Fail closed.
- **Excess handling** defaults to `fail` (abort); `omit` must not leave dangling
  links/nav to omitted pages (enforced), preventing partial leaks or broken
  published trees.
- **Path handling**: exporter refuses to overwrite unmanaged files; external
  vault writes require authorization and a managed-subtree marker; never writes
  outside the repo during automatic Prepare.
- **No secret exfiltration via frontmatter**: only the documented key set is
  interpreted; the block is otherwise passed through unmodified, so the exporter
  introduces no new parsing-driven execution.
- **Residual risk**: correct classification depends on authors setting
  `sensitivity`; the `restricted` default mitigates omission. TASK-023 carries a
  full implementation security review.

## Implementation plan (re-split per review)

1. TASK-022: `docs_root`/`docs_format` config + target-neutral handbook layout +
   frontmatter schema/enums + `reviewed_at` staleness report. Scope also touches
   bootstrap, `application-docs.md`, execute-task, critique, evaluation,
   generated surfaces, validators, migration, fixtures.
2. TASK-023: exporter **core + classification/security policy** (grammar, path
   safety, fail/omit, manifest, link validation) — **security review required**.
3. TASK-024: gitlab-wiki adapter (slugs, `_sidebar.md`/`home.md`, link rewrite).
4. TASK-025: obsidian adapter (managed subtree, external-vault authorization).
5. TASK-027: CHANGELOG template + `references/release-management.md` +
   provider-neutral release validator (GH/GL examples).
6. TASK-028: release-manifest generation + `forge-ship` Prepare/Publish
   orchestration (D5/D6/D8).

(TASK-026 is unrelated — the bootstrap setup interview.)

## Non-goals

Auto-pushing to remotes/hosted sites; generating content from code; replacing
per-task triggers; a standalone `forge-docs` CLI; multi-package release (deferred).

## Process note

Add an optional `review_state` (draft|in-review|changes-requested|accepted) to
design tasks — FORGE currently conflates "authored" with "accepted." Applied
manually here.
