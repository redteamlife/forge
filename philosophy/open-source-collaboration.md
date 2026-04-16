# Open Source Collaboration Proposal

This document proposes an evolution of the FORGE tool workflow for projects that want both private governance and healthy public collaboration.

The current dual-repo model works well when the public repository is a release target only. It is weaker when the public repository is also a true contribution surface for outside pull requests. The goal of this proposal is to preserve FORGE governance while making public contribution a first-class workflow.

## Problem

Today, the open-source tool workflow assumes:

- development happens in the private dev repo
- the public repo is a release target
- `forge-publish` replaces public `main` from `release_dir`

That creates two issues for collaborative projects:

1. Accepted public pull requests must be manually brought back into the private dev repo.
2. Re-publishing from private dev can flatten public history and dilute contributor attribution.

For redteam.life, that is a mismatch. Education, collaboration, and open contribution need to be supported directly by the workflow.

## Design Goals

- Keep private FORGE governance docs and planning artifacts private.
- Keep public contribution easy and normal for outside collaborators.
- Preserve contributor attribution and merged PR history in the public repo.
- Make public-to-private intake simple enough to be routine.
- Keep the workflow explicit and teachable for teams adopting FORGE.

## Proposal Summary

Add two new concepts to the FORGE tool workflow:

1. A `publish_strategy` field in `forge.yaml`
2. A dedicated public-intake workflow and helper script

### Proposed `forge.yaml` field

```yaml
visibility: open-source
publish_strategy: preserve-history
```

Allowed values:

- `snapshot-force-push`
- `preserve-history`

### Meaning

`snapshot-force-push`

- Current behavior.
- Best for maintainer-only public repos.
- Public `main` is treated as a release artifact branch.
- Outside PRs should not be the primary contribution path.

`preserve-history`

- New collaborative behavior.
- Best for community-facing open-source tools.
- Public `main` is treated as a normal shared source branch.
- `forge-publish` must publish on top of public history, not replace it.
- Public PR history and contributor attribution remain visible.

## Proposed Workflow

### Public contribution flow

1. Contributor opens a PR against the public repo.
2. Maintainer reviews and merges the PR in the public repo.
3. Maintainer runs a new intake command in the private dev repo.
4. FORGE creates an intake task and imports the accepted change.
5. The team validates the change under private FORGE governance.
6. Future publishes preserve the public commit graph instead of replacing it.

### Private intake flow

Add a new helper script:

- `scripts/forge-sync-public.sh`
- `scripts/forge-sync-public.ps1`

Suggested usage:

```bash
./scripts/forge-sync-public.sh --pr 123
```

Or:

```bash
./scripts/forge-sync-public.sh --merge-commit <sha>
```

What it should do:

1. Fetch the `public` remote.
2. Verify the target PR is merged.
3. Identify the merge commit or accepted commit range.
4. Create a local intake branch from the current private dev branch.
5. Cherry-pick or merge the accepted public change into private dev.
6. Create or append a task in `docs/forge/TASKS.yaml`, such as `intake-public-pr-123`.
7. Record provenance in commit trailers and optionally `MEMORY.md`.

Example commit trailers:

```text
Source-PR: public#123
Source-Repo: redteamlife/toolname
FORGE-task: intake-public-pr-123
```

## Proposed `forge-publish` behavior

### For `snapshot-force-push`

No change from current behavior.

### For `preserve-history`

`forge-publish` should change its open-source behavior:

1. Fetch `public/main`.
2. Materialize `release_dir` from `src_dir`.
3. Overlay `release_dir` onto a working copy rooted at `public/main`.
4. Commit only the actual file changes on top of existing public history.
5. Push normally to `public/main`.
6. Never force-push `main`.

That keeps:

- public PR merge history
- contributor authorship
- GitHub attribution
- normal open-source auditability

The public repo remains clean because only `release_dir` content is synced, but it is no longer treated as disposable history.

## Governance Rules

To keep the workflow disciplined, add the following policy for `preserve-history` projects:

- Public PRs may be merged only through the public repo's standard review flow.
- Every accepted public PR must be imported into private dev through the intake workflow.
- Private validation remains authoritative before the next governed release.
- Publish must fail if private dev is behind public `main` and the missing commits have not been acknowledged or imported.

That last rule matters. It prevents maintainers from accidentally overwriting or bypassing public work during the next publish.

## Documentation Changes Proposed

If this proposal is accepted, FORGE should update:

- `skills/forge/assets/templates/AI.md`
- `skills/forge/tool-workflow/SKILL.md`
- `GETTING_STARTED.md`
- `README.md`

The tool workflow docs should explicitly present two open-source patterns:

1. Maintainer-only release mirror
2. Collaborative public source repo

## Recommended Default

For open-source tools intended to accept outside PRs, the default should become:

```yaml
visibility: open-source
publish_strategy: preserve-history
```

For private teams publishing outward but not accepting code contributions, `snapshot-force-push` remains valid.

## Migration Plan

Projects using the current open-source workflow can migrate in phases:

1. Add `publish_strategy: preserve-history` to `forge.yaml`.
2. Configure the `public` remote in the private dev repo if not already present.
3. Stop force-pushing public `main`.
4. Start importing accepted public PRs through the new intake workflow.
5. Update `TOOL_WORKFLOW.md` so contributors and maintainers know the expected process.

## Why This Fits FORGE

FORGE is not just about control. It is about legible, governed collaboration.

This proposal keeps the private governance layer intact while making the public contribution path real instead of second-class. That aligns with the redteam.life values of education, collaboration, and communication:

- contributors get a normal open-source experience
- maintainers keep a disciplined private validation path
- project history stays understandable in both repos

## Recommended Next Step

Implement this in two phases:

1. Documentation and schema update
2. Script support for `preserve-history` publish and public-intake automation

The documentation should land first so the model is explicit before the tooling changes.
