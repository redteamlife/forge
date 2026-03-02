# FORGE Modes

FORGE modes define the minimum documentation requirements, enforcement strength, and execution boundaries for agentic work. Teams should choose the lowest mode that safely supports the risk and complexity of the task.

## Mode Summary

| Mode | Required Documents | Appropriate Use |
| --- | --- | --- |
| Lightweight | `AI.md`, `FORGE.md`, `TASKS.yaml` | Low-risk changes, early setup, small refactors |
| Mid | + `ARCHITECTURE.md`, `TEST_STRATEGY.md`, `EVALUATION.md`, `MEMORY.md` | Most product engineering, moderate-risk features |
| Strict | + `ARCHITECTURE_EXPLORATION.md`, `REVIEW_GUIDE.md`, `ROADMAP.md` | Security-sensitive systems, audit requirements |
| Full Discipline | All Strict documents + org governance artifacts | Regulated environments, high-impact production systems |

## Lightweight

### Required Documentation

- `AI.md`
- `FORGE.md`
- `TASKS.yaml`

### Enforcement Profile

- Basic task selection and bounded implementation.
- Manual validation of scope and constraints.
- Review and test checks may be concise but must be recorded.
- Commit discipline required for completed tasks.

### Appropriate Use

- Low-risk changes
- Early project setup work
- Small refactors with low blast radius

## Mid

### Required Documentation

- `AI.md`
- `FORGE.md`
- `TASKS.yaml`
- `ARCHITECTURE.md`
- `TEST_STRATEGY.md`
- `EVALUATION.md`
- `MEMORY.md`

### Enforcement Profile

- Required architecture alignment checks.
- Required critique pass and security review pass.
- Explicit evaluation gate before task completion.
- Batch execution allowed only when configured and bounded.

### Appropriate Use

- Most product engineering work
- Moderate-risk feature development
- Maintenance requiring consistency and review discipline

## Strict

### Required Documentation

- `AI.md`
- `FORGE.md`
- `TASKS.yaml`
- `ARCHITECTURE_EXPLORATION.md`
- `ARCHITECTURE.md`
- `REVIEW_GUIDE.md`
- `TEST_STRATEGY.md`
- `EVALUATION.md`
- `MEMORY.md`
- `ROADMAP.md`

### Enforcement Profile

- Formal validation of required documents before execution.
- Task execution must satisfy review, security, and evaluation gates with recorded outcomes.
- Batch execution requires explicit `batch_size` and task independence justification.
- Auto execution may be permitted only if configured and policy-compliant.

### Appropriate Use

- Security-sensitive systems
- Shared platforms and core infrastructure
- Projects with strong audit or change-control requirements

## Full Discipline

### Required Documentation

- All Strict mode documents, maintained and current.
- Additional organizational governance artifacts as required by policy (outside FORGE scope).

### Enforcement Profile

- Deterministic execution workflow enforced for every task.
- Strong hard-stop behavior on missing documentation, failed gates, or branch violations.
- Mandatory memory updates and guardrail refinement tracking.
- Auto execution allowed only under explicit policy and only for eligible task classes.

### Appropriate Use

- Regulated environments
- High-impact production systems
- Multi-team programs requiring formal operational governance

## Enforcement Differences

### Documentation Validation

- `Lightweight`: Minimal set validated.
- `Mid`: Core engineering docs validated.
- `Strict`: Full project operating docs validated.
- `Full Discipline`: Strict validation plus organizational policy checks as applicable.

### Execution Control

- `Lightweight`: Primarily manual, tightly bounded.
- `Mid`: Manual or bounded batch.
- `Strict`: Manual, batch, or limited auto with stronger gates.
- `Full Discipline`: Fully governed execution with explicit policy controls.

### Review and Evaluation

- `Lightweight`: Concise review and test confirmation.
- `Mid`: Required critique, security, and evaluation gates.
- `Strict`: Formalized review evidence and gate outcomes.
- `Full Discipline`: Enforced gate records and risk escalation discipline.

## Escalation Guidance

Escalation is appropriate when any of the following occurs:

- The task conflicts with documented scope, constraints, or architecture.
- A required document is missing, stale, or internally inconsistent.
- The requested change increases blast radius beyond the active mode's safe bounds.
- Security, privacy, compliance, or trust-boundary concerns are identified.
- The task cannot pass the defined evaluation gate.
- Batch execution assumptions are invalidated by task coupling.
- Branch policy, commit policy, or execution policy cannot be satisfied.

When escalation occurs, execution should stop, the blocking condition should be recorded, and the task should remain incomplete until the issue is resolved.
