# Design: Token Discipline v2 — Delivery, Cadence, Migration, Codex Reinforcement

Status: proposed. task_type: design. review_state: in-review.
Origin: two real reports that 1.9.1's `progress_policy: compact` did not reduce
narration on Codex/ChatGPT, plus a Codex-harness review that agreed with the
diagnosis and corrected the fix. All claims below verified against the installed
pack and this repo.

## Problem

1.9.1 put the output contract in the right *content* but the wrong *delivery*.
Verified gaps:

1. **Not reliably loaded.** `checkpoint-output.md` is on-demand only
   (`execute-task` line 83); no workflow step requires it. Its own "load at a run
   boundary" line lives inside the file, so it cannot trigger its own load. Only
   the inline fallback (line 40) is guaranteed present.
2. **Self-inflicted escape hatch.** `checkpoint-output.md:19` "User and harness
   requirements override" gets rationalized into "the harness likes progress, so
   narrate everything." It conflates a mandatory host cadence with discretionary
   narration.
3. **Surfaces too weak.** The generated `AGENTS.md` says "concise checkpoint
   output" but never prohibits per-tool announcements.
4. **No migration.** A version bump does not add `progress_policy` or migrate
   `response_style`. This repo's own `AI.md` still says `response_style: terse`.
5. **Codex hook stale + silent on output.** `.codex/hooks.json` uses an outdated
   two-level schema and carries only a governance echo — no output discipline,
   and it is not active until copied into a project and trusted.

Honest ceiling (agreed by the Codex review): a portable skill instruction cannot
override a higher-priority host contract. The goal is maximal reinforcement, not
a guarantee.

## Decisions

### D1. Reframe the override clause as a minimum-cadence rule (portable)

Replace "User and harness requirements override" with the distinction the Codex
review proposed:

> Explicit higher-priority host requirements and explicit user requests still
> apply. Otherwise `progress_policy` governs output. In `compact`, a
> host-required progress cadence is a **minimum heartbeat, not permission to
> narrate each tool call**. Do not announce routine reads, searches, edits,
> commands, or checks. A default conversational style or a tendency to explain
> actions is not an override.

Emit only: a required heartbeat (`Status: <state>. Next: <checkpoint>.`),
checkpoints/material state changes, blockers/decisions, and one terminal summary.
Drop the "after one initial acknowledgment" rule (heartbeats may be mandatory;
do not force a start-ack on hosts that don't need one).

### D2. Make the protocol a required read, not on-demand (portable)

Add an explicit `execute-task` workflow step: "At each initial activation or
explicit resume, read `../references/checkpoint-output.md` once." Remove it from
the on-demand list. Keep the inline fallback (with the D1 cadence distinction) so
the rule survives even if the read is skipped. Surfaces get a 2–3 line version
that explicitly prohibits per-tool announcements (name reads/searches/edits/
commands/checks), not just "be concise."

### D3. Migration path (portable)

`forge_migrate_context.py` (and a bootstrap-refresh step) must: add
`progress_policy: compact` when absent, map legacy `response_style: terse →
progress_policy: compact` (warn on other legacy values), and re-emit the updated
surface wording. Fix this repo's own `AI.md` as part of implementation. A version
bump alone must stop being treated as "migrated."

### D4. Codex-native reinforcement (Codex-specific, opt-in)

- **Fix `.codex/hooks.json`** to the current three-level schema (event → matcher
  group → handlers) with a `SessionStart` hook whose `matcher` includes
  `startup|resume|clear|compact`. It runs a small script that reads
  `docs/forge/AI.md` and emits a short output-discipline + governance line as
  developer context. The `compact` match is the key win: it re-injects the rule
  after automatic compaction, which no once-loaded reference can. Ship the script
  under `.codex/hooks/`.
- **Document an opt-in low-verbosity Codex profile** (guidance, not a portable
  field): `model_verbosity = "low"`, `model_reasoning_summary = "none"`,
  `hide_agent_reasoning = true`. Note honestly: `low` shortens output but does
  not guarantee silence; the reasoning flags cut log noise, not ordinary
  commentary.
- **Do not** use PreToolUse/PostToolUse for narration suppression (per-call token
  overhead; cannot erase emitted text), and **do not** use `model_instructions_file`
  (too invasive; `AGENTS.md` is the correct convention).
- Placement: put the strongest wording near the main working instructions in
  `AGENTS.md` (Codex loads it before work; nested overrides broader). No magic
  phrase exists — keep it concise and explicit.

## Open questions for review

1. D2: how does "required read at activation" degrade on harnesses where a skill
   cannot force a file read? (Inline fallback is the backstop — is it strong
   enough alone?)
2. D4: ship the Codex low-verbosity profile as a copyable `config.toml` fragment,
   or documentation only?
3. Should the migration (D3) run automatically on bootstrap-refresh, or only when
   the user opts in (surfaces are project files)?

## Implementation plan (bounded, if accepted)

1. TASK-035: D1 + D2 — minimum-cadence wording in `checkpoint-output.md`, the
   inline fallback, and all six surfaces (explicit no-per-tool-announcement);
   required-read workflow step in `execute-task`; fixture updates.
2. TASK-036: D3 — migration in `forge_migrate_context.py` + bootstrap-refresh;
   fix this repo's `AI.md`; fixture for `response_style → progress_policy`.
3. TASK-037: D4 — corrected `.codex/hooks.json` + `.codex/hooks/` script +
   ci-setup docs for the opt-in Codex profile. Touches a governance surface →
   security review.

## Non-goals

- A guarantee of silence (impossible from portable instructions).
- Skill-driven model/verbosity switching (operator/harness config only).
- PreToolUse-based narration suppression.
