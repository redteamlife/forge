# Frozen Evaluation Protocol — Token Discipline v2 (TASK-034 / D5)

Frozen 2026-08-02, before any TASK-035 edit. Do not change the fixed task or
rubric after baseline capture — a moved yardstick invalidates the comparison.

## Why a behavioral protocol

1.9.1 passed static verification and still narrated in practice. Acceptance of
v2 is a **behavioral** measurement on real Codex runs, not static fixtures.

## Fixed task (identical across every run)

Run in a Codex session on a bounded, representative FORGE task — the reference
task is:

> "Using the forge skill, implement the next `todo` task in this repo's ledger:
> read `docs/forge/AI.md` and the task, make the change within `file_scope`, run
> the tests, record gates, and commit. execution_mode: batch, progress_policy:
> compact."

Use the same repo state and the same task for every paired run. (nes_game or any
repo with ≥2 small queued tasks works; note which in the record.)

## Runs

- **≥3 paired runs** per comparison (behavior is probabilistic; report the
  median).
- Comparisons (each isolates one change):
  - TASK-035: 1.9.1 baseline vs. D1/D2 wording+loading.
  - TASK-037: same updated version, hook **disabled vs. enabled** (incl. a forced
    compaction mid-run to test reinjection).
  - TASK-038: original frozen baseline vs. fully integrated.
- **Baseline (capture now):** the 1.9.1 runs of the fixed task, recorded before
  any v2 edit lands.

## Rubric (pass threshold — a ratio alone is not a decision)

- **Disallowed (hard fail if any):** routine pre-tool announcements — narrating a
  read, search, edit, command, or check before doing it.
- **Allowed (enumerated):** required host heartbeats; checkpoint / material-state
  lines; blockers/decisions; exactly one terminal summary.
- **Pass:** zero disallowed announcements in **every** run AND median
  updated/enabled output-bytes ratio **≤ 0.5** of its comparison baseline.
- **Reinjection:** after a forced compaction, the compact rule visibly re-applies
  (transcript inspection).

## Recording and scoring

For each run, export a normalized transcript as JSONL — one object per turn:

```
{"role": "assistant", "text": "...", "pre_tool": true}
{"role": "tool", "name": "shell"}
```

`pre_tool: true` marks an assistant message emitted immediately before a tool
call. Score with:

```
python3 <skill-root>/assets/scripts/forge_narration_metrics.py run.jsonl [--label baseline]
```

It reports assistant-output bytes, the count of disallowed pre-tool announcements
(assistant `pre_tool` turns that are not a heartbeat/checkpoint/blocker/summary),
and the allowed-message tally. Compute the median ratio across the paired runs by
hand or feed multiple files.

## Harness boundary (honest)

The baseline **run** must happen in a Codex environment — I (in Claude Code)
cannot generate a representative Codex transcript. The protocol and scorer here
make that capture objective and reproducible; the transcripts are produced by the
Codex session and scored by the script. Record results under
`docs/forge/evaluations/`.
