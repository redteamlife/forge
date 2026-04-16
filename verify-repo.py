#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT / "skills" / "forge"


class CheckFailure(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise CheckFailure(
            f"Command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def verify_skill_names() -> None:
    for skill_file in sorted(SKILL_ROOT.rglob("SKILL.md")):
        parent = skill_file.parent.name
        lines = skill_file.read_text().splitlines()
        name = None
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---" and not in_frontmatter:
                in_frontmatter = True
                continue
            if line.strip() == "---" and in_frontmatter:
                break
            if in_frontmatter and line.startswith("name: "):
                name = line.split(": ", 1)[1].strip()
                break
        expected = "forge" if skill_file == SKILL_ROOT / "SKILL.md" else f"forge-{parent}"
        ensure(name == expected, f"{skill_file}: name '{name}' does not match expected '{expected}'")


def verify_required_files() -> None:
    required = [
        SKILL_ROOT / "SKILL.md",
        SKILL_ROOT / "bootstrap" / "SKILL.md",
        SKILL_ROOT / "execute-task" / "SKILL.md",
        SKILL_ROOT / "critique" / "SKILL.md",
        SKILL_ROOT / "security-review" / "SKILL.md",
        SKILL_ROOT / "evaluation" / "SKILL.md",
        SKILL_ROOT / "memory" / "SKILL.md",
        SKILL_ROOT / "assets" / "templates" / "AI.md",
        SKILL_ROOT / "assets" / "agent-surfaces" / "AGENTS.md",
    ]
    for path in required:
        ensure(path.exists(), f"Missing required file: {path}")


def verify_manifests() -> None:
    for path in [
        SKILL_ROOT / "assets" / "agent-surfaces" / ".codex" / "hooks.json",
    ]:
        read_json(path)


def verify_shell_scripts() -> None:
    run(["bash", "-n", "install.sh", "uninstall.sh", "verify-install.sh"], cwd=ROOT)


def verify_install_flow() -> None:
    run(["bash", "install.sh", "--force"], cwd=ROOT)
    run(["bash", "verify-install.sh"], cwd=ROOT)
    run(["bash", "uninstall.sh"], cwd=ROOT)


def main() -> int:
    try:
        verify_skill_names()
        verify_required_files()
        verify_manifests()
        verify_shell_scripts()
        verify_install_flow()
    except CheckFailure as exc:
        print(f"FORGE verify failed: {exc}", file=sys.stderr)
        return 1

    print("FORGE verify passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
