# FORGE Lifecycle Map

Use this reference when routing user intent by delivery lifecycle rather than
by exact FORGE subskill name.

FORGE remains skills-first and explicit. Lifecycle names are routing aids, not
new always-on behavior.

## Lifecycle Routes

| User intent | Public route | Underlying workflow |
|---|---|---|
| Define project workflow | `forge-bootstrap` | Create or refresh repo-local FORGE docs. |
| Plan task work | `forge-plan` | Shape bounded tasks in the authoritative task source. |
| Build task | `forge-build` | Delegate implementation to `forge-execute-task`. |
| Review task | `forge-review` | Run `forge-critique`, required `forge-security-review`, then `forge-evaluation`. |
| Secure task | `forge-security-review` | Apply task-relevant security and DevSecOps checks. |
| Verify task | `forge-evaluation` | Decide whether completion evidence is sufficient. |
| Ship task | `forge-ship` | Confirm integration, release acceptance, and claim release. |
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
