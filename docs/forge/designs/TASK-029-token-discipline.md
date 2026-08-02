# Design v3: Token Discipline — a Portable Checkpoint-Output Protocol

Status: v1 findings addressed; v2 direction approved with narrow corrections,
applied here as v3. review_state: in-review — awaiting acceptance before
TASK-030/031. D5 (file-size) removed to its own design.

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
rereads. Implementation should capture before/after measurements: native token counts and
repeated-read telemetry **when the harness exposes them**; otherwise proxies —
transcript/output bytes, tool-output volume, and observed file-read counts.

## Decisions

### D1. One canonical checkpoint-output protocol, loaded in the loop

Define the checkpoint output contract **once** in
`references/checkpoint-output.md`, scoped to `execute-task` (the loop where the
burn happens). Do NOT point plan/build/review/ship at a checkpoint-specific
reference — their terminal outputs differ; a general cross-lifecycle protocol is
a separate, larger effort and out of scope here.

Loading and run boundaries: a run boundary is an initial `execute-task`
activation or an explicit resume/new session. Load the reference at those
boundaries, never between checkpoints. Because a pointer alone can disappear
during compaction, keep a **minimal inline fallback** in `execute-task` — the
one-line success/stop schema below — for redundancy. No portable skill
instruction can guarantee preservation through every harness's compaction; the
inline schema reduces the risk, it does not eliminate it. Because `execute-task` is at 5225/5400 bytes, the
inline fallback is achieved by consolidation, not a large insertion.

### D2. The protocol is a positive template, not a list of prohibitions

Local/open-weight models follow an explicit output schema far more reliably than
negatives ("do not narrate/recap/explain"). The protocol specifies what TO emit:

- **per checkpoint (success)**: `TASK-<id> complete | validation <pass|n/a> | ref <id>`
  (ref = commit/PR/issue when one exists).
- **per checkpoint (stopped)**: cover every execute-task stop state, not just
  `blocked` — also `handoff-required`, `escalated`, `independent-review`, and
  `claim-conflict`, plus failures before a task is selected:
  - `TASK-<id> blocked | check: pytest | evidence: 2 failures | need: fix or exception`
  - `TASK-<id> handoff-required | need: independent reviewer | ref: PR-42`
  - `TASK-<id> escalated | reason: <fact> | need: <decision>`
  - `Stopped before task selection | reason: <missing prerequisite> | need: <action>`
  A stop message is itself informative; blockers are never silenced.
- **once at end of run**: exactly one compact, task-source-neutral terminal
  summary, e.g.
  `Done: TASK-030..031. Validation: pass. Refs: abc123, PR-42. Remaining: none.`
  `Refs:` covers commits, PRs, issues, and external-tracker records — better than
  a commit-specific field.
- **single-checkpoint run**: when a run ends after one checkpoint, the terminal
  summary REPLACES the checkpoint line (do not emit both). A stopped-run summary
  form covers a run that ends on a blocker:
  `Stopped: TASK-031 blocked. Done: TASK-030. Need: <action>. Remaining: TASK-032.`

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

Migration from `response_style` (decided): `progress_policy` is optional.
Defaults: `manual` → `checkpoint`, `batch`/`auto` → `compact`. Legacy
`response_style: terse` maps to `compact`; any other legacy `response_style`
value maps to the mode-derived default with a validator warning. New templates
emit only `progress_policy`. If both fields are present, `progress_policy` takes
precedence and the validator warns.

Durable-surface conflict (must be handled in TASK-030): the generated `AGENTS.md`,
the Cursor rule, and the root skill each independently hardcode "be terse," which
would contradict a configured `detailed`. TASK-030 updates those canonical
surfaces to defer to config — "Follow `progress_policy` from `AI.md`; default to
compact output when absent" — so the field is authoritative rather than
overridden by more persistent instructions.

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

## Implementation plan (bounded, if accepted)

1. TASK-030: `references/checkpoint-output.md` protocol (positive template,
   scoped to `execute-task`) + `progress_policy` field with `response_style`
   migration + validator (migration warning when both present) + inline fallback
   schema and run-boundary loading in `execute-task` (via consolidation).
   Capture before/after token measurements (native when exposed, else proxies).
2. TASK-031: model-selection guidance in `references/token-efficiency.md` (or a
   short note) — documentation only, no config field.

File-size gate: separate future design with its own security review.

## Non-goals

- Skill-driven model switching (undeliverable from portable instructions).
- Complete silence (not portable; compact structured output instead).
- Overloading `execution_mode` with output style.
- Scattering divergent output instructions across every skill.
