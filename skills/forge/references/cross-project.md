# FORGE Cross-Project Coordination

Use this reference when a multi-repo project needs explicit coordination for
shared contracts, cross-repo decisions, or agent work spanning repositories.

Cross-project coordination is opt-in. Do not apply it to ordinary single-repo
team mode.

## Goals

- make authority for shared contracts explicit
- avoid silent drift between repos that depend on the same shape
- give peer repos a standard proposal path
- pause breaking changes until affected repos review them
- keep cross-project state lightweight, diffable, and agent-readable

## Roles

| Role | Description | Powers |
|---|---|---|
| `authority` | Repo that owns the shared coordination docs and final contract decisions. | Maintains contracts, elevates inbox drafts to XPDs, promotes XPD status. |
| `peer` | Repo that implements or depends on shared contracts and can shape them. | Proposes changes through inbox drafts and reviews XPDs that affect it. |
| `downstream` | Repo that consumes outputs but does not shape contracts. | Tracks launch-impacting changes and flags blockers. |

If no repo can act as authority, stop and document that the project needs a
federated coordination model. Do not force authority-led rules onto equal peers.

## Directory Shape

In the authority repo:

```text
docs/forge/cross-project/
├── README.md
├── COORDINATION.yaml
├── contracts/
│   ├── README.md
│   └── <contract>.md
├── decisions/
│   └── XPD-NNNN-<slug>.md
├── inbox/
│   └── <repo>-<slug>.md
└── concepts/
    └── README.md
```

`COORDINATION.yaml` is a cross-project ledger. It complements, but does not
replace, `docs/forge/TASKS.yaml`, GitHub Issues, GitLab Issues, or another
configured task source.

## Coordination Config

When a repo opts into cross-project coordination, record the minimum useful
fields in `docs/forge/AI.md` if that file exists:

```yaml
cross_project_role: authority | peer | downstream
cross_project_authority: <repo URL or path>
cross_project_docs: docs/forge/cross-project/
cross_project_reviews_required: true
```

Use these fields as routing hints only. Project-local instructions and human
direction still take precedence.

## COORDINATION.yaml

Each entry should include:

- `id`: stable identifier, usually matching an XPD id or inbox draft id
- `status`: `draft` | `proposed` | `review_requested` | `accepted` |
  `implemented` | `blocked` | `superseded`
- `owner`: repo or person responsible for next movement
- `affects`: repos or surfaces affected by the change
- `review_requested_from`: peer repos that must review before acceptance
- `summary`: one compact sentence
- `artifacts`: related XPDs, contracts, PRs, issues, or inbox drafts
- `open_questions`: unresolved decisions

Entries should stay short. Put durable reasoning in XPDs or contract docs.

## Contract Docs

Contract docs describe authority-owned shapes other repos depend on. Examples:

- OpenAPI, AsyncAPI, GraphQL, protobuf, or JSON schema
- generated client package shape
- event or message schemas
- plugin manifests
- data exchange formats
- endpoint compatibility promises

Each contract doc should include:

- authoritative source files
- current shape summary
- stability promise
- compatibility expectations
- change protocol
- linked XPDs

Repos must not change authority-owned shared contracts unilaterally. Breaking
or externally visible contract changes require an XPD unless project policy
explicitly allows a smaller path.

## XPDs

XPD means Cross-Project Decision. Use XPDs like ADRs, but scoped to decisions
that affect more than one repository.

Recommended lifecycle:

- `draft`: being written
- `proposed`: ready for affected repo review
- `review_requested`: waiting on listed repos
- `accepted`: approved by the authority repo
- `implemented`: accepted decision has landed in affected repos
- `superseded`: replaced by a later XPD

Each XPD should include:

- frontmatter with `id`, `title`, `status`, `owner`, `affects`,
  `review_requested_from`, and `created`
- context
- decision
- affected contracts
- per-repo impact
- open questions
- rollout and compatibility notes

When an XPD lists repos in `review_requested_from`, the authority repo should
not promote it to `accepted` until those repos have reviewed or the human owner
explicitly overrides the pause.

## Inbox

Peer repos propose changes by sending inbox drafts to the authority repo. An
inbox draft is not authoritative until the authority repo accepts it and, when
needed, promotes it to an XPD.

Authority repo outcomes:

- accept and elevate to XPD
- request revision
- reject with a short reason
- move to concepts when the idea is useful but not ready

## Concepts

Concept docs hold fuzzy ideas and future shapes. They are allowed to be rough.
They do not change contracts and do not impose obligations on peer repos.

Concept lifecycle:

- stay as background context
- promote to inbox or XPD
- delete when obsolete

## Agent-Surface Pointers

Peer and downstream repos should include a compact pointer in their agent
surface files when cross-project coordination applies.

Reading order:

1. Authority repo `COORDINATION.yaml`
2. Relevant contract docs
3. Active XPDs affecting the current repo
4. Current repo's local FORGE docs and task source

Keep pointers explicit and short. They remind agents where to look; they do not
turn FORGE into always-on behavior.

## Validation Guidance

Useful future validators:

- every XPD has required frontmatter
- every `COORDINATION.yaml` artifact path exists
- every contract doc has a change protocol
- every contract change references an XPD or explicit exception
- peer repos configured in authority coordination docs have an agent-surface
  pointer

Treat validators as optional enforcement. The document workflow is the MVP.
