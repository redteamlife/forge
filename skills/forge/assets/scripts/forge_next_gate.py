#!/usr/bin/env python3
"""Print the next required review gate for a FORGE task checkpoint.

Deterministic conductor for the execute-task loop: reads docs/forge/AI.md and
one task file, applies the mode/artifact-aware gate rules, and prints exactly
one line — the next gate to run, or `checkpoint-complete`. Lets small models
and non-skill harnesses follow the loop without probabilistic skill chaining.

Usage: forge_next_gate.py <task-file> [--repo <repo-root>]

Gate order and rules (design TASK-011 v2, D1/D5):
  critique    always required
  security    required unless recorded (pass | n/a | escalated);
              `n/a` must be recorded, not skipped
  evaluation  full gate when docs/forge/EVALUATION.md exists; always recorded
  memory      only when memory docs exist; `no-relevant-lesson` is fine
Blocking outcomes (fail | escalated | handoff-required) print as `blocked:<gate>`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

GATE_ORDER = ["critique", "security", "evaluation", "memory"]
VALID = {
    "critique": {"pass", "fail"},
    "security": {"pass", "n/a", "escalated"},
    "evaluation": {"pass", "handoff-required", "fail"},
    "memory": {"entry", "no-relevant-lesson", "store-unavailable"},
}
BLOCKING = {"fail", "escalated", "handoff-required"}


def parse_gates(task_file: Path) -> dict[str, str]:
    """Flat parse of the task file's `gates:` block; no YAML dependency."""
    gates: dict[str, str] = {}
    in_block = False
    for raw in task_file.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("gates:"):
            in_block = True
            continue
        if in_block:
            if line and not line.startswith((" ", "\t")):
                break
            stripped = line.strip()
            if ":" in stripped and not stripped.startswith("#"):
                key, _, value = stripped.partition(":")
                gates[key.strip()] = value.strip().strip("'\"")
    return gates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("task_file")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()

    task_file = Path(args.task_file)
    if not task_file.is_file():
        print(f"error: no such task file: {task_file}", file=sys.stderr)
        return 2
    repo = Path(args.repo)
    forge_dir = repo / "docs" / "forge"

    memory_exists = (forge_dir / "MEMORY.index.yaml").is_file() or (
        forge_dir / "MEMORY.md"
    ).is_file()

    gates = parse_gates(task_file)

    for gate in GATE_ORDER:
        recorded = gates.get(gate, "")
        if recorded:
            if recorded not in VALID[gate]:
                print(f"invalid:{gate}={recorded}")
                return 1
            if recorded in BLOCKING:
                print(f"blocked:{gate}")
                return 1
            continue
        if gate == "memory" and not memory_exists:
            continue
        print(gate)
        return 0

    print("checkpoint-complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
