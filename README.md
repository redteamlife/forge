# FORGE

**A governance framework for AI-assisted coding.**

FORGE gives your AI assistant a set of documents to work from - a task list, a rules file, and a commit format. Instead of open-ended prompting, the AI follows a documented workflow you control, works one task at a time, and stops when something is unclear.

**Works with any AI assistant** that can read files: Claude Code, Codex, Cursor, GitHub Copilot Workspace, local LLMs, or any other tool with file access.

**No CI pipeline required to start.** The simplest setup is three files and five minutes.

---

## The Minimum Setup

At its most basic, FORGE gives you:

1. **`TASKS.yaml`** - your task list. The AI picks the first incomplete task, implements only that, and stops.
2. **`FORGE.md`** - the rules file. The AI reads this at the start of every session and follows it.
3. **`AI.md`** - your configuration. Declares the mode and execution style.

That's Lightweight mode. Three files. No pipeline. No hooks. The AI reads the docs, does one task, commits with a structured message, and stops.

When you're ready for more - architecture constraints, security reviews, evaluation gates, CI validation - you level up the mode and add the corresponding documents. You control the pace.

---

## Why This Helps

AI-assisted coding without any structure tends to:

- Expand scope beyond what you asked for
- Skip review and testing
- Produce commits with no clear intent
- Drift from the original plan across sessions
- Lose context between sessions

FORGE introduces boundaries. The AI cannot start work without a task. It cannot finish without passing a review. It cannot commit without a structured message. When something is ambiguous or blocked, it stops and tells you why instead of guessing.

---

## How It Works

```text
You set up docs/forge/ with your project's governance documents.
The AI reads them at the start of every session.
The documents define what the AI is allowed to do.
The AI follows the workflow and commits one task at a time.
```

The document at `docs/forge/FORGE.md` is the execution authority. If the AI's instructions conflict with it, the document wins. If the documents are silent on something, the AI stops.

---

## Four Levels of Governance

FORGE has four modes. Each adds requirements on top of the one below it.

| Mode | Required docs | Best for |
| --- | --- | --- |
| **Lightweight** | 3 files | Getting started, personal projects, low-risk work |
| **Mid** | 8 files | Most development work - adds architecture checks and security review |
| **Strict** | 11 files | Team projects, audit requirements, security-sensitive systems |
| **Full Discipline** | 12 files + org policy | Regulated environments, enterprise contexts |

Start at Lightweight. Move up when you need more.

---

## Getting Started

See [GETTING_STARTED.md](GETTING_STARTED.md) for a full walkthrough.
See [CHANGELOG.md](CHANGELOG.md) for a summary of changes across releases and unreleased branch work.

**Quick version:**

1. Copy `templates/` into your project root.
2. Tell your AI: *Read `templates/GENERATE_PROJECT_DOCS.md`, then generate FORGE documentation for: [your project in 2-3 sentences]*
3. Review `docs/forge/TASKS.yaml` and `docs/forge/AI.md`.
4. Start a session: *Read `docs/forge/FORGE.md` and begin working.*

The `templates/` folder can be removed after docs are generated.

---

## Tool Development and Release

FORGE includes a workflow for developing and releasing tools with a private/public repository separation. Internal planning docs and architecture stay in a private dev repo; only release artifacts reach the public repo.

- **Open source tools** — source code is published to a public repository
- **Closed source tools** — compiled binaries are published as GitHub Release assets via the `gh` CLI

Scaffold a new tool project with
 `scripts/forge-tool-init.sh` (Linux/macOS)
 or
 `scripts/forge-tool-init.ps1` (Windows).

Publish releases with `scripts/forge-publish.sh` / `scripts/forge-publish.ps1`.

See [GETTING_STARTED.md](GETTING_STARTED.md) for the full walkthrough.

---

## CI Pipeline Enforcement (Optional)

The `ci/` directory contains scripts and a GitHub Actions workflow that validate FORGE outputs independently of the AI - commit format, task state, evidence artifacts, file scope, and doc completeness. These run on every PR and block merges on validation failure.

This is optional. FORGE works without it. CI enforcement is most useful when working in teams or in Mid mode and above, where the stakes of a missed review or incomplete task are higher.

To set it up, copy `ci/` into your project root and follow [ci/README.md](ci/README.md).

---

## Repository Structure

```text
templates/   document templates and the generation prompt
philosophy/  design rationale for the execution model, modes, and maturity model
ci/          pipeline scripts, git hooks, GitHub Actions workflow, org policy template
scripts/     tool development and release scripts (forge-tool-init, forge-publish)
```

---

## Design Philosophy

Four principles:

1. **Documentation as contract** - the documents define what the AI is allowed to do, not suggestions it can interpret
2. **Bounded execution** - one task at a time, no scope expansion, hard stops when blocked
3. **Auditability by default** - every task committed with structured metadata, every session traceable
4. **Determinism over conversation** - the workflow is defined, not negotiated each session

- [Execution Model](philosophy/execution-model.md) - why the workflow is designed the way it is
- [Modes](philosophy/modes.md) - documentation requirements across the four modes
- [Maturity Model](philosophy/maturity-model.md) - six-level progression from ad hoc prompting to full disciplined orchestration
- [Open Source Collaboration Proposal](philosophy/open-source-collaboration.md) - proposed workflow for accepting public contributions while keeping private governance
