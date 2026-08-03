#!/usr/bin/env python3
"""Score a normalized run transcript against the token-discipline rubric.

Input: JSONL, one object per turn:
  {"role": "assistant", "text": "...", "pre_tool": true|false}
  {"role": "tool", "name": "shell"}

Reports (deterministic, harness-neutral):
  - assistant output bytes (proxy for tokens when native counts are unavailable)
  - disallowed pre-tool announcements: assistant turns with pre_tool=true whose
    text is NOT a heartbeat / checkpoint / blocker / terminal-summary line
  - allowed-message tally

A run PASSES the disallowed check with zero disallowed announcements. The
bytes-ratio threshold (<= 0.5 median vs. baseline) is computed across paired
runs by the operator; this scorer reports the per-run number.

Usage: forge_narration_metrics.py run.jsonl [--label NAME]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allowed compact-mode message shapes (positive template).
ALLOWED = [
    re.compile(r"^Status:\s", re.I),                         # heartbeat
    re.compile(r"^TASK-\S+\s+(complete|blocked|handoff-required|escalated)\b", re.I),
    re.compile(r"^Stopped\b", re.I),                          # stop line
    re.compile(r"^Done:\s", re.I),                            # terminal summary
    re.compile(r"\bblock(er|ed)\b|\bneed:\s", re.I),         # blocker/decision
]


def is_allowed(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    first = t.splitlines()[0]
    return any(p.search(first) for p in ALLOWED)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("transcript")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    path = Path(args.transcript)
    if not path.is_file():
        print(f"error: no such transcript: {path}", file=sys.stderr)
        return 2

    out_bytes = 0
    disallowed: list[str] = []
    allowed_count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            turn = json.loads(line)
        except json.JSONDecodeError:
            continue
        if turn.get("role") != "assistant":
            continue
        text = turn.get("text", "") or ""
        out_bytes += len(text.encode("utf-8"))
        if turn.get("pre_tool"):
            if is_allowed(text):
                allowed_count += 1
            else:
                disallowed.append(text.strip().splitlines()[0][:80] if text.strip() else "")

    label = args.label or path.name
    print(f"[{label}]")
    print(f"  assistant_output_bytes: {out_bytes}")
    print(f"  disallowed_pre_tool_announcements: {len(disallowed)}")
    print(f"  allowed_pre_tool_messages: {allowed_count}")
    if disallowed:
        print("  disallowed samples:")
        for d in disallowed[:5]:
            print(f"    - {d}")
    print(f"  disallowed_check: {'PASS' if not disallowed else 'FAIL'}")
    return 0 if not disallowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
