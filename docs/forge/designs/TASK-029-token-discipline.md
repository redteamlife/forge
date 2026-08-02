# Design: Token Discipline in the Execution Loop (+ file-size ratchet)

Status: proposed (TASK-029). For external review before implementation.

## Problem (confirmed by file inspection)

A real multi-hour `batch`/`auto` refactor (user's NES project) exhausted a weekly
token allowance, mostly on narration. Root cause, verified in the pack:

1. `execute-task/SKILL.md` — the skill that runs the loop — contains **no output
   discipline at all** (`grep -c terse|narrat|recap|status = 0`). The loop never
   tells the model to be terse.
2. `references/token-efficiency.md` is strong and specific (it names "narrating
   routine steps" and "prose summaries of reasoning already stored in files" as
   leaks) but is referenced **only** from the root skill's on-demand list;
   `execute-task`'s own reference list does not include it. It is effectively
   never loaded during a loop.
3. The root skill's `## Output Discipline` is good but read **once at session
   start**; over a long autonomous run it falls out of active context.

Net: the discipline exists but is not where the work happens, and it does not
scale with autonomy — narration is write-only tokens in `batch`/`auto` (no human
is reading until the loop stops), yet those modes get the same (front-loaded,
then forgotten) guidance as `manual`.

## Decisions

### D1. Put compact output discipline in the loop, not just the front door

Add a short, permanent output-discipline block to `execute-task/SKILL.md` (and a
one-liner to the other lifecycle skills that run work) so it is in context every
checkpoint, not only at startup. Add `references/token-efficiency.md` to
`execute-task`'s on-demand reference list. Keep it compact (byte budgets apply).

### D2. Scale verbosity down as autonomy goes up

Output discipline is a function of `execution_mode`:

- `manual` — a human is watching each checkpoint; a one-line `Done: … Changed: …
  Next: …` closeout is allowed and useful.
- `batch` / `auto` — nobody reads until the loop stops. Per-checkpoint output is
  a **single status line** (`TASK-007 complete`); no narration, no per-task
  summary, no reasoning prose. A compact run summary is produced **once, at the
  end**, not per task.

### D3. The task file and commit ARE the summary — do not restate them

Make explicit what token-efficiency.md implies: the task `gates:`/evidence and
the Conventional Commit already record what happened. A post-task prose recap of
that same content is duplicate output, multiplied across every looped task.
Rule: do not narrate gate reasoning unless a gate fails; do not summarize a task
after committing it; do not echo file contents or re-explain the plan.

### D4. Model tiering is a recommendation, NOT skill-enforced (honest scoping)

A skill cannot change the running model — that is harness/operator control, not
portable instruction. So FORGE ships **guidance**, not a mechanism:

- `references/token-efficiency.md` (or a short model-tiering note) recommends
  which work suits a cheaper tier (bounded mechanical `execute-task` iterations,
  routine gate runs) vs. a stronger tier (planning, architecture, security
  review, ambiguous critique).
- An optional advisory config field (e.g. `model_profile: economical | balanced |
  max`) may **express intent** in `AI.md` for harnesses that can honor it, but
  the pack must not claim to switch models itself. Do not design a mechanism we
  cannot deliver.

### D5. File-size ratchet as a mechanical quality gate (separate concern)

Adopt the "small files" idea as a configurable, ratcheting, tiered gate — not a
blunt 500-line purge:

- **Ratchet**: existing over-cap files are not violations; growing one past the
  cap, or adding a new file over it, is. No day-one refactor tax.
- **Tiers**: warn at a soft cap (default 500), block at a hard cap (default
  ~800–1000). Same warn/block philosophy as the existing hooks.
- **Exclusions + exceptions**: `generated/`, `vendor/`, fixtures, lockfiles
  excluded by config; a per-file documented exception with justification is
  allowed (mirrors the scope-expansion rule).
- Enforced in `forge-quality.yml` / pre-commit — a numeric rule a one-line check
  can enforce (the same pattern as the pack's own SKILL.md byte budgets, which
  have repeatedly caught drift).

Rationale: this is really an agent-ergonomics rule (small files edit reliably,
review cheaply, fit in context), which also reduces tokens.

## Open questions for review

1. D2: is a single status line per checkpoint too terse for `batch` — should a
   failed checkpoint still emit a short reason (yes, I think) while successes
   stay one line?
2. D4: is an advisory `model_profile` field worth shipping if no current harness
   honors it, or should it stay pure documentation until one does?
3. D5: soft/hard cap defaults (500/1000?) and whether the ratchet baseline is the
   file's line count at gate-introduction time or at each commit.
4. Should output discipline also tighten the gate skills (critique/evaluation)
   in-loop, or is D1+D3 enough given they already say "findings-first"?

## Implementation plan (bounded, if accepted)

1. TASK-030: D1–D3 — in-loop output discipline block in `execute-task` (+ short
   lines in plan/build/review/ship), `execution_mode`-scaled verbosity, "task &
   commit are the summary" rule; reference token-efficiency.md from the loop.
2. TASK-031: D4 — model-tiering recommendation doc (+ optional advisory
   `model_profile` field with validator, explicitly non-enforcing).
3. TASK-032: D5 — file-size ratchet gate (config, `forge-quality.yml`/pre-commit
   check, exclusions/exceptions, fixtures).

## Non-goals

- Skill-driven model switching (cannot be delivered from portable instructions).
- A blunt universal line cap or forced refactor of legacy files.
- Removing useful `manual`-mode summaries (a watching human benefits from them).
