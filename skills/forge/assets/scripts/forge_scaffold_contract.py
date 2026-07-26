#!/usr/bin/env python3
"""Scaffold a contract-first surface for a FORGE repo.

Emits:

- a contract file stub (`openapi.yaml`, `api.proto`, or `schema.graphql`)
- a Makefile snippet describing `make openapi` / `make check-openapi`
  (OpenAPI only; protobuf/graphql users typically have their own toolchain)
- a CI workflow stub that fails when the committed contract drifts from the
  live application

Idempotent: existing files are not overwritten unless `--force` is passed.
"""
from __future__ import annotations

import argparse
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates" / "contracts"


KIND_FILES = {
    "openapi": [
        (TEMPLATES_DIR / "openapi" / "openapi.yaml", "openapi.yaml"),
        (
            TEMPLATES_DIR / "openapi" / "Makefile.snippet",
            "docs/forge/contracts/Makefile.snippet",
        ),
        (
            TEMPLATES_DIR / "openapi" / "check-openapi-drift.yml",
            ".github/workflows/check-openapi-drift.yml",
        ),
    ],
    "protobuf": [
        (TEMPLATES_DIR / "protobuf" / "api.proto", "proto/api.proto"),
    ],
    "graphql": [
        (TEMPLATES_DIR / "graphql" / "schema.graphql", "schema.graphql"),
    ],
}


def render(src: Path, project_name: str) -> str:
    return src.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", project_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a contract-first surface.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument(
        "--kind",
        choices=sorted(KIND_FILES),
        default="openapi",
        help="Which contract surface to scaffold.",
    )
    parser.add_argument(
        "--project-name",
        default="This Project",
        help="Project name used to render contract-file headers.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files.",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    wrote: list[Path] = []
    skipped: list[Path] = []

    for src, rel_target in KIND_FILES[args.kind]:
        dest = repo / rel_target
        if dest.exists() and not args.force:
            skipped.append(dest)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(src, args.project_name), encoding="utf-8")
        wrote.append(dest)

    for path in wrote:
        print(f"FORGE: wrote {path}")
    for path in skipped:
        print(f"FORGE: exists, not overwritten: {path}")

    if wrote and args.kind == "openapi":
        print()
        print(
            "Next: merge docs/forge/contracts/Makefile.snippet into your project "
            "Makefile, replace the `your-app dump-openapi` placeholder with the "
            "real command for your framework, and record the contract file in "
            "docs/forge/ARCHITECTURE.md under 'Contract Artifacts'."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
