---
name: forge-critique
description: Run the FORGE critique pass for a completed or in-progress task. Use when checking for scope drift, undocumented assumptions, architecture conflicts, missing docs, or unaddressed failure modes before marking a task complete.
---

# FORGE Critique

Review the change strictly through the lens of bounded execution.

## Use When

- implementation exists and needs a scope, architecture, docs, or task-metadata review
- the user asks for a FORGE review before evaluation
- `forge-review` routes here as the first review gate

## Do Not Use When

- the user is asking for security checklist review only; use `forge-security-review`
- the user is asking whether evidence is sufficient for completion; use `forge-evaluation` after critique
- there is no selected task, issue, PR, MR, or change surface to review

## Checks

- Did the work exceed the selected task?
- Are assumptions and deferred issues explicit?
- Are edge cases or failure modes left unaddressed?
- Does the change conflict with architecture or documented constraints?
- If contract files are declared, were required OpenAPI, protobuf, schema, generated-client, or integration-boundary updates included?
- Were required docs updated?
- If `application_docs: true`, were the human-facing `docs/` files matching the task's triggers updated in scope? See `../references/application-docs.md` for the trigger map.
- If the task represents a significant architectural decision (framework choice, data store change, trust boundary, major component replacement) and `application_docs: true`, was a new `docs/adr/NNNN-<slug>.md` proposed? Routine refactors and bug fixes do not need ADRs.
- In team mode, do branch, claim, and file-scope records still match the actual work?
- For issue-backed task sources, does the PR/MR link the issue, does the branch or title identify the ticket, and does the current assignee/label state match project policy?

## Output

Produce a concise pass/fail style critique with:

- blocking findings
- non-blocking notes
- whether the task may proceed to security review and evaluation
- whether the task metadata remains consistent for a PR-based merge
- whether contract artifacts and external tracker links are consistent
- if `requires_independent_review: true`, note that critique is complete but evaluation must still be performed by a human reviewer or a separate agent session

## Hard Stops

Stop when:

- no task or change surface is identifiable
- changed files exceed declared scope without explicit approval
- a required contract, ADR, XPD, application doc, or task-source update is missing
- branch, claim, issue, PR, or MR metadata conflicts with project policy

## Rationalizations To Reject

| Rationalization | FORGE response |
|---|---|
| "CI passed, so critique is done." | CI is evidence; critique checks scope, assumptions, and governance consistency. |
| "The extra refactor is harmless." | Unscoped refactors are findings unless approved by the task. |
| "Docs can wait for a follow-up." | Required docs are part of the same task when triggers fire. |
| "The issue title is close enough." | Task metadata must match the actual branch, files, and PR/MR surface. |

## Evidence Required

- reviewed task, issue, PR, MR, or diff reference
- blocking findings or explicit pass
- contract, docs, tracker, and branch metadata consistency result
- whether the task may proceed to security review and evaluation

Keep the critique short. Prefer a few findings over a narrative review.
Use findings-first output. Avoid explanatory recap when a short finding line is enough.

If there are blocking issues, stop rather than softening the conclusion.
