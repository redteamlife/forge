#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_task(repo: Path, task_id: str) -> tuple[dict | None, str]:
    forge_dir = repo / "docs" / "forge"
    index_path = forge_dir / "TASKS.index.yaml"
    legacy_path = forge_dir / "TASKS.yaml"

    if index_path.is_file():
        index = load_yaml(index_path)
        for entry in index.get("tasks", []):
            if str(entry.get("id", "")) != task_id:
                continue
            task = dict(entry)
            task_file = entry.get("task_file")
            if task_file:
                detail_path = repo / str(task_file)
                detail = load_yaml(detail_path)
                if detail:
                    detail.update(task)
                    task = detail
            return task, str(index_path.relative_to(repo))
        return None, str(index_path.relative_to(repo))

    if legacy_path.is_file():
        legacy = load_yaml(legacy_path)
        for task in legacy.get("tasks", []):
            if str(task.get("id", "")) == task_id:
                return task, str(legacy_path.relative_to(repo))
        return None, str(legacy_path.relative_to(repo))

    return None, "docs/forge/TASKS.index.yaml or docs/forge/TASKS.yaml"


def print_field(task: dict, field: str) -> None:
    value = task.get(field)
    if value is None:
        return
    if isinstance(value, list):
        for item in value:
            print(item)
    elif isinstance(value, (dict, tuple)):
        print(json.dumps(value, sort_keys=True))
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve FORGE tasks from split or legacy task ledgers.")
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument("--task", required=True, help="Task id to resolve.")
    parser.add_argument("--field", help="Field to print from the task.")
    parser.add_argument("--json", action="store_true", help="Print the task as JSON.")
    parser.add_argument("--ledger", action="store_true", help="Print the ledger path used.")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    task, ledger = load_task(repo, args.task)
    if task is None:
        print(f"FORGE: Task '{args.task}' not found in {ledger}.", file=sys.stderr)
        return 1

    if args.ledger:
        print(ledger)
    elif args.json:
        print(json.dumps(task, sort_keys=True))
    elif args.field:
        print_field(task, args.field)
    else:
        print(json.dumps(task, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
