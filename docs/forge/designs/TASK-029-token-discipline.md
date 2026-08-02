# Design v2: Token Discipline — a Portable Checkpoint-Output Protocol

Status: v1 critique = fail pending revision; all blocking findings verified and
incorporated. review_state: changes-incorporated. D5 (file-size) removed to its
own design. Awaiting acceptance before TASK-030/031.

## Problem (re-scoped)

A real multi-hour `batch`/`auto` refactor exhausted a weekly token allowance,
much of it apparently on narration. Inspection confirms a **contributing control
gap** — not a proven root cause:

- `execute-task/SKILL.md` (the loop) has no output contract
  (`grep -c terse|narrat|recap|status = 0`).
- `references/token-efficiency.md` is strong but referenced only from the root
  skill, never from the loop; effectively never loaded during a run.
- The root `## Output Discipline` is read once at session start; on long runs it
  may drift out of active context (a **portability risk**, not a proven
  universal behavior — some harnesses reinforce it).

Coverage already varies by harness: the always-applied Cursor rule and the
`AGENTS.md` surface already request terse output, so Cursor/AGENTS users see less
of this; the gap is worst where no persistent rule surface reinforces the
contract. What the inspection does NOT establish: how much burn came from visible
narration vs. repeated reads, tool output, gate execution, compaction, or source
rereads. Implementation should capture before/after measurements (output tokens
per checkpoint, tokens per task, repeated reads, tool-output volume).

## Decisions

### D1. One canonical checkpoint-output protocol, loaded in the loop

Define the output contract **once** in `references/checkpoint-output.md` (not
scattered, slightly-different, across every lifecycle skill — the gate skills are
already compact). `execute-task` loads it **once at the start of a run** (never
re-read per checkpoint) and references it; other lifecycle skills point at the
same file. Because `execute-task` is at 5225/5400 bytes, this is a compact
pointer + protocol reference, achieved by consolidation, not a large insertion.

### D2. The protocol is a positive template, not a list of prohibitions

Local/open-weight models follow an explicit output schema far more reliably than
negatives ("do not narrate/recap/explain"). The protocol specifies what TO emit:

- **per checkpoint**: one line — `TASK-<id>: <complete|blocked>` (+ commit/PR ref
  when one exists).
- **on a blocker**: always emit the failed gate/check, the relevant evidence, and
  the required action — blockers are never silenced.
- **once at end of run**: exactly one compact terminal summary, e.g.
  `Done: TASK-030..032. Gates: pass. Commits: abc123, def456. Remaining: none.`

No-duplication principle (from v1 D3, corrected): do not restate task evidence or
gate reasoning that is already recorded — but DO produce the single terminal
summary. This holds across configurations where a commit is not the record:
issue-tracker-authoritative work, team PR-ready-without-commit, this repo's
release branch that strips `docs/forge/`, and hosts requiring a self-contained
final response.

### D3. Verbosity level is its own field, not overloaded onto execution_mode

`execution_mode` is defined as checkpoint *pacing* and must stay that. Add a
separate field:

```
progress_policy: checkpoint | compact | detailed
```

- `checkpoint` — concise per-checkpoint summaries (default `manual`).
- `compact` — one success line, detailed blockers (default `batch`/`auto`).
- `detailed` — operator-requested narration.

`batch`/`auto` default to `compact`, but **user and harness requirements
override** — a host that requires periodic progress or a self-contained final
response gets it. Complete silence is not portable; compact structured updates
are.

### D4. Model selection is documentation only — no config field yet

A skill cannot switch the running model. Ship **guidance**, not a mechanism, and
do not add a validated `model_profile` field (an unimplemented field implies a
capability FORGE lacks; add configuration only when an adapter consumes it):

- Economical-tier candidates: deterministic checks (tests, linters,
  `forge_next_gate.py`), mechanical bounded edits.
- Stronger-tier work: planning, architecture, and the judgment gates —
  critique, evaluation, security review. (v1 wrongly implied "routine gate runs"
  suit weak models; judgment gates do not.)

## Removed: file-size ratchet (was D5)

Deferred to its own design (`TASK-0xx-file-size-gate`). It carries independent
policy, CI/pre-commit changes (so a **security/DevSecOps review is required**,
not n/a), exception storage, and baseline semantics. Design notes for later: the
pack's own budgets are **byte-based**, not line-based (line count is a weak proxy
that invites artificial splitting); prefer bytes + optional line thresholds;
compare against the PR merge base (natural ratchet); block growth of over-limit
files and new over-limit files; advisory soft threshold; exceptions in config
with owner/justification/optional expiry; apply only to configured source
classes.

## Open questions for review

1. D2 terminal-summary shape — is the `Done/Gates/Commits/Remaining` line the
   right canonical schema, or should it vary by task_source?
2. D3 — new `progress_policy` field vs. clarifying/reusing the existing
   `response_style`? (New field is explicit; reuse avoids config growth.)
3. D1 loading — "once at start of run" is clear for a fresh session; how should a
   resumed/compacted session re-establish the protocol?

## Implementation plan (bounded, if accepted)

1. TASK-030: `references/checkpoint-output.md` protocol (positive template) +
   `progress_policy` field + validator + load-once wiring in `execute-task` (via
   consolidation) + one-line pointers in plan/build/review/ship. Capture
   before/after token measurements as evidence.
2. TASK-031: model-selection guidance in `references/token-efficiency.md` (or a
   short note) — documentation only, no config field.

File-size gate: separate future design with its own security review.

## Non-goals

- Skill-driven model switching (undeliverable from portable instructions).
- Complete silence (not portable; compact structured output instead).
- Overloading `execution_mode` with output style.
- Scattering divergent output instructions across every skill.
