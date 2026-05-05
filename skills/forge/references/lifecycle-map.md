# FORGE Lifecycle Map

Use this reference when routing user intent by delivery lifecycle rather than
by exact FORGE subskill name.

FORGE remains skills-first and explicit. Lifecycle names are routing aids, not
new always-on behavior.

## Lifecycle Routes

| User intent | Route | Purpose |
|---|---|---|
| Define project workflow | `forge-bootstrap` | Create or refresh repo-local FORGE docs. |
| Plan task work | task source, `TASKS.yaml`, or issue tracker | Shape bounded tasks before execution. |
| Build task | `forge-execute-task` | Implement one selected task with scope and branch discipline. |
| Review task | `forge-critique` | Check scope drift, assumptions, architecture, docs, and contract consistency. |
| Secure task | `forge-security-review` | Apply task-relevant security and DevSecOps checks. |
| Verify task | `forge-evaluation` | Decide whether completion evidence is sufficient. |
| Ship task | team closeout and release reconciliation | Confirm integration, release acceptance, and claim release. |
| Coordinate repos | `forge-cross-project` | Manage authority, peer, downstream, contract, XPD, and inbox workflows. |

## Prompt Patterns

- `Use forge to define this repo's workflow.`
- `Use forge to plan the next bounded task.`
- `Use forge to build the next task.`
- `Use forge to review this task.`
- `Use forge to verify completion.`
- `Use forge to ship or reconcile this task.`
- `Use forge-cross-project to coordinate this multi-repo contract change.`

## Guardrails

- Planning does not replace task-source state.
- Building does not include review or evaluation unless the user explicitly asks
  for an end-to-end pass and the project policy allows it.
- Review is not the same as security review.
- CI passing is not the same as evaluation.
- Shipping requires observable integration or release acceptance, not just a
  local commit.
