#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT / "skills" / "forge"


class CheckFailure(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run(
    args: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False, env=env)
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
        SKILL_ROOT / "plan" / "SKILL.md",
        SKILL_ROOT / "build" / "SKILL.md",
        SKILL_ROOT / "review" / "SKILL.md",
        SKILL_ROOT / "ship" / "SKILL.md",
        SKILL_ROOT / "execute-task" / "SKILL.md",
        SKILL_ROOT / "critique" / "SKILL.md",
        SKILL_ROOT / "security-review" / "SKILL.md",
        SKILL_ROOT / "evaluation" / "SKILL.md",
        SKILL_ROOT / "memory" / "SKILL.md",
        SKILL_ROOT / "cross-project" / "SKILL.md",
        SKILL_ROOT / "assets" / "templates" / "AI.md",
        SKILL_ROOT / "assets" / "templates" / "CONTEXT.md",
        SKILL_ROOT / "assets" / "templates" / "MEMORY.index.yaml",
        SKILL_ROOT / "assets" / "templates" / "SKILL-ANATOMY.md",
        SKILL_ROOT / "assets" / "templates" / "TASKS.index.yaml",
        SKILL_ROOT / "assets" / "templates" / "tasks" / "TASK-001.yaml",
        SKILL_ROOT / "assets" / "templates" / "team" / "claiming.md",
        SKILL_ROOT / "assets" / "templates" / "team" / "release.md",
        SKILL_ROOT / "assets" / "templates" / "team" / "trackers.md",
        SKILL_ROOT / "assets" / "templates" / "team" / "contracts.md",
        SKILL_ROOT / "assets" / "templates" / "memory" / "decisions.md",
        SKILL_ROOT / "assets" / "templates" / "memory" / "failures.md",
        SKILL_ROOT / "assets" / "templates" / "memory" / "conventions.md",
        SKILL_ROOT / "assets" / "templates" / "memory" / "project-facts.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "README.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "COORDINATION.yaml",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "contracts" / "README.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "contracts" / "contract-template.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "decisions" / "XPD-0001-template.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "inbox" / "README.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "inbox" / "draft-template.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "concepts" / "README.md",
        SKILL_ROOT / "assets" / "cross-project" / "templates" / "sister-repo-pointer.md",
        SKILL_ROOT / "assets" / "agent-surfaces" / "AGENTS.md",
        SKILL_ROOT / "references" / "repo-flavors.md",
        SKILL_ROOT / "references" / "agent-flavors.md",
        SKILL_ROOT / "references" / "team-claiming.md",
        SKILL_ROOT / "references" / "team-release.md",
        SKILL_ROOT / "references" / "team-trackers.md",
        SKILL_ROOT / "references" / "team-contracts.md",
        SKILL_ROOT / "references" / "devsecops-gates.md",
        SKILL_ROOT / "references" / "application-docs.md",
        SKILL_ROOT / "references" / "cross-project.md",
        SKILL_ROOT / "references" / "lifecycle-map.md",
        SKILL_ROOT / "references" / "skill-anatomy.md",
        SKILL_ROOT / "assets" / "application-docs" / "tool-overview.md",
        SKILL_ROOT / "assets" / "application-docs" / "developer-guide.md",
        SKILL_ROOT / "assets" / "application-docs" / "adr" / "0001-record-architecture-decisions.md",
        SKILL_ROOT / "assets" / "ci" / "hooks" / "pre-commit",
        SKILL_ROOT / "assets" / "ci" / "hooks" / "commit-msg",
        SKILL_ROOT / "assets" / "ci" / "hooks" / "pre-push",
        SKILL_ROOT / "assets" / "ci" / "docs" / "commit-format.md",
        SKILL_ROOT / "assets" / "ci" / "docs" / "validators.md",
        SKILL_ROOT / "assets" / "ci" / "docs" / "governance-patterns.md",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "forge-governance.yml",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "verify-team-closeout.sh",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "forge_task_resolver.py",
        SKILL_ROOT / "assets" / "scripts" / "install-forge-hooks.sh",
        SKILL_ROOT / "assets" / "scripts" / "install-forge-hooks.ps1",
        SKILL_ROOT / "assets" / "scripts" / "forge_context_budget.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_generate_agent_surfaces.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_migrate_context.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_validate_context.py",
    ]
    for path in required:
        ensure(path.exists(), f"Missing required file: {path}")


def verify_manifests() -> None:
    for path in [
        SKILL_ROOT / "assets" / "agent-surfaces" / ".codex" / "hooks.json",
    ]:
        read_json(path)


def verify_skill_anatomy() -> None:
    core_skills = [
        SKILL_ROOT / "execute-task" / "SKILL.md",
        SKILL_ROOT / "critique" / "SKILL.md",
        SKILL_ROOT / "security-review" / "SKILL.md",
        SKILL_ROOT / "evaluation" / "SKILL.md",
        SKILL_ROOT / "cross-project" / "SKILL.md",
    ]
    required_markers = [
        "## Use When",
        "## Do Not Use When",
        "## Hard Stops",
        "## Rationalizations To Reject",
    ]
    for path in core_skills:
        text = path.read_text()
        for marker in required_markers:
            ensure(marker in text, f"{path}: missing skill anatomy marker {marker}")
        ensure(
            "## Evidence Required" in text or "## Evidence" in text,
            f"{path}: missing evidence section",
        )


def verify_size_budgets() -> None:
    budgets = {
        SKILL_ROOT / "SKILL.md": 3200,
        SKILL_ROOT / "bootstrap" / "SKILL.md": 5000,
        SKILL_ROOT / "execute-task" / "SKILL.md": 5200,
        SKILL_ROOT / "assets" / "templates" / "AI.md": 3200,
        SKILL_ROOT / "assets" / "templates" / "TEAM.md": 3200,
        SKILL_ROOT / "assets" / "agent-surfaces" / "AGENTS.md": 1600,
        SKILL_ROOT / "assets" / "agent-surfaces" / ".cursor" / "rules" / "forge.mdc": 1500,
        SKILL_ROOT / "assets" / "agent-surfaces" / ".github" / "copilot-instructions.md": 1500,
        SKILL_ROOT / "assets" / "agent-surfaces" / ".windsurf" / "rules" / "forge.md": 1500,
        SKILL_ROOT / "assets" / "agent-surfaces" / ".codex" / "hooks.json": 800,
    }
    for path, limit in budgets.items():
        size = path.stat().st_size
        ensure(size <= limit, f"{path}: size {size} exceeds budget {limit}")


def verify_shell_scripts() -> None:
    run(["bash", "-n", "install.sh", "uninstall.sh", "verify-install.sh"], cwd=ROOT)
    hooks_dir = SKILL_ROOT / "assets" / "ci" / "hooks"
    for hook in sorted(hooks_dir.iterdir()):
        if hook.is_file():
            run(["bash", "-n", str(hook.relative_to(ROOT))], cwd=ROOT)
    scripts_dir = SKILL_ROOT / "assets" / "scripts"
    for script in sorted(scripts_dir.glob("*.sh")):
        run(["bash", "-n", str(script.relative_to(ROOT))], cwd=ROOT)
    ci_scripts_dir = SKILL_ROOT / "assets" / "ci" / "scripts"
    for script in sorted(ci_scripts_dir.glob("*.sh")):
        run(["bash", "-n", str(script.relative_to(ROOT))], cwd=ROOT)


def verify_python_scripts() -> None:
    scripts_dir = SKILL_ROOT / "assets" / "scripts"
    for script in sorted(scripts_dir.glob("*.py")):
        run([sys.executable, "-m", "py_compile", str(script.relative_to(ROOT))], cwd=ROOT)
    ci_scripts_dir = SKILL_ROOT / "assets" / "ci" / "scripts"
    for script in sorted(ci_scripts_dir.glob("*.py")):
        run([sys.executable, "-m", "py_compile", str(script.relative_to(ROOT))], cwd=ROOT)


def verify_context_validation() -> None:
    script = SKILL_ROOT / "assets" / "scripts" / "forge_validate_context.py"
    with tempfile.TemporaryDirectory(prefix="forge-context-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = repo / "docs" / "forge"
        forge_dir.mkdir(parents=True)
        (forge_dir / "AI.md").write_text("agent_context_profile: lite\n", encoding="utf-8")
        (forge_dir / "CONTEXT.md").write_text("context_profile: lite\n", encoding="utf-8")
        (repo / "CLAUDE.md").write_text(
            "# Repo Agent Guide\n\nRead docs/forge/AI.md and the selected task only.\n",
            encoding="utf-8",
        )
        result = run([sys.executable, str(script), str(repo)], cwd=ROOT)
        ensure("Context profile: lite" in result.stdout, "validate-context did not report lite profile")
        ensure("Warnings:\n  - none" in result.stdout, "validate-context reported unexpected warnings")

    with tempfile.TemporaryDirectory(prefix="forge-context-bomb-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = repo / "docs" / "forge"
        forge_dir.mkdir(parents=True)
        (forge_dir / "AI.md").write_text("agent_context_profile: lite\n", encoding="utf-8")
        (forge_dir / "CONTEXT.md").write_text("context_profile: lite\n", encoding="utf-8")
        (forge_dir / "MEMORY.md").write_text("# Memory\n", encoding="utf-8")
        (forge_dir / "TEAM.md").write_text("# Team\n", encoding="utf-8")
        (repo / "CLAUDE.md").write_text(
            "@./docs/forge/AI.md\n@./docs/forge/MEMORY.md\n@./docs/forge/TEAM.md\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(script), str(repo)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        ensure(result.returncode != 0, "validate-context allowed lite include bomb")
        ensure("includes more than one docs/forge file" in result.stdout, "missing include-bomb failure")


def verify_install_flow() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-verify-") as temp_dir:
        env = os.environ.copy()
        env["FORGE_SKILL_TARGET"] = str(Path(temp_dir) / "skills")

        run(["bash", "install.sh", "--force"], cwd=ROOT, env=env)
        run(["bash", "verify-install.sh"], cwd=ROOT, env=env)
        run(["bash", "uninstall.sh"], cwd=ROOT, env=env)


def main() -> int:
    try:
        verify_skill_names()
        verify_required_files()
        verify_manifests()
        verify_skill_anatomy()
        verify_size_budgets()
        verify_shell_scripts()
        verify_python_scripts()
        verify_context_validation()
        verify_install_flow()
    except CheckFailure as exc:
        print(f"FORGE verify failed: {exc}", file=sys.stderr)
        return 1

    print("FORGE verify passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
