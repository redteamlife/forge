#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def render(profile: str) -> str:
    return f"""# FORGE Context Budget

```yaml
context_profile: {profile}

default_session_reads:
  - docs/forge/AI.md
  - selected task only

never_auto_read:
  - docs/forge/SECURITY_CHECKLISTS.md
  - docs/forge/security-checklists/*
  - docs/forge/MEMORY.md
  - docs/forge/TEAM.md
  - docs/forge/ARCHITECTURE.md
  - docs/forge/SETUP.md
  - docs/forge/EVALUATION.md

read_when:
  TEAM.md: "team mode, ownership conflict, branch claiming ambiguity, or reviewer routing"
  ARCHITECTURE.md: "task touches design boundaries, persistence, interfaces, deployment, data flow, or cross-module behavior"
  SECURITY_CHECKLISTS.md: "explicit security review or security-relevant change surface"
  MEMORY.md: "before closing a task, repeated failure investigation, or user asks about prior decisions"
  EVALUATION.md: "evaluation/reflection tasks only"
  SETUP.md: "environment setup or onboarding tasks only"

hard_rules:
  - "Do not load all docs/forge files at startup."
  - "Do not read every task to select work; use the task index."
  - "Do not load full checklists unless performing a security review."
  - "Prefer selected snippets over whole files when possible."

budgets:
  lite:
    default_context_tokens_warn: 2500
    default_context_tokens_fail: 5000
  standard:
    default_context_tokens_warn: 5000
    default_context_tokens_fail: 10000
  full:
    default_context_tokens_warn: 15000
    default_context_tokens_fail: 30000
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate docs/forge/CONTEXT.md.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--profile", choices=["lite", "standard", "full"], default="lite")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    path = Path(args.repo).resolve() / "docs" / "forge" / "CONTEXT.md"
    if path.exists() and not args.force:
        print(f"FORGE: exists, not overwritten: {path}")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(args.profile), encoding="utf-8")
    print(f"FORGE: wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
