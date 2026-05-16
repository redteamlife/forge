#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


BUDGETS = {
    "lite": {"warn": 2500, "fail": 5000},
    "standard": {"warn": 5000, "fail": 10000},
    "full": {"warn": 15000, "fail": 30000},
}

SURFACE_TOKEN_BUDGETS = {
    "CLAUDE.md": 800,
    "AGENTS.md": 800,
    ".cursor/rules/forge.mdc": 700,
    ".github/copilot-instructions.md": 700,
    ".windsurf/rules/forge.md": 700,
    ".codex/hooks.json": 350,
}

FORBIDDEN_LITE_INCLUDES = {
    "SECURITY_CHECKLISTS.md",
    "MEMORY.md",
    "TEAM.md",
    "ARCHITECTURE.md",
    "SETUP.md",
    "EVALUATION.md",
}

FORBIDDEN_SURFACE_PHRASES = (
    "load all docs/forge",
    "read all docs/forge",
    "read every generated file",
    "load every generated file",
)


@dataclass(frozen=True)
class LoadedDoc:
    label: str
    path: Path
    tokens: int


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def find_config_value(text: str, key: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(key)}:\s*([A-Za-z0-9_-]+)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def detect_profile(root: Path, override: str | None) -> str:
    if override:
        return override
    context_text = read_text(root / "docs" / "forge" / "CONTEXT.md")
    profile = find_config_value(context_text, "context_profile")
    if profile in BUDGETS:
        return profile
    ai_text = read_text(root / "docs" / "forge" / "AI.md")
    profile = find_config_value(ai_text, "agent_context_profile")
    return profile if profile in BUDGETS else "lite"


def extract_forge_includes(text: str) -> list[str]:
    matches = re.findall(r"@(?:\./)?(docs/forge/[A-Za-z0-9_./-]+)", text)
    return sorted(dict.fromkeys(matches))


def add_doc(docs: list[LoadedDoc], label: str, path: Path) -> None:
    text = read_text(path)
    if text:
        docs.append(LoadedDoc(label=label, path=path, tokens=estimate_tokens(text)))


def default_loaded_docs(root: Path, claude_includes: list[str]) -> list[LoadedDoc]:
    docs: list[LoadedDoc] = []
    add_doc(docs, "CLAUDE.md", root / "CLAUDE.md")
    if claude_includes:
        for include in claude_includes:
            add_doc(docs, include, root / include)
    else:
        add_doc(docs, "docs/forge/AI.md", root / "docs" / "forge" / "AI.md")
    return docs


def surface_paths(root: Path) -> list[tuple[str, Path]]:
    return [(label, root / label) for label in SURFACE_TOKEN_BUDGETS]


def validate_surface(label: str, path: Path, profile: str) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = []
    text = read_text(path)
    if not text:
        return warnings, failures

    includes = extract_forge_includes(text)
    tokens = estimate_tokens(text)
    limit = SURFACE_TOKEN_BUDGETS[label]
    if tokens > limit:
        warnings.append(f"{label} is {tokens} tokens; budget is {limit}.")

    if profile == "lite":
        if includes:
            failures.append(f"{label} includes docs/forge files in lite mode.")
        lowered = text.lower()
        for phrase in FORBIDDEN_SURFACE_PHRASES:
            if phrase in lowered and f"do not {phrase}" not in lowered:
                warnings.append(f"{label} may encourage broad context loading: '{phrase}'.")
    elif profile == "standard":
        extra = [include for include in includes if include != "docs/forge/AI.md"]
        if extra:
            failures.append(f"{label} includes non-AI.md docs/forge files in standard mode.")

    for include in includes:
        name = Path(include).name
        if name in FORBIDDEN_LITE_INCLUDES:
            failures.append(f"{label} includes {include}.")

    return warnings, failures


def validate(root: Path, profile: str) -> tuple[list[LoadedDoc], list[str], list[str]]:
    warnings: list[str] = []
    failures: list[str] = []

    claude_text = read_text(root / "CLAUDE.md")
    claude_includes = extract_forge_includes(claude_text)
    docs = default_loaded_docs(root, claude_includes)
    total_tokens = sum(doc.tokens for doc in docs)

    for label, path in surface_paths(root):
        surface_warnings, surface_failures = validate_surface(label, path, profile)
        warnings.extend(surface_warnings)
        failures.extend(surface_failures)

    if profile == "lite" and len(claude_includes) > 1:
        failures.append("CLAUDE.md includes more than one docs/forge file in lite mode.")
    if len(claude_includes) > 3:
        warnings.append("CLAUDE.md includes many docs/forge files; prefer router-style context.")

    tasks_yaml = root / "docs" / "forge" / "TASKS.yaml"
    tasks_index = root / "docs" / "forge" / "TASKS.index.yaml"
    if tasks_yaml.exists() and not tasks_index.exists() and tasks_yaml.stat().st_size > 20000:
        warnings.append("TASKS.yaml is large and unsplit; prefer TASKS.index.yaml plus docs/forge/tasks/.")

    checklist = root / "docs" / "forge" / "SECURITY_CHECKLISTS.md"
    split_checklists = root / "docs" / "forge" / "security-checklists"
    if checklist.exists() and not split_checklists.exists() and checklist.stat().st_size > 12000:
        warnings.append("SECURITY_CHECKLISTS.md is large and monolithic; prefer docs/forge/security-checklists/.")

    memory = root / "docs" / "forge" / "MEMORY.md"
    memory_index = root / "docs" / "forge" / "MEMORY.index.yaml"
    if memory.exists() and not memory_index.exists() and memory.stat().st_size > 12000:
        warnings.append("MEMORY.md is large and unsplit; prefer MEMORY.index.yaml plus docs/forge/memory/.")

    budget = BUDGETS[profile]
    if total_tokens >= budget["fail"]:
        failures.append(f"Estimated default context {total_tokens} tokens exceeds {profile} fail budget {budget['fail']}.")
    elif total_tokens >= budget["warn"]:
        warnings.append(f"Estimated default context {total_tokens} tokens exceeds {profile} warn budget {budget['warn']}.")

    return docs, warnings, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate FORGE default context size and agent-surface discipline.")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root to validate.")
    parser.add_argument("--profile", choices=sorted(BUDGETS), help="Override detected context profile.")
    args = parser.parse_args(argv)

    root = Path(args.repo).resolve()
    profile = detect_profile(root, args.profile)
    docs, warnings, failures = validate(root, profile)

    print(f"Context profile: {profile}")
    print("Auto-loaded docs:")
    if docs:
        for doc in docs:
            print(f"  - {doc.label}: {doc.tokens} tokens")
    else:
        print("  - none detected")
    print()
    print("Estimated default context:")
    total = 0
    for doc in docs:
        total += doc.tokens
        print(f"  {doc.label}: {doc.tokens} tokens")
    print(f"  Total: {total} tokens")
    print()
    print("Warnings:")
    if warnings:
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("  - none")

    if failures:
        print()
        print("Failures:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
