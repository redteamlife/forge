# Design: Workflow Stickiness (closing the loop, moment-routing, continuous mode)

Status: proposed (TASK-011). Implementation follows in separate bounded tasks after
review. Written for external review; feedback welcome on every decision.

## Problem

After `forge-bootstrap`, governed behavior decays. Observed pattern (reported by the
pack maintainer and matching downstream usage): bootstrap generates docs and tasks,
then the operator must repeatedly say "use forge skills to create tasks for X",
"commit using forge skills". Several gate skills (critique, security-review,
evaluation, memory) effectively never run unless explicitly requested.

Root causes found by reviewing all 13 subskills:

1. **The execution loop does not close.** `forge-execute-task`'s workflow is
   implement -> checks -> update state -> commit -> stop. Critique, security
   review, evaluation, and the memory write are separate skills it never invokes.
   The gates exist; nothing conducts them.
2. **Philosophy/skill drift.** `philosophy/execution-model.md` specifies memory is
   queried before the alignment check; `forge-execute-task` never mentions memory
   in reads, workflow, or evidence.
3. **Agent surfaces route to files, not moments.** The generated router says what
   to read (`AI.md`, task index, one task) but never when to invoke which skill.
   The surface is the only always-in-context lever per session, and it is spent on
   read order instead of activation.
4. **Meta trigger descriptions.** Lifecycle aliases describe themselves as "Route
   FORGE planning requests..." — they trigger only when the user says "FORGE".
   A user in a bootstrapped repo says "now add auth", and ungoverned work happens
   in a governed repo.
5. **Continuous mode is undefined.** `execution_mode` exists in FORGE-config and
   execute-task step 12 allows continuing "when the project explicitly allows it",
   but no semantics are defined anywhere.

Design tension to resolve honestly: FORGE's core principle is explicit activation,
never always-on. Resolution: **the repo opts in at bootstrap.** Once a repo carries
`docs/forge/`, its own surfaces declare FORGE the default workflow for that repo.
Explicitness moves from every-message to once-at-bootstrap; the pack itself remains
inert in repos that never opted in.

## Decisions

### D1. Close the loop inside `forge-execute-task`

The checkpoint definition becomes: select/claim task -> **memory read (index +
relevant topic only, before the alignment check — fixes drift #2)** -> implement
-> run checks -> **critique gate** -> **security-review gate when the change
surface or `security_profile` requires it** -> **evaluation gate** -> **memory
write (short entry; fuller entry only when reusable)** -> update task state ->
commit -> stop or continue per `execution_mode`.

- The gate skills remain independently invocable (required for
  `requires_independent_review`, standalone review requests, and forge-review
  routing). Execute-task *invokes* them; it does not inline their content.
- Gate failures behave as today: blocking findings are hard stops.
- Cost control: gates already mandate compact findings-first output; the loop
  adds no new reads beyond what each gate already declares.
- Evidence list gains: memory entry reference, gate results per checkpoint.

Rejected alternative: merging critique/evaluation content into execute-task.
Bloats the highest-frequency skill past its size budget and breaks independent
review, forge-review routing, and separate-session evaluation.

### D2. Agent surfaces become moment->skill maps

`forge_generate_agent_surfaces.py` router output (and the narrative template's
governance section) is rewritten to a compact intent table:

- plan / break down / add or reshape tasks -> `forge-plan`
- implement / build / fix / continue work -> `forge-execute-task` (gates run
  inside the loop per D1)
- review / "is this done" -> `forge-review`
- commit / merge / release / promote -> `forge-ship`
- record or recall lessons -> `forge-memory`

Plus one activation line: "This repo uses FORGE for all implementation work —
route through these skills even when the request does not mention FORGE."
File read-order guidance shrinks to one line (`AI.md`, `CONTEXT.md`, task index,
one task). Lite context budgets are preserved: the moment table replaces, not
augments, the current router prose; `forge_validate_context.py` size checks and
include-bomb rules still apply unchanged.

Rejected alternative: keeping read-order routing and relying on better skill
descriptions alone. Descriptions compete with every other installed skill; the
repo surface is the only deterministic, always-loaded channel.

### D3. De-meta the alias descriptions; eval them

Rewrite `forge-plan`/`forge-build`/`forge-review`/`forge-ship` (and audit
`forge-critique`/`forge-evaluation`/`forge-memory`) descriptions to trigger on
the user's words plus the repo signal, not the word FORGE. Shape: "Use when the
user asks to plan, break down, or add tasks in a repo containing `docs/forge/`
or governed by FORGE...". Then run the existing description-optimization harness
(`skills/forge-workspace/description-optimization/`) over the subskills — the
same process that fixed the root skill's triggering — with the collision lesson
applied (isolate the skill under test from the system-wide install).

Guardrail: descriptions must still condition on the repo signal so the pack does
not capture generic "review this" requests in non-FORGE repos. Always-on capture
is a non-goal.

### D4. Define `execution_mode` semantics

In FORGE-config and `references/`:

- `manual` (default): stop after each checkpoint (today's behavior).
- `continuous`: after a completed checkpoint (all gates + evidence + commit),
  select the next eligible task and continue; stop only on hard stops, ledger
  exhaustion, or blocked dependencies. Every checkpoint retains full gates —
  continuous changes pacing, never rigor.

Bootstrap asks for it alongside the existing profile questions; execute-task
step 12 references the field instead of "when the project explicitly allows it".
The README's "do not stop until done" kickoff phrase maps to `continuous`.

### D5. Optional harness enforcement (Claude Code)

New optional asset: `.claude/settings.json` fragment with a PreToolUse hook on
`git commit` that warns (not blocks) when `docs/forge/` exists and the staged
change set updates task state without touching `docs/forge/EVALUATION.md` —
mirroring the existing git `pre-commit` hook so the nudge exists even before git
hooks are installed. Opt-in at bootstrap, documented in `ci-setup/`.

Additionally: bootstrap's hook-install question defaults to **yes** for
`solo-governed` and `team-full` (currently "when the user wants it") — the git
hooks are the enforcement layer that already exists and is rarely installed.

Rejected alternative: making the Claude hook blocking. Cross-harness parity does
not exist (Cursor/Copilot/Windsurf have no equivalent), and FORGE policy is that
CI is the durable backstop; local nudges stay advisory.

## Non-goals

- No always-on behavior at the pack level; repos without `docs/forge/` are
  untouched by every change here.
- No new subskills. The fix is wiring, not surface area.
- No harness-specific behavior beyond the optional D5 asset.

## Implementation plan (bounded tasks, target 1.9.0)

1. TASK-012: D1 + memory drift fix (execute-task workflow/evidence, philosophy
   cross-check) + D4 semantics (config comment, execute-task step 12, bootstrap
   question, README mapping).
2. TASK-013: D2 surface generator + narrative template rewrite; regenerate
   fixtures; context-validator budgets re-verified.
3. TASK-014: D3 description rewrites + description-optimization eval runs;
   record before/after trigger rates as evidence.
4. TASK-015: D5 Claude hook asset + bootstrap hook-default change + ci-setup
   docs.

Verification: existing verify-repo fixtures plus new checks that (a) execute-task
names all four gates in its workflow, (b) generated surfaces contain the moment
table and stay within size budgets, (c) subskill descriptions parse under strict
YAML and contain the repo-signal condition.

## Review questions for downstream

1. D1: is invoking gates from inside execute-task the right granularity, or
   should gate results be summarized inline with full runs only on findings?
2. D2: does the moment table read as capture-y in mixed repos (FORGE governs one
   service in a monorepo)? Should the activation line be scoped to paths?
3. D4: should `continuous` be the bootstrap default for solo-governed, or is
   manual-first still right for new users?
4. D5: is a warn-only Claude hook worth the harness-specific surface, or is
   defaulting git hooks to installed sufficient?
