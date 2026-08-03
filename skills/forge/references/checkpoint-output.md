# FORGE Checkpoint Output Protocol

The output contract for the `execute-task` loop. It exists to keep long
`batch`/`auto` runs from spending tokens on narration. It is a **positive
template** — emit exactly these shapes; do not add prose, recaps, or reasoning
that is already recorded in the task file and commit.

Load this once at a run boundary (an initial `execute-task` activation or an
explicit resume/new session), not between checkpoints. `execute-task` also
carries a one-line fallback in case this reference is not reloaded after
compaction.

## Verbosity is set by `progress_policy` (docs/forge/AI.md)

- `checkpoint` — concise per-checkpoint summaries (default for `manual`).
- `compact` — one success line, detailed blockers (default for `batch`/`auto`).
- `detailed` — operator-requested narration.

Absent field: default to `compact`. `progress_policy` is a separate axis from
`execution_mode` (which is pacing).

**Minimum-cadence rule (read carefully).** Explicit higher-priority host
requirements and explicit user requests still apply — otherwise `progress_policy`
governs output. In `compact`, a host-required progress cadence is a **minimum
heartbeat, not permission to narrate each tool call.** Do not announce routine
reads, searches, edits, commands, or checks before doing them. A default
conversational style, or your own tendency to explain each action, is **not** an
override. After any initial acknowledgment the host requires, go quiet except for
the outputs enumerated below.

## Per-checkpoint output

Success:

```
TASK-<id> complete | validation <pass|n/a> | ref <commit|PR|issue>
```

Stopped — cover every stop state (map `independent-review` → `handoff-required`
and `claim-conflict` → `blocked`; do not invent new outcome words):

```
TASK-<id> blocked | check: <name> | evidence: <fact> | need: <fix or exception>
TASK-<id> handoff-required | need: independent reviewer | ref: <PR>
TASK-<id> escalated | reason: <fact> | need: <decision>
Stopped before task selection | reason: <missing prerequisite> | need: <action>
```

A stop message is itself informative; blockers are never silenced.

## Terminal summary (once per run)

```
Done: TASK-<a>..<b>. Validation: pass. Refs: <ids>. Remaining: <ids|none>.
```

`Refs:` covers commits, PRs, issues, and external-tracker records. If a run ends
on a blocker:

```
Stopped: TASK-<id> blocked. Done: <ids>. Need: <action>. Remaining: <ids>.
```

When a run contains a single checkpoint, the terminal summary REPLACES the
per-checkpoint line — do not emit both.

## Do not

Restate task evidence or gate reasoning already recorded; echo file contents;
re-explain the plan each iteration; narrate routine inspection. The task file and
commit ARE the record; produce the one terminal summary, not per-task recaps.
