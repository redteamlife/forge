# FORGE Maturity Model

This maturity model describes progressive adoption of disciplined agentic engineering practices using FORGE. Teams can operate at any level, but higher levels require stronger documentation quality, execution controls, and evaluation rigor.

## Summary

| Level | Name | Key Characteristic |
| --- | --- | --- |
| 0 | Ad Hoc Prompting | Unstructured, high variability |
| 1 | Structured Docs | `AI.md`, `TASKS.yaml`, explicit task tracking |
| 2 | Architecture Discipline | Trade-offs, trust boundaries documented |
| 3 | Evaluation Gates | Explicit completion gates, security review |
| 4 | Controlled Batch Execution | Bounded multi-task with per-task enforcement |
| 5 | Full Disciplined Orchestration | Deterministic end-to-end, auditability, operational learning |

## Level 0 - Ad Hoc Prompting

### Characteristics

- Work is driven by unstructured prompts.
- Requirements, constraints, and acceptance criteria are implicit or missing.
- Architecture decisions are made reactively and are not documented.
- Reviews are inconsistent and depend on individual habits.

### Typical Outcomes

- Fast short-term iteration on small tasks.
- High variability in quality and repeatability.
- Weak traceability for decisions and changes.

### Primary Risks

- Scope drift
- Regressions
- Security oversights
- Inconsistent commit hygiene

## Level 1 - Structured Docs

### Characteristics

- Core project documentation exists and is referenced during execution.
- Task tracking is explicit (for example, via `TASKS.yaml`).
- AI-facing instructions are documented in `AI.md`.
- Definition of scope and constraints begins to stabilize.

### Typical Outcomes

- Improved consistency in task execution.
- Better collaboration between humans and agents.
- Reduced ambiguity for routine tasks.

### Primary Risks

- Documentation may become stale.
- Enforcement is still mostly manual.
- Reviews may remain uneven.

## Level 2 - Architecture Discipline

### Characteristics

- Architecture exploration and architecture documentation are maintained.
- Decisions include trade-offs, risks, and rationale.
- Changes are checked against architectural alignment.
- Trust boundaries and deployment assumptions are identified.

### Typical Outcomes

- Better long-term maintainability.
- Stronger design coherence across iterations.
- Reduced rework caused by local optimizations.

### Primary Risks

- Architecture artifacts may be produced but not enforced.
- Teams may over-document without clear decision closure.

## Level 3 - Evaluation Gates

### Characteristics

- Explicit evaluation criteria define release and task readiness.
- Security review and quality checks are part of the workflow.
- Testing expectations are documented and mode-aware.
- Completion requires passing documented gates, not just code changes.

### Typical Outcomes

- Higher confidence in task completion quality.
- Clearer accountability for risk acceptance.
- Better operational readiness before merge or release.

### Primary Risks

- Gate definitions may be too vague or too strict.
- Teams may bypass evaluation under time pressure unless enforced.

## Level 4 - Controlled Batch Execution

### Characteristics

- Multiple tasks may be executed in bounded batches under explicit rules.
- Batch size and sequencing are documented and controlled.
- Evaluation and commit discipline are enforced per task within a batch.
- Hard stop conditions prevent uncontrolled continuation.

### Typical Outcomes

- Higher throughput with maintained discipline.
- Better use of agentic execution for low-coupling work.
- Improved traceability across related task sequences.

### Primary Risks

- Hidden task coupling can invalidate batch assumptions.
- Batch execution can amplify errors if validation is weak.

## Level 5 - Full Disciplined System Orchestration

### Characteristics

- End-to-end execution is governed by mode, documented constraints, and explicit gates.
- Task selection, implementation bounds, review passes, evaluation, and memory updates are deterministic.
- Escalation policies and branch discipline are enforced.
- Operational learning is captured and fed back into guardrails.

### Typical Outcomes

- Repeatable engineering workflows across teams and projects.
- Strong auditability and change control.
- Sustainable agentic collaboration in enterprise contexts.

### Primary Risks

- Process complexity can slow delivery if not calibrated to context.
- Governance artifacts require maintenance discipline to remain effective.

## Advancement Guidance

Teams should advance one level at a time. Progress should be based on demonstrated operating behavior, not document existence alone. A higher maturity claim is valid only when the team consistently follows the corresponding controls during real project execution.
