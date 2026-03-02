# FORGE Execution Model

This document explains the reasoning behind the FORGE execution workflow. It is human-facing. Agents do not need to read it. The authoritative runtime rules live in `FORGE.md` in the target project's `docs/FORGE/` directory.

## Why Documentation Governs Execution

AI agents working without explicit constraints tend to expand scope, make undocumented architectural decisions, and produce changes that are difficult to trace or reverse. The documentation-first approach addresses this by making the project's intent, constraints, and architecture legible to the agent before it acts. The agent is not trusted to infer scope from the codebase alone.

The contract is: the agent reads the documents, the documents define what is allowed, and the agent stops when the documents are silent or conflicted.

## Why FORGE.md Is the Execution Authority

Putting the workflow in a dedicated document rather than embedding it in `AI.md` or splitting it across files serves one purpose: conflict resolution. When a task description, an architectural constraint, and a project preference point in different directions, there must be a single authority. `FORGE.md` is that authority. Any other document can inform execution; only `FORGE.md` governs it.

## Why Document Presence Is Checked Before Content Is Read

Existence checks are cheap. Content loading is the token cost. Validating that all required documents are present before task selection prevents mid-task hard stops that waste work already done. Reading document content only when the workflow step that needs it is reached avoids loading documents that are not relevant to the selected task.

## Why Memory Is Queried Before Alignment Check

The order matters. Querying `MEMORY.md` before the pre-implementation alignment check means that any recorded failures, risk patterns, or guardrail lessons can inform how the agent interprets the architecture alignment. A prior failure on a similar component might change what the alignment check flags as uncertain. If the order were reversed, memory would be consulted after the agent had already framed the implementation approach.

## Why Critique and Security Are Separate Passes

Critique is scope-focused: did the implementation stay within task bounds, are assumptions documented, are edge cases considered? Security review is boundary-focused: does the change affect trust boundaries, permissions, or sensitive data handling? Combining them risks the scope concerns crowding out the security concerns. Keeping them separate ensures both lenses are applied and both outcomes are recorded distinctly.

## Why Hard Stops Are Unconditional

Hard stops exist to prevent the agent from making judgment calls in situations where the documentation is ambiguous, missing, or conflicted. Allowing the agent to proceed on its own judgment in these situations defeats the purpose of the governance model. The cost of stopping is low: the human resolves the issue and restarts. The cost of proceeding incorrectly can include compounded scope drift, architectural violations, or undetected security regressions. Unconditional stops keep the human in the loop at precisely the moments when human judgment is most needed.

## Why Commit-Per-Task Is Enforced

Bundling multiple task changes into a single commit makes it difficult to:

- Attribute specific behavior changes to specific tasks
- Revert a failing task without reverting unrelated work
- Audit what gate outcomes applied to what changes

One task, one commit makes the history an accurate record of what was done and what was validated. The structured commit message format reinforces this by making task identity and mode visible directly in the log.

## Why Auto Mode Is Available at Any Mode Level

Auto mode allows the agent to iterate across tasks without human reinvocation. Rather than restricting auto mode to higher governance levels, FORGE relies on hard stops to contain risk at any mode. If a gate fails, a document is missing, or a security concern is identified, execution halts unconditionally regardless of execution mode. The hard stop rules are the safety envelope - not the mode level. Teams operating at Lightweight with auto mode accept that fewer gates are enforced; the appropriate response is to match mode to actual risk tolerance, not to restrict the execution model.

## Why Escalation Stops Execution Rather Than Continuing

Escalation is not a warning - it is a stop condition. When the agent cannot proceed safely or deterministically, continuing produces output that cannot be validated against the documented requirements. Recording the escalation and stopping is always cheaper than implementing something that later needs to be unwound. The escalation record also serves as feedback: repeated escalations on the same condition indicate a gap in the project's documentation that should be closed.

## Why Modes Are Additive

Each mode includes the requirements of all modes below it. This means a team operating at Strict is also operating at Mid and Lightweight - they do not skip the base controls. Additive modes prevent gaps created by jumping to a higher governance level without establishing the foundational controls. Teams advancing through modes should verify that lower-level controls are already working before layering on additional requirements.

## Why Task Fields Are Optional at Lower Modes

Requiring `acceptance_criteria` and `scope_boundary` for every task at every mode would add authoring overhead that is disproportionate to the governance benefit at Lightweight or Mid. The value of these fields increases with task complexity and blast radius - exactly the conditions that Strict and Full Discipline are designed for. Making them optional at lower modes preserves the low-friction entry point that allows teams to adopt FORGE incrementally. The fields are visible in the schema so teams can adopt them voluntarily before the mode requires them.
