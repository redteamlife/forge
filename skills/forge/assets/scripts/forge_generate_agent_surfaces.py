#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROUTER = """# Repo Agent Guide

Use installed FORGE skills for governed work.

Default read order:
1. `docs/forge/AI.md`
2. `docs/forge/CONTEXT.md` if present
3. `docs/forge/TASKS.index.yaml` or the configured task source
4. one selected task
5. task-relevant source files only

Do not load all `docs/forge/*` files at session start.
Read team, architecture, memory, setup, evaluation, and security checklist docs only when relevant.
"""

STANDARD = """# Repo Agent Guide

@./docs/forge/AI.md

Use installed FORGE skills for governed work. Read `docs/forge/CONTEXT.md`, the compact task index, and one selected task before inspecting task-relevant source files.
"""

FULL = """# Repo Agent Guide

High-context FORGE surface. Use only when explicitly selected for local/developer workflows.

@./docs/forge/AI.md
@./docs/forge/CONTEXT.md
@./docs/forge/TASKS.index.yaml
"""


def surface_text(profile: str, claude_no_includes: bool) -> str:
    if profile == "full":
        return FULL
    if profile == "standard" and not claude_no_includes:
        return STANDARD
    return ROUTER


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate compact FORGE agent surfaces.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--profile", choices=["lite", "standard", "full"], default="lite")
    parser.add_argument("--no-claude-includes", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    text = surface_text(args.profile, args.no_claude_includes)
    for name in ("CLAUDE.md", "AGENTS.md"):
        path = repo / name
        if path.exists() and not args.force:
            print(f"FORGE: exists, not overwritten: {path}")
            continue
        path.write_text(text, encoding="utf-8")
        print(f"FORGE: wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
