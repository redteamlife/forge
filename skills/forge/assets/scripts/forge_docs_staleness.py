#!/usr/bin/env python3
"""Report application docs whose review window has lapsed.

Staleness = `reviewed_at + review_in_days` is before the reference date.
`reviewed_at` (a human confirmed correctness), NOT `updated` (content changed),
drives the clock. Docs missing `reviewed_at` are reported as never-reviewed.

Reads only a bounded set of frontmatter scalars — no general YAML parser, no
PyYAML dependency. Surfaced at release preparation (forge-ship).

Usage: forge_docs_staleness.py <docs_root> [--today YYYY-MM-DD]
Exit: 0 = all fresh; 1 = at least one stale/never-reviewed doc.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path


def scalar(frontmatter: str, key: str) -> str:
    for line in frontmatter.splitlines():
        s = line.strip()
        if s.startswith(f"{key}:"):
            return s.split(":", 1)[1].strip().strip("'\"")
    return ""


def frontmatter_of(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("docs_root")
    parser.add_argument("--today", default=None)
    args = parser.parse_args()

    today = parse_date(args.today) if args.today else date.today()
    if today is None:
        print(f"error: bad --today: {args.today}", file=sys.stderr)
        return 2

    root = Path(args.docs_root)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    stale: list[str] = []
    never: list[str] = []
    for md in sorted(root.rglob("*.md")):
        fm = frontmatter_of(md.read_text(encoding="utf-8"))
        if not fm:
            continue
        reviewed = parse_date(scalar(fm, "reviewed_at"))
        window = scalar(fm, "review_in_days")
        rel = md.relative_to(root)
        if reviewed is None:
            never.append(str(rel))
            continue
        try:
            days = int(window)
        except ValueError:
            days = 90
        if (today - reviewed).days > days:
            stale.append(f"{rel} (reviewed {reviewed}, window {days}d)")

    for item in never:
        print(f"NEVER-REVIEWED: {item}")
    for item in stale:
        print(f"STALE: {item}")
    if not stale and not never:
        print("FORGE: all application docs are within their review window.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
