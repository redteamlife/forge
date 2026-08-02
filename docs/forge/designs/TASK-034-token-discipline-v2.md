# Design: Token Discipline v2 — Delivery, Cadence, Migration, Codex Reinforcement

Status: changes-incorporated after external review. task_type: design.
status: complete (document authored). review_state: in-review.
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
the on-demand list. Keep the inline fallback (with the D1 cadence distinction) and
make it **independently normative** — the rule holds even if the read is skipped;
the reference only adds detail. Surfaces get a 2–3 line version that explicitly
prohibits per-tool announcements (name reads/searches/edits/commands/checks), not
just "be concise." Constraint: `execute-task` is at 5389/5400 bytes — the added
step + stronger fallback require explicit consolidation, not insertion.

### D3. Safe migration path (portable) — dedicated `forge_upgrade.py`

The existing `forge_migrate_context.py` is destructive (verified): it backs up
only CLAUDE/AGENTS/CONTEXT — not `AI.md` — and force-regenerates surfaces via the
generator, discarding narrative and project-specific content and ignoring
Cursor/Copilot/Windsurf/Codex. That violates the repo's own "do not start over"
rule (GETTING_STARTED "Updating Existing Projects"). Do NOT route migration
through it. Prefer a dedicated `forge_upgrade.py` with this contract:

- **detect automatically, mutate only with explicit authorization.**
- **`AI.md`: patch structurally after a backup**, limited to the `FORGE-config`
  block (never touch prose). Add `progress_policy: compact` when absent; map
  legacy `response_style: terse → progress_policy: compact`. Both-fields rule: a
  valid `progress_policy` is authoritative — after backup + authorization, remove
  the recognized legacy `response_style`; STOP on an invalid or conflicting value
  for human choice. Never regenerate `AI.md`.
- **Surfaces: auto-update only when the file matches a known FORGE-generated
  version or carries a managed marker/hash.** Otherwise emit a diff/fragment and
  require approval. **Never force-regenerate a customized narrative `AGENTS.md`.**
- **Idempotent**, with tests for both-fields-present, comment lines, code-fence
  boundaries, and repeated execution.
- Fix this repo's own `AI.md` (still `response_style: terse`) as part of impl.

A version bump must stop being treated as "migrated."

### D4. Codex-native reinforcement (Codex-specific, opt-in)

- **Fix `.codex/hooks.json`** to the current three-level schema (event → matcher
  group → handlers) with a `SessionStart` hook whose `matcher` includes
  `startup|resume|clear|compact`. It runs a small script (under `.codex/hooks/`)
  that reads `docs/forge/AI.md` and emits a short output-discipline + governance
  line as developer context. The `compact` match is the key win: it re-injects
  the rule after automatic compaction, which no once-loaded reference can.
- **Installation/upgrade safety (must specify):** if `.codex/hooks.json` already
  exists, **merge — never overwrite** unrelated hooks; identify the FORGE entry by
  a **schema-valid identity — the canonical command path** (do not assume the hook
  schema accepts an arbitrary marker field) so upgrades find and replace only it.
  **Recognize the currently shipped legacy hook** by its exact known signature
  (the 1.9.x inline `echo '...FORGE governance...'` command string / a recorded
  hash) so it can be safely replaced; **any unknown hook stays untouched**.
  Upgrades find and replace only the FORGE entry;
  respect project trust / hook-review (a hook is not active merely by existing).
  **Fail closed:** malformed hook JSON → refuse and report (no partial write);
  duplicate FORGE entries → dedupe to the canonical one; a conflicting command
  path → stop for human resolution. The script uses **fixed-enum parsing of
  `progress_policy`** — it never evaluates project-controlled text — emits **no
  secrets**, and performs **no repository mutation**. Tests: `compact`/
  `checkpoint`/`detailed`, missing/invalid AI config, all matcher events
  (`startup`/`resume`/`clear`/`compact`), and the fail-closed cases above.
- **Document a copyable, user-owned low-verbosity Codex profile** (guidance, not
  a portable field, and FORGE never writes to `~/.codex`): `model_verbosity =
  "low"`, `model_reasoning_summary = "none"`, `hide_agent_reasoning = true`. Note
  honestly: `low` shortens output but does not guarantee silence; the reasoning
  flags cut log/reasoning noise, not ordinary commentary.
- **Do not** use PreToolUse/PostToolUse for narration suppression (per-call token
  overhead; cannot erase emitted text), and **do not** use `model_instructions_file`
  (too invasive; `AGENTS.md` is the correct convention).
- Placement: put the strongest wording near the main working instructions in
  `AGENTS.md` (Codex loads it before work; nested overrides broader). No magic
  phrase exists — keep it concise and explicit.

### D5. A behavioral success criterion (not just static fixtures)

This design exists because 1.9.1 **passed static verification and failed in
practice.** Static fixtures are necessary but insufficient — behavioral evidence
is required. Lifecycle (avoids a retroactive gate that clashes with FORGE's
one-task/per-checkpoint model, and avoids capturing the baseline after the fact):

1. **Freeze the protocol and capture the baseline BEFORE TASK-035** changes
   anything (a recorded Codex run of a representative task under 1.9.1).
2. **Behavioral acceptance is part of TASK-035 and TASK-037** — the output/wording
   change and the Codex hook are the tasks whose effect is narration, so each
   proves its own behavioral delta against the frozen baseline.
3. **TASK-036 (migration) closes on deterministic safety tests** — narration
   behavior does not validate a migration utility.
4. **TASK-038 is the final integrated regression evidence** across the shipped set
   (baseline vs. fully-updated run), not an unexplained retroactive gate.

Objective rubric with a **pass threshold** (reporting a ratio is not a decision):

- **Disallowed (hard fail):** any routine pre-tool announcement (reads, searches,
  edits, commands, checks) — pass requires **zero** across the run.
- **Allowed (enumerated):** required host heartbeats, checkpoint/material-state
  lines, blockers/decisions, one terminal summary.
- **Runs:** ≥3 paired runs of the same fixed task (behavior is probabilistic);
  report the **median** output-bytes (or native tokens) ratio.
- **Pass:** zero disallowed narration in every run AND median updated/enabled
  ratio ≤ **0.5** of its comparison baseline (chosen threshold; tune once the
  frozen baseline exists).
- **Reinjection:** transcript inspection confirms the rule re-appears after a
  forced compaction event.

Comparison targets (isolate each change; do not confound):

- **TASK-035:** 1.9.1 baseline vs. D1/D2 wording+loading.
- **TASK-037:** the *same* updated version with the hook **disabled vs. enabled**
  (especially after compaction) — comparing to 1.9.1 cannot isolate the hook.
- **TASK-038:** original frozen baseline vs. the fully integrated result.

Record BOTH deterministic contract tests and the transcript-based Codex runs.

## Answers to review (resolved — no open questions remain)

- **Required reads on weak harnesses:** accept the limitation; the inline
  fallback is independently normative (the reference only adds detail); Codex
  gets extra durability from the D4 hook.
- **Low-verbosity profile:** documentation plus a copyable user-level profile
  example; FORGE never installs into or mutates `~/.codex`.
- **Automatic migration:** automatic detection, explicit mutation; only recognized
  untouched FORGE-managed files are eligible for automatic refresh.

## Implementation plan (bounded, if accepted)

1. TASK-035: D1 + D2. **First checkpoint (before any edit): freeze the D5
   protocol and capture the 1.9.1 baseline runs** — the baseline is the opening
   step of this bounded task, not a separate pseudo-task. Then: minimum-cadence
   wording in `checkpoint-output.md`, the independently-normative inline fallback,
   and all six surfaces (explicit no-per-tool-announcement); required-read
   workflow step in `execute-task` (consolidate — it is at 5389/5400 bytes, 11
   free); static fixtures **plus its behavioral delta vs. the frozen baseline**.
   **Security review required** (an output-policy change must not suppress
   security blockers).
2. TASK-036: D3 — new `forge_upgrade.py` with the safe contract (patch `AI.md`
   after backup; surfaces only on managed-marker/known-version match, else
   diff-for-approval; never force-regen narrative `AGENTS.md`); fix this repo's
   `AI.md`; **closes on deterministic migration-safety/idempotency tests** (not
   narration). **Security review required** (mutates existing project files).
3. TASK-037: D4 — corrected `.codex/hooks.json` (merge-safe, managed identity) +
   `.codex/hooks/` script + ci-setup docs for the opt-in user-owned Codex
   profile; **behavioral delta measured hook-disabled vs. hook-enabled on the same
   updated version (esp. post-compaction reinjection)**. **Security review
   required** (executable hooks).
4. TASK-038: D5 — final integrated regression evidence (baseline vs. fully-updated
   run) across the shipped set. Not a retroactive per-task gate.

## Non-goals

- A guarantee of silence (impossible from portable instructions).
- Skill-driven model/verbosity switching (operator/harness config only).
- PreToolUse-based narration suppression.
