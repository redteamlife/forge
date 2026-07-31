# Security Review: forge_docs_export.py (TASK-023)

Scope: the publication trust boundary — classification enforcement, path
handling, and frontmatter parsing in `forge_docs_export.py` /
`forge_docs_adapters.py`.

## Change surface

A stdlib-only exporter that reads authored docs and writes a target tree
(GitLab wiki / Obsidian). It never pushes to a remote and never executes doc
content. Threat model: (a) leaking a doc above the target's clearance,
(b) overwriting unmanaged files, (c) parser-driven surprises from frontmatter.

## Findings and controls

- **Classification lattice** `public < internal < confidential < restricted`,
  compared as integer ranks. Missing/unknown `sensitivity` maps to `restricted`
  (fail closed). `pass` — verified by fixture (a `confidential` doc against an
  `internal` target aborts; a README with no sensitivity is treated as
  restricted and blocks until classified).
- **Excess behavior**: `fail` (default) aborts the whole export; `omit` drops
  the doc AND fails if any kept page's link resolves to an omitted page, so no
  dangling nav/link can leak the existence of, or a path to, withheld content.
  `pass` — fixture confirms the dangling-link abort.
- **Path safety**: refuses a non-empty destination lacking the
  `.forge-export-manifest.json` marker unless `--force`; re-export into a managed
  dir is allowed. `pass` — fixture confirms refusal of an unmanaged dir.
- **No content execution / no parser RCE**: frontmatter is parsed with a bounded
  grammar (documented scalar + simple-list keys); the block is otherwise
  preserved verbatim and never evaluated. No YAML/eval. `pass`.
- **Reproducibility**: output is deterministically ordered; the manifest records
  per-file sha256; `release_timestamp`/`generated_at` are excluded from the
  hashed outputs. `pass` — fixture confirms identical hashes across runs.

## Residual risk

- Correct classification depends on authors setting `sensitivity`. Mitigated by
  the `restricted` default (unclassified never publishes) and by the staleness /
  review workflow surfacing docs for human attention.
- External-vault writes (Obsidian) require explicit authorization and a managed
  subtree; automatic Prepare only writes in-repo (enforced by the caller /
  forge-ship, TASK-028).

## Outcome

No blocking issues. The publication boundary is fail-closed by construction.
security: pass.
