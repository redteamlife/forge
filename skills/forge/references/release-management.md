# FORGE Release Management

Configured in `docs/forge/AI.md`; nothing here is universal. FORGE conducts the
release the project's way rather than imposing one.

```
release_management: semver | calver | tag-only | external | disabled
version_source:     VERSION | package.json | pyproject.toml | tag | external
changelog:          keep-a-changelog | provider-generated | external | disabled
```

## Versioning

- `semver` — MAJOR.MINOR.PATCH: breaking / feature / fix. Default recommendation.
- `calver` — date-based (e.g. `2026.07.0`).
- `tag-only` — annotated tags, no version file.
- `external` / `disabled` — another system owns versioning, or none.

`version_source` is the single authority for the current version. Do not create
a `VERSION` file when the project already carries its version in
`package.json`, `pyproject.toml`, or tags — that invites drift. FORGE reads and
bumps the configured source only.

## Changelog

With `changelog: keep-a-changelog`, maintain `CHANGELOG.md` (template in
`assets/templates/CHANGELOG.md`). Conventional-Commit types **suggest** sections
but do not mechanically determine them — a human curates:

| Commit type | Usual section | But may be |
| --- | --- | --- |
| feat | Added | Changed |
| fix | Fixed | Security |
| refactor/perf | Changed | — |
| `!` / BREAKING | Changed | Removed, Security |

At release, move `Unreleased` entries under the new version with the date.

## Release cadence and gates

Documentation and changelog are updated at **release**, not on every commit
(per-task triggers already maintain changed docs). The `forge-ship` Prepare
stage is the cumulative backstop: it validates triggered + stale docs
(`forge_docs_staleness.py`), curates the changelog, bumps the version source,
and regenerates any configured doc exports before the tag exists. Tag-triggered
CI is too late to gate an invalid changelog — see `forge-ship`.

## Provider automation

Ship a provider-neutral release validator; wire it with a thin GitHub Actions or
GitLab CI job. The validator asserts the changelog has an entry matching the
version being released and that no docs are past their review window. It runs in
Prepare (authoritative, pre-tag); tag-triggered jobs only publish notes after.
