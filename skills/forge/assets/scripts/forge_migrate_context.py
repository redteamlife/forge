#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def backup(path: Path) -> None:
    if path.exists():
        target = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, target)
        print(f"FORGE: backup {target}")


def run(args: list[str]) -> None:
    result = subprocess.run(args, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def ensure_ai_profile(repo: Path, profile: str) -> None:
    ai = repo / "docs" / "forge" / "AI.md"
    if not ai.exists():
        return
    text = ai.read_text(encoding="utf-8")
    if "agent_context_profile:" in text:
        text = "\n".join(
            f"agent_context_profile: {profile}" if line.strip().startswith("agent_context_profile:") else line
            for line in text.splitlines()
        ) + "\n"
    elif "task_source:" in text:
        text = text.replace("task_source: local", f"task_source: local\nagent_context_profile: {profile}", 1)
    else:
        text += f"\nagent_context_profile: {profile}\n"
    ai.write_text(text, encoding="utf-8")
    print(f"FORGE: updated {ai}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate a repo to context-safe FORGE surfaces.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--profile", choices=["lite", "standard", "full"], default="lite")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    for name in ("CLAUDE.md", "AGENTS.md", "docs/forge/CONTEXT.md"):
        backup(repo / name)
    ensure_ai_profile(repo, args.profile)
    run([sys.executable, str(SCRIPT_DIR / "forge_context_budget.py"), str(repo), "--profile", args.profile, "--force"])
    run([
        sys.executable,
        str(SCRIPT_DIR / "forge_generate_agent_surfaces.py"),
        str(repo),
        "--profile",
        args.profile,
        "--force",
    ])
    run([sys.executable, str(SCRIPT_DIR / "forge_validate_context.py"), str(repo), "--profile", args.profile])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
