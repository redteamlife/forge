# FORGE

## **FORGE - A Documentation-First Governance Framework for Agentic Engineering**

FORGE provides a deterministic operating model for AI-assisted engineering inside an IDE. It transforms agentic coding from an unbounded conversation into a structured, auditable, and repeatable workflow.

---

## Why FORGE Exists

AI-assisted coding without governance creates entropy:

- Tasks expand beyond original scope
- Security review is skipped
- Commits lack bounded intent
- Memory is not captured
- Evaluation gates are inconsistent
- Implementation drifts from plan

FORGE introduces execution discipline.

It separates:

- Planning
- Validation
- Implementation
- Review
- Security analysis
- Evaluation
- Memory capture
- Commit finalization

All governed by a deterministic execution contract.

---

## What FORGE Is

- A documentation framework for governed AI execution
- A mode-driven control model with progressively stronger guardrails
- A bounded task execution system
- A commit-disciplined workflow
- A reusable project bootstrap template

FORGE defines *how* agentic work happens - not what to build.

---

## What FORGE Is Not

- Not an autonomous agent
- Not a daemon, runtime, or background service
- Not a code generator
- Not a replacement for engineering judgment
- Not a task management tool

FORGE is governance.

---

## Core Operating Principle

All execution is governed by:

`docs/forge/FORGE.md`

This document defines:

- Deterministic workflow sequencing
- Task validation requirements
- Implementation boundaries
- Security review expectations
- Evaluation gates
- Memory update rules
- Commit discipline

No task proceeds outside this contract.

---

## Repository Usage

See [GETTING_STARTED.md](GETTING_STARTED.md) for a step-by-step walkthrough.

**Quick summary:**

1. Copy `templates/` into the target repository.
2. Give your AI assistant the prompt: *Read `templates/GENERATE_PROJECT_DOCS.md`, then generate FORGE documentation for: [your project description]*
3. Review the generated `docs/forge/` documents, especially `TASKS.yaml` and `AI.md`.
4. Begin governed execution by telling your AI: *Read `docs/forge/FORGE.md` and begin working.*

The `templates/` directory may be removed after documentation is generated and validated.

To add pipeline enforcement, copy `ci/` into the project root and follow the setup steps in `ci/README.md`.

---

## Repository Scope

This repository contains governance framework assets only.

- No application code
- No runtime agents
- No demo applications
- No tool-specific integrations

FORGE is execution discipline, not an automation layer.

### Repository Structure

- `templates/` - document templates and the generation prompt for bootstrapping a new project
- `philosophy/` - design rationale for the execution model, modes, and maturity model
- `ci/` - pipeline enforcement scripts, git hooks, GitHub Actions workflow, and org policy template

---

## Design Philosophy

FORGE is built on four principles:

1. Determinism over conversation
2. Bounded execution over exploratory drift
3. Documentation as contract
4. Auditability by default

Agentic systems become reliable only when execution is constrained by structure.

FORGE provides that structure.

### Philosophy Docs

- [Execution Model](philosophy/execution-model.md) - why the workflow is designed the way it is
- [Modes](philosophy/modes.md) - documentation requirements and enforcement differences across the four modes
- [Maturity Model](philosophy/maturity-model.md) - six-level progression from ad hoc prompting to full disciplined orchestration
