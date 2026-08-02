# FORGE Token Efficiency

FORGE should reduce drift and rework without becoming a large token tax.

## High-Value Rules

- Load only the files required for the current step.
- Use `docs/forge/CONTEXT.md` when present; otherwise default to conservative `lite` reads.
- Prefer `TASKS.index.yaml` plus one selected task file over loading a large task ledger.
- Prefer compact structured outputs over narrative explanations.
- Do not re-read unchanged repo-local docs repeatedly in one execution pass.
- Use the coordination branch only when claim or task-state transitions require it.
- Read only relevant split security checklist files or sections; do not load all checklists by default.
- Keep `MEMORY.md` entries short and high-signal.
- Prefer fixed response shapes over free-form summaries.

## Where Tokens Usually Leak

- restating the selected task or project context in every response
- reading every governance doc at the start of every step
- narrating routine inspection and planning steps
- verbose critique and evaluation writeups
- copying all security checklist sections into every project
- echoing generated file contents back into chat
- repeated warnings about expected branch drift in team mode

## Practical Default

FORGE should behave more like:

- short action updates
- narrow file loads
- direct edits
- compact gate results
- `Done / Changed / Next` closeouts

and less like:

- long conversational explanation
- repeated context recap
- exhaustive changelog narration
- prose summaries of reasoning already stored in files

## Model Selection (guidance, not a mechanism)

A FORGE skill cannot switch the running model — that is harness/operator control.
This is guidance for whoever configures the session, not a config field FORGE
enforces (an unimplemented `model_profile` field would imply a capability the
pack lacks; add configuration only when an adapter consumes it).

Economical-tier candidates:

- deterministic checks — tests, linters, `forge_next_gate.py`, doc validators
- bounded mechanical `execute-task` iterations on a small, well-scoped change

Stronger-tier work (do not downgrade):

- planning and architecture (`forge-plan`, design tasks)
- the judgment gates — `forge-critique`, `forge-evaluation`, `forge-security-review`

Deterministic checks being economical does not make the gates that *interpret*
them economical: a linter run is cheap-model work; deciding whether a finding is
a blocker is not.
