#!/usr/bin/env python3
"""Generate FORGE agent surfaces (`CLAUDE.md`, `AGENTS.md`).

Two output styles:

- router (default for `lite`): compact pointer text only.
- narrative: a humane front-door briefing (project goal, architecture quick
  view, stack, layout, role split). Stays compatible with the lite
  context-validator: it must not include `@docs/forge/*` files in lite mode.
"""
from __future__ import annotations

import argparse
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"
NARRATIVE_TEMPLATE = TEMPLATES_DIR / "AGENTS.narrative.md"
SCOPED_RULES_DIR = (
    SCRIPT_DIR.parent / "agent-surfaces" / ".cursor" / "rules-scoped"
)


# Stack -> scoped rule file. `project-conventions` and `security` are
# emitted unconditionally when scoped rules are requested.
STACK_RULES: dict[str, str] = {
    "python": "python-backend.mdc",
    "js": "js-frontend.mdc",
    "ts": "js-frontend.mdc",
    "go": "go-backend.mdc",
}


def detect_stacks(repo: Path) -> list[str]:
    """Cheap stack detection by marker files. Returns a deduped list."""
    stacks: list[str] = []
    markers = {
        "python": ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile"),
        "js": ("package.json",),
        "go": ("go.mod",),
    }
    seen: set[str] = set()
    for stack, files in markers.items():
        for name in files:
            if (repo / name).exists():
                if stack not in seen:
                    stacks.append(stack)
                    seen.add(stack)
                break
    # Probe top-level subdirs cheaply for the most common layouts.
    candidates = ["backend", "frontend", "src", "app", "server", "web"]
    for sub in candidates:
        path = repo / sub
        if not path.is_dir():
            continue
        for stack, files in markers.items():
            for name in files:
                if (path / name).exists() and stack not in seen:
                    stacks.append(stack)
                    seen.add(stack)
                    break
    return stacks


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


DEFAULTS = {
    "PROJECT_NAME": "This Project",
    "PROJECT_GOAL": (
        "Replace this paragraph with one or two sentences describing what the "
        "project does and who uses it."
    ),
    "TECH_STACK": (
        "- Language / runtime:\n"
        "- Framework:\n"
        "- Datastore:\n"
        "- Tests:\n"
        "- CI:"
    ),
    "REPO_LAYOUT": (
        "```\n"
        "repo/\n"
        "├─ docs/forge/                 # FORGE governance docs (read on demand)\n"
        "├─ src/                        # implementation\n"
        "└─ tests/                      # tests\n"
        "```"
    ),
    "ROLE_SPLIT": (
        "Single-operator project. If this becomes a multi-person codebase, "
        "split roles by area (for example, `backend` vs `frontend`) and name "
        "the shared contract file (OpenAPI, protobuf, schema, etc.) as the "
        "integration seam. Record the split in `docs/forge/TEAM.md`."
    ),
}


def narrative_text(values: dict[str, str]) -> str:
    template = NARRATIVE_TEMPLATE.read_text(encoding="utf-8")
    for key, default in DEFAULTS.items():
        template = template.replace("{{" + key + "}}", values.get(key) or default)
    return template


def surface_text(
    profile: str,
    claude_no_includes: bool,
    narrative: bool,
    narrative_values: dict[str, str],
) -> str:
    if narrative:
        return narrative_text(narrative_values)
    if profile == "full":
        return FULL
    if profile == "standard" and not claude_no_includes:
        return STANDARD
    return ROUTER


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate FORGE agent surfaces.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--profile", choices=["lite", "standard", "full"], default="lite")
    parser.add_argument("--no-claude-includes", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--narrative",
        action="store_true",
        help="Emit a narrative AGENTS.md/CLAUDE.md (project briefing) instead of the router.",
    )
    parser.add_argument("--project-name")
    parser.add_argument("--project-goal")
    parser.add_argument("--tech-stack")
    parser.add_argument("--repo-layout")
    parser.add_argument("--role-split")
    parser.add_argument(
        "--narrative-target",
        choices=["agents", "claude", "both"],
        default="both",
        help="Which surface receives the narrative form. CLAUDE.md may stay a router even when AGENTS.md is narrative.",
    )
    parser.add_argument(
        "--scoped-rules",
        action="store_true",
        help=(
            "Also emit scoped Cursor rule files under .cursor/rules/ based on "
            "detected stacks (python, js/ts, go). Always emits "
            "project-conventions.mdc and security.mdc."
        ),
    )
    parser.add_argument(
        "--stacks",
        default="",
        help=(
            "Comma-separated stack overrides (python,js,ts,go). When provided, "
            "skip auto-detection."
        ),
    )
    args = parser.parse_args()

    values = {
        "PROJECT_NAME": args.project_name,
        "PROJECT_GOAL": args.project_goal,
        "TECH_STACK": args.tech_stack,
        "REPO_LAYOUT": args.repo_layout,
        "ROLE_SPLIT": args.role_split,
    }

    repo = Path(args.repo).resolve()
    router = surface_text(args.profile, args.no_claude_includes, False, values)
    briefing = narrative_text(values) if args.narrative else None

    def pick(name: str) -> str:
        if not args.narrative:
            return router
        if name == "AGENTS.md" and args.narrative_target in ("agents", "both"):
            return briefing  # type: ignore[return-value]
        if name == "CLAUDE.md" and args.narrative_target in ("claude", "both"):
            return briefing  # type: ignore[return-value]
        return router

    for name in ("CLAUDE.md", "AGENTS.md"):
        text = pick(name)
        path = repo / name
        if path.exists() and not args.force:
            print(f"FORGE: exists, not overwritten: {path}")
            continue
        path.write_text(text, encoding="utf-8")
        print(f"FORGE: wrote {path}")

    if args.scoped_rules:
        emit_scoped_rules(repo, args.stacks, args.force)
    return 0


def emit_scoped_rules(repo: Path, stacks_override: str, force: bool) -> None:
    if stacks_override:
        stacks = [s.strip() for s in stacks_override.split(",") if s.strip()]
    else:
        stacks = detect_stacks(repo)

    targets: list[str] = ["project-conventions.mdc", "security.mdc"]
    seen: set[str] = set(targets)
    for stack in stacks:
        rule = STACK_RULES.get(stack)
        if rule and rule not in seen:
            targets.append(rule)
            seen.add(rule)

    out_dir = repo / ".cursor" / "rules"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in targets:
        src = SCOPED_RULES_DIR / name
        if not src.exists():
            print(f"FORGE: scoped rule template missing: {src}")
            continue
        dest = out_dir / name
        if dest.exists() and not force:
            print(f"FORGE: exists, not overwritten: {dest}")
            continue
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"FORGE: wrote {dest}")


if __name__ == "__main__":
    raise SystemExit(main())
