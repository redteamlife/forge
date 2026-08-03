# FORGE Output Evaluation Harness

Behavioral measurement for the output-discipline rules — because static fixtures
can pass while real runs stay chatty (the 1.9.1 lesson). Use it to gate any
future output-discipline change on measured behavior, per harness.

## Tools

- `assets/scripts/forge_narration_metrics.py <transcript.jsonl> [--label X]` —
  scores a normalized run transcript: assistant output bytes, disallowed
  pre-tool announcements, allowed messages, and the permitted run-start
  acknowledgment (the first pre-tool message is exempt as the run-start ack;
  every later routine announcement counts as disallowed).

## Transcript format

One JSON object per turn, in order:

```
{"role": "assistant", "text": "<message>", "pre_tool": true}
{"role": "tool", "name": "<tool>"}
{"role": "assistant", "text": "<message>", "pre_tool": false}
```

`pre_tool: true` = an assistant message emitted immediately before a tool call.

## Protocol

1. Freeze a fixed, bounded task and the rubric BEFORE any change (a moved
   yardstick invalidates the comparison).
2. Capture ≥3 paired runs, fresh session each, resetting the repo between runs.
3. Score each; use the median. Compare only isolated changes (wording vs. hook
   vs. integrated) so each effect is attributable.

## Pass threshold

Zero disallowed announcements in every run (the run-start ack is permitted) AND
median output bytes ≤ 0.5× the frozen baseline. Blockers and the compact
checkpoint template must be preserved.

## Reference result (1.9.1 -> 1.9.2, Codex, 3-task rig)

Baseline median 29 disallowed / 5742 bytes -> updated ~0 genuine / 529 bytes
(~91% output reduction). See the eval rig and `~/forge-eval-results/`.
