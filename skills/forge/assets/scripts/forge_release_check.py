#!/usr/bin/env python3
"""Provider-neutral release validator (runs in forge-ship Prepare, pre-tag).

Asserts the changelog has an entry for the version being released, and
(optionally) that no application docs are past their review window. Authoritative
pre-tag gate; tag-triggered CI only publishes notes afterward.

Usage:
  forge_release_check.py --version X.Y.Z [--changelog CHANGELOG.md]
    [--docs-root DIR] [--today YYYY-MM-DD]
Exit: 0 = release is publishable; 1 = a gate failed.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def changelog_has_version(changelog: Path, version: str) -> bool:
    if not changelog.is_file():
        return False
    pat = re.compile(r"^##\s*\[?" + re.escape(version) + r"\]?", re.MULTILINE)
    return pat.search(changelog.read_text(encoding="utf-8")) is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", required=True)
    parser.add_argument("--changelog", default="CHANGELOG.md")
    parser.add_argument("--docs-root", default=None)
    parser.add_argument("--today", default=None)
    args = parser.parse_args()

    failed = False

    if not changelog_has_version(Path(args.changelog), args.version):
        print(f"FORGE: {args.changelog} has no entry for version {args.version}.",
              file=sys.stderr)
        failed = True

    if args.docs_root:
        cmd = [sys.executable, str(SCRIPT_DIR / "forge_docs_staleness.py"),
               args.docs_root]
        if args.today:
            cmd += ["--today", args.today]
        r = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if r.returncode != 0:
            print("FORGE: documentation review gate failed:", file=sys.stderr)
            print(r.stdout, file=sys.stderr)
            failed = True

    if failed:
        return 1
    print(f"FORGE: release {args.version} passes pre-tag validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
