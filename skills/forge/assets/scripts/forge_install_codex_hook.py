#!/usr/bin/env python3
"""Install/upgrade the FORGE Codex SessionStart hook into a repo, merge-safe.

Design TASK-037. Never overwrites unrelated hooks. Identifies the FORGE entry by
the canonical command path (`.codex/hooks/forge_session_context.py`) and also
recognizes the legacy 1.9.x inline-echo hook by signature so it can be replaced.
Fails closed on malformed JSON. A hook is not active until the project is trusted
in Codex — this only writes the file.

Usage: forge_install_codex_hook.py <repo> [--apply]
Default is a dry run.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ASSET_DIR = SCRIPT_DIR.parent / "agent-surfaces" / ".codex"
CANONICAL_CMD = "python3 .codex/hooks/forge_session_context.py"
LEGACY_SIGNATURE = "This repo uses FORGE governance"  # 1.9.x inline echo


def is_forge_entry(group: dict) -> bool:
    for h in group.get("hooks", []):
        if CANONICAL_CMD in str(h.get("command", "")):
            return True
    # top-level legacy shape: {"type":"command","command":"echo '...FORGE...'"}
    if LEGACY_SIGNATURE in str(group.get("command", "")):
        return True
    for h in group.get("hooks", []):
        if LEGACY_SIGNATURE in str(h.get("command", "")):
            return True
    return False


def desired_group() -> dict:
    return {
        "matcher": "startup|resume|clear|compact",
        "hooks": [{"type": "command", "command": CANONICAL_CMD}],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo)
    hooks_json = repo / ".codex" / "hooks.json"

    existing: dict = {"hooks": {}}
    if hooks_json.is_file():
        try:
            existing = json.loads(hooks_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"FORGE: STOP — {hooks_json} is malformed JSON ({exc}); "
                  f"refusing to write. Fix or remove it first.", file=sys.stderr)
            return 1
        if not isinstance(existing.get("hooks"), dict):
            print(f"FORGE: STOP — unexpected hooks.json shape; refusing to write.",
                  file=sys.stderr)
            return 1

    session = existing["hooks"].get("SessionStart", [])
    # drop any existing FORGE/legacy entries; keep everything else untouched
    kept = [g for g in session if not is_forge_entry(g)]
    removed = len(session) - len(kept)
    kept.append(desired_group())
    existing["hooks"]["SessionStart"] = kept
    existing["_forge_managed"] = (
        "FORGE SessionStart entry identified by the canonical command path; "
        "re-running this installer replaces only that entry."
    )

    action = (f"replace {removed} FORGE/legacy entr{'y' if removed==1 else 'ies'}"
              if removed else "add FORGE entry")
    unrelated = len(kept) - 1
    if not args.apply:
        print(f"DRY RUN: would {action} in {hooks_json} "
              f"({unrelated} unrelated SessionStart entr{'y' if unrelated==1 else 'ies'} preserved). "
              f"Re-run with --apply.")
        return 0

    (repo / ".codex" / "hooks").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSET_DIR / "hooks" / "forge_session_context.py",
                 repo / ".codex" / "hooks" / "forge_session_context.py")
    hooks_json.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"FORGE: {action}; installed .codex/hooks/forge_session_context.py "
          f"({unrelated} unrelated entries preserved). Trust the project in Codex to activate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
