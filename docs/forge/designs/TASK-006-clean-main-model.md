# Design: First-Class Clean-Main Model (dev-only paths, promote tooling, surface degradation)

Status: proposed (TASK-006). Implementation follows in separate bounded tasks after review.

Origin: downstream bootstrap report against FORGE 1.7.0 (solo-governed, clean-main
repo): guards hardcode `^docs/forge/`, generated agent surfaces dangle on main after
promotion, no shipped promote tooling, solo integration branch undocumented, version
hard to discover. This repo already runs the clean-main model via repo-local
`scripts/forge-promote.sh` + `main-branch-guard.yml`; this design generalizes both
into the pack.

## Decisions

### D1. Canonical dev-only path set lives in FORGE-config

Add one optional field to the `FORGE-config` block in `docs/forge/AI.md`:

```
dev_only_paths: docs/forge/
```

- Comma-separated, single line — parseable by the existing `get_config_value` grep
  used by all shell consumers; no new file format, no new dotfile.
- Absent field = `docs/forge/` (today's behavior; fully backward compatible).
- Trailing `/` marks a prefix; otherwise exact file match.
- Projects wanting zero surfaces on main opt in explicitly:
  `dev_only_paths: docs/forge/, CLAUDE.md, AGENTS.md, .cursor/rules/`

Rejected alternative: separate manifest file (`.dev-only-paths`). One more governance
file to strip, and FORGE-config is already the single config surface validators parse.

### D2. Agent surfaces degrade gracefully; exclusion is opt-in, NOT default

Disagreement with the downstream proposal: generated `CLAUDE.md`/`AGENTS.md` default
to *staying* on main. Main is where fresh clones and new agents land; a router that
explains the repo uses FORGE is useful there. The actual bug is dangling references,
fixed at generation time:

- `forge_generate_agent_surfaces.py` appends one fallback line to every generated
  surface (router and narrative):
  "If `docs/forge/` is absent, this is the release branch of a clean-main FORGE
  repo: switch to `<integration_branch>` for governed work, or ask before making
  governed changes."
- The line is emitted only when the config indicates the clean-main model (D4),
  keeping non-clean-main surfaces unchanged.

### D3. Ship promote tooling and the main guard as pack assets

- `assets/scripts/forge-promote.sh`: generalized from this repo's script.
  - Tree-snapshot promotion (`git read-tree -u --reset <integration>`), NEVER
    squash-merge — squash reuses the original merge-base and conflicts on the
    second edit to the same line (hit in this repo, promotion 3).
  - Reads `release_branch`, `integration_branch`, and `dev_only_paths` from
    `docs/forge/AI.md` on the integration branch; flags: `-m`, `--tag`, `--dry-run`.
  - Refuses dirty trees; trap-based rollback to the starting branch on failure.
- `assets/ci/workflows/release-branch-guard.yml`: generalized `main-branch-guard.yml`;
  fails any push/PR to the release branch containing a dev-only path.
- `forge-ship` SKILL.md gains a short "clean-main promotion" step routing to the
  script when `dev_only_paths` is configured.

### D4. Consumers read the set from one place

`block-forge-in-main.sh` and the `pre-push` hook replace hardcoded `^docs/forge/`
grep with paths derived from `dev_only_paths`:

- pre-push / promote script: read `docs/forge/AI.md` from the local working tree
  (always the integration branch — fine).
- CI guard on the release branch: `docs/forge/AI.md` is stripped there by design,
  so the guard cannot read config from its own tree. Rule: if `docs/forge/AI.md`
  is absent, enforce the default set (`docs/forge/`); the workflow asset documents
  that projects extending `dev_only_paths` should mirror the list in the workflow
  env block (one documented duplication, flagged by bootstrap closeout).

### D5. Solo-governed + integration branch becomes first-class

- `AI.md` template comment changes from "omit integration_branch for solo" to:
  solo-simple/solo-governed omit it UNLESS running clean-main, where
  `integration_branch: dev` (or staging) is the documented pattern.
- `bootstrap/references/doc-minimums.md` solo-governed section gains a
  "Clean-Main Variant" subsection: task branches -> dev (integration) -> promote
  to main (release) via forge-promote.sh; SETUP.md records the model.
- Bootstrap asks one extra question for solo-governed/team-full: "Should the
  release branch stay free of FORGE governance files?" If yes: set
  `dev_only_paths`, offer to create the integration branch, copy promote script +
  guard workflow, record the promotion model in SETUP.md.

### D6. Version discoverability

- Add `skills/forge/VERSION` (single line, e.g. `1.7.0`), installed with the pack.
- `verify-repo.py` asserts VERSION == templates/AI.md `forge_version` == newest
  CHANGELOG.md entry, so the three cannot drift.
- NOT a frontmatter field: installers strict-parse SKILL.md frontmatter (1.7.0
  lesson) and unknown-key tolerance is not guaranteed.

### D7. hooksPath: document, do not default

`git config core.hooksPath ci/hooks` is offered in ci-setup docs as an option with
its trade-offs stated (per-clone config still required; disables `.git/hooks/`
entirely). Default install path stays `install-forge-hooks.sh`. CI remains the
durable backstop by design.

## Implementation plan (separate bounded tasks)

1. TASK-007: `dev_only_paths` config + consumer rewiring (block script, pre-push,
   validator awareness) + tests.
2. TASK-008: promote script + release-branch-guard workflow assets + forge-ship
   wiring + surface fallback line in the generator.
3. TASK-009: bootstrap clean-main question + doc-minimums/SETUP updates + VERSION
   file + verify-repo sync check.

Each lands with verify-repo fixtures (promotion dry-run fixture, guard
negative/positive, VERSION drift) and a CHANGELOG entry; ships in 1.8.0.

## Out of scope

- Moving governance to an orphan state branch (worktree model) — rejected earlier:
  breaks task/evidence-to-commit traceability.
- Auto-configuring provider branch protection — FORGE records, humans enforce.
