# Cross-Project Coordination

This directory is the authority repo's FORGE coordination surface for repos
that share contracts, releases, or cross-repo decisions.

## Roles

- `authority`: owns these docs and makes final calls on authority-owned
  contracts.
- `peer`: proposes changes and reviews XPDs that affect it.
- `downstream`: consumes outputs and flags launch or user-facing blockers.

## Reading Order

1. `COORDINATION.yaml`
2. Relevant files in `contracts/`
3. Active files in `decisions/`
4. New proposals in `inbox/`
5. Background material in `concepts/`

## Protocol

- Authority-owned shared contracts are changed through XPDs.
- Peer repos propose changes through inbox drafts.
- XPDs that list `review_requested_from` pause until those repos review or a
  human owner explicitly overrides the pause.
- `COORDINATION.yaml` tracks open cross-project movement; task execution still
  uses the repo's normal FORGE task source.
