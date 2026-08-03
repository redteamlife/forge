#!/usr/bin/env python3
"""Safely upgrade an existing repo's FORGE config and surfaces to the current pack.

Non-destructive by design (design TASK-036): detect first, mutate only with
--apply, back up before editing, and NEVER force-regenerate a customized
(narrative) agent surface. A version bump alone is not a migration.

What it does with --apply:
  - docs/forge/AI.md: patch the FORGE-config block only (never prose) after a
    .bak backup — set forge_version, add `progress_policy: compact` if absent,
    map legacy `response_style: terse` -> remove it (progress_policy governs),
    STOP on any other legacy response_style value.
  - Agent surfaces (CLAUDE.md/AGENTS.md): regenerate ONLY when the file is a
    recognized stock FORGE router (first heading `# Repo Agent Guide`). A
    customized/narrative surface is left untouched and reported for manual edit.

Usage:
  forge_upgrade.py <repo> [--apply] [--version X.Y.Z]
Default (no --apply) is a dry run: report what would change.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STOCK_SURFACE_MARKER = "# Repo Agent Guide"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def config_block_bounds(text: str) -> tuple[int, int] | None:
    m = re.search(r"```FORGE-config\n(.*?)```", text, re.DOTALL)
    if not m:
        return None
    return m.start(1), m.end(1)


def upgrade_ai_md(repo: Path, version: str, apply: bool) -> list[str]:
    ai = repo / "docs" / "forge" / "AI.md"
    text = read(ai)
    if not text:
        return ["AI.md: not found (skip)"]
    bounds = config_block_bounds(text)
    if not bounds:
        return ["AI.md: no FORGE-config block (skip)"]
    start, end = bounds
    block = text[start:end]
    actions: list[str] = []

    # legacy response_style handling
    rs = re.search(r"^response_style:\s*(.+)$", block, re.MULTILINE)
    if rs:
        val = rs.group(1).strip()
        if val == "terse":
            block = re.sub(r"^response_style:\s*terse\s*\n", "", block, flags=re.MULTILINE)
            actions.append("map response_style: terse -> progress_policy (removed legacy field)")
        else:
            return [f"AI.md: STOP — legacy response_style: {val} needs a human decision "
                    f"(map to progress_policy manually). No changes made."]

    # ensure progress_policy present
    if not re.search(r"^progress_policy:", block, re.MULTILINE):
        block = block.rstrip("\n") + "\nprogress_policy: compact\n"
        actions.append("add progress_policy: compact")

    # bump forge_version
    if re.search(r"^forge_version:", block, re.MULTILINE):
        new_block = re.sub(r"^forge_version:.*$", f"forge_version: {version}", block, flags=re.MULTILINE)
        if new_block != block:
            actions.append(f"set forge_version: {version}")
            block = new_block

    if not actions:
        return ["AI.md: already current"]
    if apply:
        ai.with_suffix(".md.bak").write_text(text, encoding="utf-8")
        ai.write_text(text[:start] + block + text[end:], encoding="utf-8")
        actions = [f"AI.md: {a} (backup .md.bak)" for a in actions]
    else:
        actions = [f"AI.md (dry-run): would {a}" for a in actions]
    return actions


def upgrade_surfaces(repo: Path, apply: bool) -> list[str]:
    actions: list[str] = []
    stock: list[str] = []
    for name in ("CLAUDE.md", "AGENTS.md"):
        p = repo / name
        text = read(p)
        if not text:
            continue
        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        if first.strip() == STOCK_SURFACE_MARKER:
            stock.append(name)
        else:
            actions.append(f"{name}: customized/narrative — left untouched; "
                           f"add the output-discipline line manually")
    if stock:
        if apply:
            subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "forge_generate_agent_surfaces.py"),
                 str(repo), "--force"], check=False, capture_output=True)
            actions.append(f"regenerated stock surfaces: {', '.join(stock)}")
        else:
            actions.append(f"would regenerate stock surfaces: {', '.join(stock)}")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--version", default=None)
    args = parser.parse_args()

    repo = Path(args.repo)
    if not (repo / "docs" / "forge").is_dir():
        print(f"error: no docs/forge in {repo}", file=sys.stderr)
        return 2

    version = args.version
    if version is None:
        version = read(SCRIPT_DIR.parent.parent / "VERSION").strip() or "unknown"

    report = upgrade_ai_md(repo, version, args.apply)
    stopped = any(r.startswith("AI.md: STOP") for r in report)
    if not stopped:
        report += upgrade_surfaces(repo, args.apply)

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"FORGE upgrade ({mode}) — {repo}")
    for line in report:
        print(f"  {line}")
    if stopped:
        return 1
    if not args.apply:
        print("  (re-run with --apply to make changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
