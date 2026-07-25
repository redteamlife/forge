---
name: forge-cross-project
description: Bootstrap and maintain opt-in FORGE cross-project coordination docs for multi-repo projects with shared contracts, authority repos, peer repos, downstream repos, XPDs, and inbox proposals.
---

# FORGE Cross-Project

Use this skill only when the user explicitly asks for multi-repo,
cross-project, authority-repo, sister-repo, shared-contract, or XPD
coordination.

Do not load or apply this workflow during normal `solo-simple`,
`solo-governed`, or `team-full` work unless the project-local docs already
declare cross-project coordination.

## Use When

- the user asks for multi-repo, cross-project, authority-repo, peer-repo,
  downstream, sister-repo, shared-contract, inbox, or XPD coordination
- a repo already declares `docs/forge/cross-project/`
- an authority-owned contract change needs affected repo review

## Do Not Use When

- normal single-repo team mode is sufficient
- the repo only needs `contract-first` local contract discipline
- no repo can act as authority and the user has not chosen a federation model

## Covers

- authority, peer, and downstream repo roles
- `docs/forge/cross-project/` scaffolding
- cross-repo coordination ledger entries
- contract documents for authority-owned shared shapes
- XPD records for cross-project decisions
- inbox drafts from peer repos
- agent-surface pointers from peer or downstream repos to the authority repo

## Read On Demand

- `../references/cross-project.md`

Use templates from `../assets/cross-project/templates/` when creating or
refreshing cross-project docs.

## Workflows

### Initialize Authority Repo

When the user asks to initialize the current repo as the authority repo:

1. Read `../references/cross-project.md`.
2. Create `docs/forge/cross-project/`.
3. Copy the authority-repo templates from `../assets/cross-project/templates/`.
   Exclude `sister-repo-pointer.md` unless adding a peer or downstream pointer.
4. Fill project-specific repo names, owner fields, and dates when known.
5. Keep `COORDINATION.yaml` as the cross-project ledger, not a replacement for
   the task source or issue tracker.
6. Add a short pointer in `docs/forge/AI.md` only when that file exists.
7. Add `docs/forge/cross-project/README.md` to root agent-surface reading
   order only when those surfaces already exist.

### Create XPD

When the user asks for a new cross-project decision:

1. Find the next `XPD-NNNN` number under
   `docs/forge/cross-project/decisions/`.
2. Create `XPD-NNNN-<slug>.md` from the XPD template.
3. Set status to `draft` unless the user explicitly says otherwise.
4. Add or update the matching entry in `COORDINATION.yaml`.
5. If a contract shape changes, link the affected contract doc from the XPD.

### Draft Inbox Proposal

When working from a peer repo:

1. Create an inbox draft from `inbox/draft-template.md`.
2. Record the originating repo, requested change, affected contracts, and open
   questions.
3. Do not edit authority-owned contract docs directly from the peer repo unless
   the user explicitly instructs that this repo is also the authority.

### Add Sister Repo Pointer

When adding cross-project awareness to a peer or downstream repo:

1. Prefer existing agent-surface files such as `AGENTS.md`, `CLAUDE.md`,
   `.github/copilot-instructions.md`, Cursor rules, Codex hooks, or Windsurf
   rules.
2. Insert a compact pointer based on `sister-repo-pointer.md`.
3. Include the authority repo location, reading order, and any specific XPD or
   contract docs the repo must check.
4. Keep the pointer explicit and non-blocking; do not make FORGE always-on.

## Hard Stops

Stop and ask for a human decision when:

- no authority repo is identifiable
- two repos claim authority for the same contract
- a peer repo proposes a breaking contract change without an XPD
- an XPD lists a repo in `review_requested_from` and that repo has not reviewed
- a project needs a federation model rather than authority-led coordination

## Rationalizations To Reject

| Rationalization | FORGE response |
|---|---|
| "The peer repo can just patch the contract." | Authority-owned contracts change through the authority workflow. |
| "This breaking change is obvious." | Breaking or externally visible changes require XPD traceability. |
| "We can notify sister repos after merge." | XPDs pause for listed affected repo review before acceptance. |
| "The inbox draft is already a decision." | Inbox drafts are proposals until elevated by the authority repo. |

## Evidence Required

- authority, peer, or downstream role recorded or explicitly confirmed
- `COORDINATION.yaml` entry for active cross-project movement
- linked XPD, inbox draft, contract doc, PR/MR, or issue artifact
- review status for repos listed in `review_requested_from`
- updated agent-surface pointer when adding a peer or downstream repo
