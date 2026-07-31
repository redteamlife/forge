# FORGE Application Docs

Use this reference when a project enables `application_docs: true` in
`docs/forge/AI.md`.

Application docs are **human-facing** delivery and operational documentation,
parallel to FORGE's agent-facing governance docs. They live in `docs/`
(separate from `docs/forge/`).

## Audience Split

| Audience | Path | Examples |
|---|---|---|
| Agent execution | `docs/forge/` | AI.md, task ledger, EVALUATION.md, MEMORY.md, ARCHITECTURE.md (agent-facing constraints) |
| Human delivery / ops | `docs/` | tool-overview.md, architecture-overview.md, threat-model.md, developer-guide.md, interfaces-and-protocols.md, deployment-playbook.md, incident-runbook.md, adr/ |

`docs/forge/ARCHITECTURE.md` and `docs/architecture-overview.md` are
intentionally separate. The first is agent-facing constraints and contract
files. The second is the human-facing system explanation.

## Default Set By Profile

Bootstrap generates only the docs that match the configured profile and
security_profile. Each profile is additive.

| Profile | Always | Adds |
|---|---|---|
| `solo-simple` | tool-overview, developer-guide, adr/ | — |
| `solo-governed` | (above) | architecture-overview, interfaces-and-protocols, deployment-playbook, incident-runbook |
| `team-full` | (above) | — |
| `security_profile >= repo-fortress` | | threat-model |

## Maintenance Triggers

Each doc has a clear update trigger. Agents update the matching doc in the
same task, PR, or MR that triggers the change. `forge-execute-task` checks
this; `forge-critique` flags missing updates; `forge-evaluation` requires
the matching doc to be touched in-scope when the trigger fires.

| Task touches... | Update doc |
|---|---|
| API, schema, generated client, wire format, contract files | `docs/interfaces-and-protocols.md` |
| New component, trust boundary, major dependency, deployment topology | `docs/architecture-overview.md` |
| Build, test, local-dev, release process, code conventions | `docs/developer-guide.md` |
| New attack surface, sensitive data flow, post-incident hardening | `docs/threat-model.md` |
| Deployment process, environment, rollout, rollback | `docs/deployment-playbook.md` |
| Newly observed failure mode, alert, runbook step | `docs/incident-runbook.md` |
| Significant architectural decision | new `docs/adr/NNNN-<slug>.md` |
| Project bootstrap, ownership change, major reframe | `docs/tool-overview.md` |

When no trigger fires, application docs do not need to change. This keeps
updates targeted instead of ceremonial.

## ADR Handling

ADRs are per-decision rather than living docs. When a task represents a
significant architectural decision, propose a new ADR by:

1. Creating `docs/adr/NNNN-<slug>.md` from the template, where NNNN is the
   next zero-padded number.
2. Setting Status to `Proposed` initially.
3. Recording context, decision, options considered, consequences, follow-up.
4. Linking the ADR from `docs/architecture-overview.md` if it materially
   changes the system shape.

Routine refactors, bug fixes, and small features do not need ADRs.

## Diagrams

Default to **Mermaid** for any diagram embedded in application docs
(architecture, sequence, state, deployment, data flow, threat-model trust
boundaries, runbook decision flows, etc.). Mermaid keeps diagrams in plain
text alongside the prose, renders natively on GitHub/GitLab, and stays
diffable in PRs.

- Use fenced ` ```mermaid ` blocks. Do not embed binary images, drawio
  exports, or screenshot diagrams when a Mermaid equivalent is feasible.
- Pick the chart type that fits: `flowchart` for component/data flow,
  `sequenceDiagram` for request/response and protocol exchanges,
  `stateDiagram-v2` for lifecycle, `erDiagram` for data models,
  `C4Context`/`C4Container` for system context when supported by the
  renderer the project uses.
- Keep diagrams small and scoped to one concept; prefer multiple focused
  diagrams over one omnibus diagram.
- Only fall back to another tool (PlantUML, drawio, image asset) when
  Mermaid genuinely cannot express the diagram (e.g., complex network
  topologies). Note the reason in the doc when you do.

## Layout: flat or handbook

`docs_format` (in `docs/forge/AI.md`) selects the layout under `docs_root`
(default `docs/handbook`):

- `flat` (migration default): docs live directly under `docs_root`.
- `handbook` (recommended for new projects): docs live in target-neutral
  semantic folders — `overview/`, `system/`, `software/`, `interfaces/`,
  `operations/`, `troubleshooting/`, `adr/` — with a `README.md` whose ordered
  link list is the single navigation manifest. Do NOT use numbered folder
  prefixes; ordering lives in the README, not in filenames.

## Frontmatter

Core schema (enums fixed; `x-*` extension keys allowed):

```
---
title: <doc title>
slug: <kebab-case>
doc_type: overview | system | software | interface | operations | troubleshooting | adr
owners: [name, name]
created: YYYY-MM-DD
updated: YYYY-MM-DD          # content changed
reviewed_at: YYYY-MM-DD      # a human confirmed it is still correct
review_in_days: 90
status: draft | active | deprecated | archived
tags: [tag, tag]
sensitivity: public | internal | confidential | restricted
---
```

`updated` and `reviewed_at` are distinct: a mechanical edit bumps `updated` but
must not reset the review clock; a no-change review bumps `reviewed_at`.
Staleness is `reviewed_at + review_in_days` in the past — reported by
`assets/scripts/forge_docs_staleness.py` and surfaced at release preparation.

`sensitivity` is an ordered lattice (`public < internal < confidential <
restricted`) that gates publication (see `forge_docs_export.py`); missing values
are treated as `restricted` (fail closed). Never strip `sensitivity` on export.
