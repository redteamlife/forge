#!/usr/bin/env python3
"""FORGE Codex SessionStart hook — inject governance + output discipline.

Runs on startup/resume/clear/compact. Its stdout becomes Codex developer
context, so the output-discipline rule is re-established after compaction (the
one thing a once-loaded reference cannot do). Reads docs/forge/AI.md with a
fixed-enum parse of `progress_policy` only — never evaluates project-controlled
text. Emits no secrets and performs no repository mutation.
"""
from __future__ import annotations

import re
from pathlib import Path


def progress_policy() -> str:
    ai = Path("docs/forge/AI.md")
    if not ai.is_file():
        return "compact"
    for line in ai.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*progress_policy:\s*(checkpoint|compact|detailed)\s*$", line)
        if m:
            return m.group(1)
    return "compact"


def main() -> int:
    if not Path("docs/forge").is_dir():
        return 0  # not a FORGE repo; stay silent
    policy = progress_policy()
    print(
        "This repo uses FORGE. Route implementation through the forge skills. "
        f"progress_policy is {policy}: do not announce routine reads, searches, "
        "edits, commands, or checks; a host progress cadence is a heartbeat "
        "floor, not narration license. Emit only checkpoint lines, blockers, and "
        "one terminal summary. Read docs/forge/AI.md and one selected task; do "
        "not load all docs/forge files at startup."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
