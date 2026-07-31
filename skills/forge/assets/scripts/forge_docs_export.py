#!/usr/bin/env python3
"""Export the FORGE application-docs handbook to a publish target.

Targets: `gitlab-wiki` (primary) and `obsidian`. Canonical docs are authored
once (target-neutral, semantic folders, README nav manifest); this script
down-converts. Deterministic, stdlib only — no PyYAML.

SECURITY: publication is a trust boundary. Each doc's `sensitivity`
(public < internal < confidential < restricted) is compared to the target's
max; missing/unknown sensitivity is treated as `restricted` (fail closed).
Behavior on excess is `fail` (abort, default) or `omit` (drop + record; then
fail if any kept page's nav/link references an omitted page). `sensitivity` is
never stripped.

Frontmatter is parsed with a bounded grammar only (documented scalars + simple
lists); the block is otherwise preserved verbatim. The script writes trees; it
never pushes to a remote. Destinations are refused unless empty, already a
managed export (marker present), or --force.

Usage:
  forge_docs_export.py --target {gitlab-wiki|obsidian} --docs-root DIR --out DIR
    [--repo ROOT] [--force] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SENSITIVITY = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
MARKER = ".forge-export-manifest.json"
SCALAR_KEYS = {
    "title", "slug", "doc_type", "status", "sensitivity",
    "reviewed_at", "review_in_days",
}
LIST_KEYS = {"owners", "tags"}


def config_value(repo: Path, field: str) -> str:
    ai = repo / "docs" / "forge" / "AI.md"
    if not ai.is_file():
        return ""
    for line in ai.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith(f"{field}:"):
            return s.split(":", 1)[1].strip().strip("'\"")
    return ""


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return parts[1], parts[2]


def parse_frontmatter(fm: str) -> dict:
    """Bounded grammar: `key: scalar`, `key: [a, b]`, and block lists."""
    data: dict = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        i += 1
        if not s or s.startswith("#") or ":" not in s:
            continue
        key, _, val = s.partition(":")
        key = key.strip()
        val = val.strip()
        if key in LIST_KEYS:
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
            elif val == "":
                items = []
                while i < len(lines) and lines[i].lstrip().startswith("- "):
                    items.append(lines[i].lstrip()[2:].strip().strip("'\""))
                    i += 1
                data[key] = items
            else:
                data[key] = [val.strip("'\"")]
        elif key in SCALAR_KEYS:
            data[key] = val.strip("'\"")
    return data


def sensitivity_rank(value: str) -> int:
    # Missing/unknown -> most restrictive (fail closed).
    return SENSITIVITY.get(value.strip().lower(), SENSITIVITY["restricted"])


def slugify(name: str) -> str:
    base = re.sub(r"^\d+\s*[-_.]\s*", "", name)  # strip any legacy NN- prefix
    base = base.rsplit(".md", 1)[0]
    base = re.sub(r"[^\w./-]+", "-", base).strip("-")
    return base


def collect_docs(docs_root: Path) -> list[Path]:
    return sorted(p for p in docs_root.rglob("*.md"))


def destination_is_safe(out: Path, force: bool) -> tuple[bool, str]:
    if not out.exists():
        return True, ""
    if not any(out.iterdir()):
        return True, ""
    if (out / MARKER).exists():
        return True, ""  # previously managed by us — safe to refresh
    if force:
        return True, ""
    return False, (
        f"destination {out} is non-empty and not a managed FORGE export "
        f"(no {MARKER}); refusing to overwrite. Use --force to override."
    )


def build_plan(docs_root: Path, repo: Path, target: str) -> dict:
    max_sens = config_value(repo, f"{target.replace('-', '_')}_max_sensitivity") or "internal"
    behavior = config_value(repo, "sensitivity_excess_behavior") or "fail"
    max_rank = sensitivity_rank(max_sens)

    kept: list[dict] = []
    omitted: list[dict] = []
    for md in collect_docs(docs_root):
        fm_text, body = split_frontmatter(md.read_text(encoding="utf-8"))
        meta = parse_frontmatter(fm_text)
        rank = sensitivity_rank(meta.get("sensitivity", ""))
        rel = md.relative_to(docs_root)
        entry = {"src": str(rel), "meta": meta, "fm": fm_text, "body": body,
                 "sensitivity_rank": rank}
        if rank > max_rank:
            omitted.append(entry)
        else:
            kept.append(entry)
    return {"target": target, "max_sensitivity": max_sens, "behavior": behavior,
            "kept": kept, "omitted": omitted}


def enforce_classification(plan: dict) -> list[str]:
    """Return blocking errors per the fail/omit policy."""
    errors: list[str] = []
    omitted_names = {e["src"] for e in plan["omitted"]}
    if plan["omitted"]:
        if plan["behavior"] == "fail":
            for e in plan["omitted"]:
                errors.append(
                    f"classification: {e['src']} exceeds {plan['target']} "
                    f"max_sensitivity={plan['max_sensitivity']} (behavior=fail)")
            return errors
        # omit mode: kept pages must not link to omitted ones.
        omit_slugs = {slugify(Path(n).name) for n in omitted_names}
        for e in plan["kept"]:
            for m in re.findall(r"\]\(([^)]+)\)", e["body"]):
                target_slug = slugify(Path(m.split("#", 1)[0]).name)
                if target_slug and target_slug in omit_slugs:
                    errors.append(
                        f"omit: kept page {e['src']} links to omitted page ({m})")
    return errors


def write_manifest(out: Path, plan: dict, outputs: dict[str, str],
                   content_commit: str) -> None:
    manifest = {
        "forge_docs_export": 1,
        "target": plan["target"],
        "max_sensitivity": plan["max_sensitivity"],
        "behavior": plan["behavior"],
        "content_commit": content_commit or None,
        "omitted": sorted(e["src"] for e in plan["omitted"]),
        "outputs": dict(sorted(outputs.items())),
    }
    (out / MARKER).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Adapters are registered by TASK-024 (gitlab-wiki) and TASK-025 (obsidian).
from forge_docs_adapters import render  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", required=True, choices=["gitlab-wiki", "obsidian"])
    parser.add_argument("--docs-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--content-commit", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    docs_root = Path(args.docs_root)
    if not docs_root.is_dir():
        print(f"error: docs-root not found: {docs_root}", file=sys.stderr)
        return 2
    out = Path(args.out)
    repo = Path(args.repo)

    plan = build_plan(docs_root, repo, args.target)
    errors = enforce_classification(plan)
    if errors:
        for e in errors:
            print(f"FORGE: {e}", file=sys.stderr)
        return 1

    outputs = render(args.target, plan)  # {relpath: content}, deterministic

    if args.dry_run:
        print(f"DRY RUN {args.target}: {len(outputs)} pages, "
              f"{len(plan['omitted'])} omitted, max={plan['max_sensitivity']}")
        for rel in sorted(outputs):
            print(f"  {rel}")
        return 0

    ok, msg = destination_is_safe(out, args.force)
    if not ok:
        print(f"FORGE: {msg}", file=sys.stderr)
        return 1

    out.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for rel, content in sorted(outputs.items()):
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        hashes[rel] = sha256(content)
    write_manifest(out, plan, hashes, args.content_commit)
    print(f"FORGE: exported {len(outputs)} pages to {out} "
          f"({len(plan['omitted'])} omitted by classification).")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
