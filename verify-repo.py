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


def verify_skill_frontmatter_yaml() -> None:
    """Frontmatter must parse under strict YAML: installer CLIs (e.g. Vercel
    skills) reject e.g. unquoted scalars containing ': '."""
    import yaml

    for skill_file in sorted(SKILL_ROOT.rglob("SKILL.md")):
        text = skill_file.read_text()
        parts = text.split("---", 2)
        ensure(len(parts) >= 3, f"{skill_file}: missing frontmatter block")
        try:
            data = yaml.safe_load(parts[1])
        except yaml.YAMLError as exc:
            raise CheckFailure(f"{skill_file}: frontmatter is not strict YAML: {exc}") from exc
        ensure(isinstance(data, dict) and "name" in data and "description" in data,
               f"{skill_file}: frontmatter must define name and description")


def verify_version_sync() -> None:
    import re

    version = (SKILL_ROOT / "VERSION").read_text().strip()
    ensure(re.fullmatch(r"\d+\.\d+\.\d+", version) is not None,
           f"skills/forge/VERSION is not a semver: '{version}'")
    ai_md = (SKILL_ROOT / "assets" / "templates" / "AI.md").read_text()
    m = re.search(r"^forge_version:\s*(\S+)$", ai_md, re.MULTILINE)
    ensure(m is not None, "templates/AI.md is missing forge_version")
    ensure(m.group(1) == version,
           f"VERSION ({version}) != templates/AI.md forge_version ({m.group(1)})")
    changelog = (ROOT / "CHANGELOG.md").read_text()
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.MULTILINE)
    ensure(m is not None, "CHANGELOG.md has no released version entry")
    ensure(m.group(1) == version,
           f"VERSION ({version}) != newest CHANGELOG entry ({m.group(1)})")


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
        SKILL_ROOT / "references" / "execution-modes.md",
        SKILL_ROOT / "references" / "release-management.md",
        SKILL_ROOT / "assets" / "scripts" / "forge_next_gate.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_docs_staleness.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_docs_export.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_docs_adapters.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_release_check.py",
        SKILL_ROOT / "assets" / "templates" / "CHANGELOG.md",
        SKILL_ROOT / "assets" / "agent-surfaces" / ".claude" / "settings.forge-fragment.json",
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
        SKILL_ROOT / "assets" / "ci" / "workflows" / "forge-quality.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "scorecard.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "codeql.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "codeql-config.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "semgrep.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "dependency-review.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "osv-scanner.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "sbom.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "security" / "zap-baseline.yml",
        SKILL_ROOT / "assets" / "ci" / "gitlab" / "security.gitlab-ci.yml",
        SKILL_ROOT / "assets" / "ci" / "workflows" / "release-branch-guard.yml",
        SKILL_ROOT / "assets" / "scripts" / "forge-promote.sh",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "verify-team-closeout.sh",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "forge_task_resolver.py",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "validate-generated-docs.sh",
        SKILL_ROOT / "assets" / "templates" / "AGENTS.narrative.md",
        SKILL_ROOT / "assets" / "templates" / "SECURITY.md",
        SKILL_ROOT / "assets" / "templates" / "dependabot.yml",
        SKILL_ROOT / "assets" / "templates" / "CODEOWNERS",
        SKILL_ROOT / "assets" / "templates" / "gitignore.starter",
        SKILL_ROOT / "assets" / "templates" / "contracts" / "openapi" / "openapi.yaml",
        SKILL_ROOT / "assets" / "templates" / "contracts" / "protobuf" / "api.proto",
        SKILL_ROOT / "assets" / "templates" / "contracts" / "graphql" / "schema.graphql",
        SKILL_ROOT / "assets" / "agent-surfaces" / ".cursor" / "rules-scoped" / "project-conventions.mdc",
        SKILL_ROOT / "assets" / "agent-surfaces" / ".cursor" / "rules-scoped" / "security.mdc",
        SKILL_ROOT / "assets" / "security-checklists" / "general.md",
        SKILL_ROOT / "bootstrap" / "references" / "scaffolding.md",
        SKILL_ROOT / "bootstrap" / "references" / "setup-interview.md",
        SKILL_ROOT / "bootstrap" / "references" / "doc-minimums.md",
        SKILL_ROOT / "bootstrap" / "references" / "team-mode.md",
        SKILL_ROOT / "assets" / "scripts" / "install-forge-hooks.sh",
        SKILL_ROOT / "assets" / "scripts" / "install-forge-hooks.ps1",
        SKILL_ROOT / "assets" / "scripts" / "forge_context_budget.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_generate_agent_surfaces.py",
        SKILL_ROOT / "assets" / "scripts" / "forge_scaffold_contract.py",
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
        # Raised 5200 -> 5400 for the checkpoint gate loop (design TASK-011 D1).
        SKILL_ROOT / "execute-task" / "SKILL.md": 5400,
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


def verify_yaml_assets() -> None:
    import yaml

    yaml_files = sorted((SKILL_ROOT / "assets" / "ci").rglob("*.yml")) + sorted(
        (SKILL_ROOT / "assets" / "ci").rglob("*.yaml")
    )
    ensure(
        any("security" in str(p) for p in yaml_files),
        "assets/ci is missing the security workflow assets",
    )
    for path in yaml_files:
        try:
            yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            raise CheckFailure(f"{path}: invalid YAML: {exc}") from exc


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


def _write_generated_docs_fixture(
    repo: Path,
    forge_mode: str = "Lightweight",
    security_profile: str = "baseline",
    setup_sections: list[str] | None = None,
) -> Path:
    forge_dir = repo / "docs" / "forge"
    (forge_dir / "tasks").mkdir(parents=True)
    (forge_dir / "AI.md").write_text(
        "# AI Execution Configuration\n\n"
        "```FORGE-config\n"
        f"FORGE_mode: {forge_mode}\n"
        "execution_mode: manual\n"
        "collaboration_mode: solo\n"
        f"security_profile: {security_profile}\n"
        "```\n\n"
        "## Purpose\n\nFixture repo.\n\n"
        "## Constraints\n\nNone.\n",
        encoding="utf-8",
    )
    (forge_dir / "TASKS.index.yaml").write_text(
        "tasks:\n"
        "  - id: TASK-001\n"
        '    title: "Fixture task"\n'
        "    status: todo\n"
        "    task_file: docs/forge/tasks/TASK-001.yaml\n",
        encoding="utf-8",
    )
    (forge_dir / "tasks" / "TASK-001.yaml").write_text(
        "id: TASK-001\nstatus: todo\n", encoding="utf-8"
    )
    if forge_mode != "Lightweight":
        (forge_dir / "ARCHITECTURE.md").write_text(
            "# Architecture\n\n## Overview\n\nFixture overview.\n", encoding="utf-8"
        )
        (forge_dir / "TEST_STRATEGY.md").write_text("# Test Strategy\n\nUnit tests.\n", encoding="utf-8")
        (forge_dir / "EVALUATION.md").write_text(
            "# Evaluation\n\n## Definition of Done\n\nTests pass.\n", encoding="utf-8"
        )
        (forge_dir / "MEMORY.md").write_text("# Memory\n\nNo lessons yet.\n", encoding="utf-8")
    if setup_sections is not None:
        body = "# FORGE Setup\n\n"
        for section in setup_sections:
            body += f"## {section}\n\nRecorded.\n\n"
        (forge_dir / "SETUP.md").write_text(body, encoding="utf-8")
    return forge_dir


def _run_generated_docs_validator(repo: Path) -> subprocess.CompletedProcess[str]:
    script = SKILL_ROOT / "assets" / "ci" / "scripts" / "validate-generated-docs.sh"
    return subprocess.run(
        ["bash", str(script)], cwd=repo, text=True, capture_output=True, check=False
    )


def verify_generated_docs_validation() -> None:
    template = (SKILL_ROOT / "assets" / "templates" / "ARCHITECTURE.md").read_text()
    ensure("## Overview" in template, "ARCHITECTURE.md template heading drifted from validator's '## Overview'")
    wrapper_template = (SKILL_ROOT / "assets" / "templates" / "SECURITY_CHECKLISTS.md").read_text()
    ensure(
        "security-checklists/" in wrapper_template,
        "SECURITY_CHECKLISTS.md template no longer routes to the split directory",
    )

    general_asset = (SKILL_ROOT / "assets" / "security-checklists" / "general.md").read_text()

    always_setup = ["Local Hooks", "CI Enforcement", "Team Closeout", "Release Reconciliation"]

    # solo-simple / Lightweight baseline with no checklist surface: valid.
    with tempfile.TemporaryDirectory(prefix="forge-docs-lite-") as temp_dir:
        repo = Path(temp_dir)
        _write_generated_docs_fixture(repo)
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode == 0, f"Lightweight baseline fixture failed:\n{result.stdout}{result.stderr}")

    # Non-Lightweight with valid split checklist layout and baseline SETUP
    # (no Branch Protection section): valid.
    with tempfile.TemporaryDirectory(prefix="forge-docs-split-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = _write_generated_docs_fixture(
            repo, forge_mode="Standard", setup_sections=always_setup
        )
        checklist_dir = forge_dir / "security-checklists"
        checklist_dir.mkdir()
        (checklist_dir / "general.md").write_text(general_asset, encoding="utf-8")
        (forge_dir / "SECURITY_CHECKLISTS.md").write_text(
            (SKILL_ROOT / "assets" / "templates" / "SECURITY_CHECKLISTS.md").read_text(),
            encoding="utf-8",
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode == 0, f"valid split checklist fixture failed:\n{result.stdout}{result.stderr}")

        # Split directory missing general.md: invalid.
        (checklist_dir / "general.md").unlink()
        (checklist_dir / "api.md").write_text("- [ ] item\n", encoding="utf-8")
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode != 0, "split layout missing general.md passed validation")
        ensure("missing the mandatory general.md" in result.stdout, "missing-general.md failure not reported")

        # general.md without checklist items: invalid.
        (checklist_dir / "general.md").write_text("# General\n\nSee elsewhere.\n", encoding="utf-8")
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode != 0, "general.md without checklist items passed validation")
        ensure("no checklist items" in result.stdout, "empty-general.md failure not reported")

    # Index-only compatibility wrapper referencing a missing split dir: invalid.
    with tempfile.TemporaryDirectory(prefix="forge-docs-index-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = _write_generated_docs_fixture(repo, forge_mode="Standard")
        (forge_dir / "SECURITY_CHECKLISTS.md").write_text(
            (SKILL_ROOT / "assets" / "templates" / "SECURITY_CHECKLISTS.md").read_text(),
            encoding="utf-8",
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode != 0, "index-only SECURITY_CHECKLISTS.md wrapper passed validation")
        ensure(
            "does not exist" in result.stdout,
            "index-only wrapper failure not reported",
        )

        # Monolithic wrapper with real items: valid.
        (forge_dir / "SECURITY_CHECKLISTS.md").write_text(
            "# Security Checklists\n\n## General\n\n" + general_asset, encoding="utf-8"
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode == 0, f"valid monolithic checklist fixture failed:\n{result.stdout}{result.stderr}")

    # Clean-main drift check: guard workflow env must mirror extended dev_only_paths.
    with tempfile.TemporaryDirectory(prefix="forge-docs-drift-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = _write_generated_docs_fixture(repo)
        ai = forge_dir / "AI.md"
        ai.write_text(ai.read_text().replace(
            "security_profile: baseline",
            "security_profile: baseline\ndev_only_paths: docs/forge/, CLAUDE.md",
        ))
        wf = repo / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "release-branch-guard.yml").write_text(
            'env:\n  DEV_ONLY_PATHS: "docs/forge"\n'
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode != 0, "guard-env drift (missing CLAUDE.md) passed validation")
        ensure("missing from DEV_ONLY_PATHS" in result.stdout, "drift failure not reported")

        (wf / "release-branch-guard.yml").write_text(
            'env:\n  DEV_ONLY_PATHS: "docs/forge CLAUDE.md"\n'
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode == 0, f"synced guard env failed validation:\n{result.stdout}")

    # repo-fortress: requires a checklist layout and Branch Protection in SETUP.md.
    with tempfile.TemporaryDirectory(prefix="forge-docs-fortress-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = _write_generated_docs_fixture(
            repo,
            security_profile="repo-fortress",
            setup_sections=always_setup,
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode != 0, "repo-fortress with no checklist layout passed validation")
        ensure("no security checklist layout" in result.stdout, "missing-layout failure not reported")

        checklist_dir = forge_dir / "security-checklists"
        checklist_dir.mkdir()
        (checklist_dir / "general.md").write_text(general_asset, encoding="utf-8")
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode != 0, "repo-fortress SETUP.md without Branch Protection passed validation")
        ensure("Branch Protection" in result.stdout, "Branch Protection failure not reported")

        setup = forge_dir / "SETUP.md"
        setup.write_text(
            setup.read_text() + "## Branch Protection\n\nMain protected: yes.\n",
            encoding="utf-8",
        )
        result = _run_generated_docs_validator(repo)
        ensure(result.returncode == 0, f"valid repo-fortress fixture failed:\n{result.stdout}{result.stderr}")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": "forge-test", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "forge-test", "GIT_COMMITTER_EMAIL": "t@t",
    })
    return subprocess.run(["git", "-C", str(repo), *args],
                          text=True, capture_output=True, check=False, env=env)


def verify_dev_only_guards() -> None:
    block_script = SKILL_ROOT / "assets" / "ci" / "scripts" / "block-forge-in-main.sh"
    pre_push = SKILL_ROOT / "assets" / "ci" / "hooks" / "pre-push"

    with tempfile.TemporaryDirectory(prefix="forge-guard-") as temp_dir:
        repo = Path(temp_dir)
        _git(repo, "init", "-q", "-b", "main")
        forge_dir = repo / "docs" / "forge"
        forge_dir.mkdir(parents=True)
        (repo / "app.py").write_text("print('hi')\n")
        (forge_dir / "AI.md").write_text(
            "```FORGE-config\nrelease_branch: main\n"
            "dev_only_paths: docs/forge/, CLAUDE.md\n```\n"
        )
        (repo / "CLAUDE.md").write_text("router\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "base")
        base_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        # Simulate a PR branch that adds governance + surface + app changes.
        _git(repo, "checkout", "-q", "-b", "feature")
        (forge_dir / "TASKS.index.yaml").write_text("tasks: []\n")
        (repo / "CLAUDE.md").write_text("router v2\n")
        (repo / "app.py").write_text("print('v2')\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "feature work")
        feat_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        _git(repo, "update-ref", "refs/remotes/origin/main", base_sha)

        env = os.environ.copy()
        env["GITHUB_BASE_REF"] = "main"
        result = subprocess.run(["bash", str(block_script)], cwd=repo,
                                text=True, capture_output=True, check=False, env=env)
        ensure(result.returncode != 0, "block script allowed dev-only paths into main")
        ensure("CLAUDE.md" in result.stdout and "docs/forge/TASKS.index.yaml" in result.stdout,
               f"block script did not report extended dev-only set:\n{result.stdout}")

        # pre-push: pushing feature to release branch must be rejected.
        push_line = f"refs/heads/feature {feat_sha} refs/heads/main {base_sha}\n"
        result = subprocess.run(["bash", str(pre_push), "origin", "url"], cwd=repo,
                                input=push_line, text=True, capture_output=True, check=False)
        ensure(result.returncode != 0, "pre-push allowed dev-only paths to main")

        # Clean promotion commit (app change only) must pass both guards.
        _git(repo, "checkout", "-q", "main")
        (repo / "app.py").write_text("print('promoted')\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "promo")
        promo_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        result = subprocess.run(["bash", str(block_script)], cwd=repo,
                                text=True, capture_output=True, check=False, env=env)
        ensure(result.returncode == 0, f"block script rejected a clean promotion:\n{result.stdout}")
        push_line = f"refs/heads/main {promo_sha} refs/heads/main {base_sha}\n"
        result = subprocess.run(["bash", str(pre_push), "origin", "url"], cwd=repo,
                                input=push_line, text=True, capture_output=True, check=False)
        ensure(result.returncode == 0, f"pre-push rejected a clean promotion:\n{result.stdout}{result.stderr}")

        # Default set (no config): docs/forge/ blocked, CLAUDE.md allowed.
        (forge_dir / "AI.md").write_text("```FORGE-config\nrelease_branch: main\n```\n")
        _git(repo, "checkout", "-q", "feature")
        result = subprocess.run(["bash", str(block_script)], cwd=repo,
                                text=True, capture_output=True, check=False, env=env)
        ensure(result.returncode != 0, "block script allowed docs/forge with default set")
        ensure("CLAUDE.md" not in result.stdout.replace("docs/forge/AI.md", ""),
               "default set wrongly blocked CLAUDE.md")


def verify_promote_flow() -> None:
    promote = SKILL_ROOT / "assets" / "scripts" / "forge-promote.sh"

    def run_promote(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update({
            "GIT_AUTHOR_NAME": "forge-test", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "forge-test", "GIT_COMMITTER_EMAIL": "t@t",
        })
        return subprocess.run(["bash", str(promote), *args], cwd=repo,
                              text=True, capture_output=True, check=False, env=env)

    with tempfile.TemporaryDirectory(prefix="forge-promote-") as temp_dir:
        repo = Path(temp_dir)
        _git(repo, "init", "-q", "-b", "dev")
        forge_dir = repo / "docs" / "forge"
        forge_dir.mkdir(parents=True)
        (forge_dir / "AI.md").write_text(
            "```FORGE-config\nrelease_branch: main\nintegration_branch: dev\n"
            "dev_only_paths: docs/forge/, CLAUDE.md\n```\n"
        )
        (repo / "CLAUDE.md").write_text("router\n")
        (repo / "app.py").write_text("print('v1')\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "base")

        # First promotion creates the unborn release branch.
        result = run_promote(repo, "-m", "release: v1")
        ensure(result.returncode == 0, f"first promotion (unborn main) failed:\n{result.stdout}{result.stderr}")
        trailer = _git(repo, "log", "-1",
                       "--format=%(trailers:key=Promoted-From,valueonly)", "main").stdout.strip()
        ensure(len(trailer) == 40, f"promotion commit missing Promoted-From trailer: '{trailer}'")
        main_files = _git(repo, "ls-tree", "-r", "--name-only", "main").stdout.split()
        ensure("app.py" in main_files, "promotion dropped app files")
        ensure(not any(f.startswith("docs/forge") or f == "CLAUDE.md" for f in main_files),
               f"promotion leaked dev-only paths: {main_files}")

        # Regression (squash merge-base bug): edit the SAME line twice across
        # two promotions — snapshot promotion must never conflict.
        (repo / "app.py").write_text("print('v2')\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "v2")
        result = run_promote(repo, "-m", "release: v2")
        ensure(result.returncode == 0, f"second promotion failed:\n{result.stdout}{result.stderr}")
        (repo / "app.py").write_text("print('v3')\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "v3")
        result = run_promote(repo, "-m", "release: v3", "--tag", "v3.0.0")
        ensure(result.returncode == 0, f"third promotion (same-line edit) failed:\n{result.stdout}{result.stderr}")
        ensure(_git(repo, "rev-parse", "v3.0.0").returncode == 0, "promotion --tag did not create tag")
        content = _git(repo, "show", "main:app.py").stdout
        ensure("v3" in content, "promotion did not carry latest content")
        ensure(_git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() == "dev",
               "promotion did not return to the starting branch")

        # No-op promotion.
        result = run_promote(repo, "-m", "release: noop")
        ensure(result.returncode == 0 and "Nothing to promote" in result.stdout,
               f"no-op promotion misbehaved:\n{result.stdout}{result.stderr}")

        # Divergence guard: a direct commit on the release branch (no
        # Promoted-From trailer) must refuse without --force.
        _git(repo, "checkout", "-q", "main")
        (repo / "hotfix.txt").write_text("oops\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "direct hotfix on main")
        _git(repo, "checkout", "-q", "dev")
        (repo / "app.py").write_text("print('v4')\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "v4")
        result = run_promote(repo, "-m", "release: v4")
        ensure(result.returncode != 0 and "Promoted-From" in result.stderr,
               f"divergence guard did not refuse direct-commit release HEAD:\n{result.stdout}{result.stderr}")
        result = run_promote(repo, "-m", "release: v4", "--force")
        ensure(result.returncode == 0, f"--force promotion failed:\n{result.stdout}{result.stderr}")


def verify_surface_fallback() -> None:
    generator = SKILL_ROOT / "assets" / "scripts" / "forge_generate_agent_surfaces.py"
    marker = "release branch of a clean-main FORGE repo"
    with tempfile.TemporaryDirectory(prefix="forge-surface-") as temp_dir:
        repo = Path(temp_dir)
        forge_dir = repo / "docs" / "forge"
        forge_dir.mkdir(parents=True)
        (forge_dir / "AI.md").write_text(
            "```FORGE-config\ndev_only_paths: docs/forge/\nintegration_branch: dev\n```\n"
        )
        run([sys.executable, str(generator), str(repo), "--force"], cwd=ROOT)
        text = (repo / "CLAUDE.md").read_text()
        ensure(marker in text, "clean-main fallback missing from generated surface")

        (forge_dir / "AI.md").write_text("```FORGE-config\nrelease_branch: main\n```\n")
        run([sys.executable, str(generator), str(repo), "--force"], cwd=ROOT)
        text = (repo / "CLAUDE.md").read_text()
        ensure(marker not in text, "fallback wrongly emitted without dev_only_paths")

        # Moment map is always present; activation line only with repo-default consent.
        ensure("forge-plan" in text and "forge-ship" in text,
               "generated router lost the moment map")
        activation_marker = "even when the request does not mention FORGE"
        ensure(activation_marker not in text,
               "activation line emitted without activation_mode: repo-default")
        (forge_dir / "AI.md").write_text(
            "```FORGE-config\nactivation_mode: repo-default\ngoverned_paths: src/\n```\n"
        )
        run([sys.executable, str(generator), str(repo), "--force"], cwd=ROOT)
        text = (repo / "CLAUDE.md").read_text()
        ensure(activation_marker in text and "`src/`" in text,
               "activation line missing or unscoped under repo-default")


def verify_docs_staleness() -> None:
    script = SKILL_ROOT / "assets" / "scripts" / "forge_docs_staleness.py"
    with tempfile.TemporaryDirectory(prefix="forge-stale-") as temp_dir:
        root = Path(temp_dir)
        (root / "overview").mkdir()
        (root / "overview" / "stale.md").write_text(
            "---\ntitle: S\nreviewed_at: 2020-01-01\nreview_in_days: 90\n---\nx\n")
        (root / "overview" / "never.md").write_text(
            "---\ntitle: N\nreview_in_days: 90\n---\nx\n")
        (root / "overview" / "fresh.md").write_text(
            "---\ntitle: F\nreviewed_at: 2026-07-30\nreview_in_days: 90\n---\nx\n")
        r = subprocess.run([sys.executable, str(script), str(root), "--today", "2026-07-31"],
                           text=True, capture_output=True, check=False)
        ensure(r.returncode == 1, "staleness did not flag lapsed docs")
        ensure("STALE: overview/stale.md" in r.stdout, "stale doc not reported")
        ensure("NEVER-REVIEWED: overview/never.md" in r.stdout, "never-reviewed doc not reported")
        ensure("fresh.md" not in r.stdout, "fresh doc wrongly reported")


def verify_docs_export() -> None:
    script = SKILL_ROOT / "assets" / "scripts" / "forge_docs_export.py"

    def setup(repo: Path, arch_sensitivity: str, behavior: str) -> Path:
        (repo / "docs" / "forge").mkdir(parents=True)
        (repo / "docs" / "forge" / "AI.md").write_text(
            "```FORGE-config\n"
            "gitlab_wiki_max_sensitivity: internal\n"
            f"sensitivity_excess_behavior: {behavior}\n```\n")
        hb = repo / "handbook"
        (hb / "system").mkdir(parents=True)
        (hb / "README.md").write_text(
            "---\ntitle: HB\nsensitivity: internal\n---\n\n"
            "- [Arch](system/arch.md)\n")
        (hb / "system" / "arch.md").write_text(
            f"---\ntitle: Arch\nsensitivity: {arch_sensitivity}\n---\n\n# Arch\n")
        return hb

    def run(repo, hb, target, out, *extra):
        return subprocess.run(
            [sys.executable, str(script), "--target", target, "--docs-root", str(hb),
             "--out", str(out), "--repo", str(repo), *extra],
            text=True, capture_output=True, check=False)

    # fail-closed: confidential > internal aborts
    with tempfile.TemporaryDirectory(prefix="forge-export-fail-") as td:
        repo = Path(td); hb = setup(repo, "confidential", "fail")
        r = run(repo, hb, "gitlab-wiki", repo / "out")
        ensure(r.returncode == 1 and "exceeds gitlab-wiki" in r.stderr,
               f"export did not fail-close on excess sensitivity:\n{r.stderr}")

    # omit mode: kept README links to omitted arch -> dangling link fails
    with tempfile.TemporaryDirectory(prefix="forge-export-omit-") as td:
        repo = Path(td); hb = setup(repo, "confidential", "omit")
        r = run(repo, hb, "gitlab-wiki", repo / "out")
        ensure(r.returncode == 1 and "links to omitted" in r.stderr,
               f"omit mode did not catch dangling link:\n{r.stderr}")

    # clean gitlab export: home.md + _sidebar.md + slug page + manifest
    with tempfile.TemporaryDirectory(prefix="forge-export-ok-") as td:
        repo = Path(td); hb = setup(repo, "internal", "fail")
        out = repo / "out"
        r = run(repo, hb, "gitlab-wiki", out)
        ensure(r.returncode == 0, f"clean gitlab export failed:\n{r.stderr}")
        ensure((out / "home.md").exists(), "gitlab export missing home.md")
        ensure((out / "_sidebar.md").exists(), "gitlab export missing _sidebar.md")
        ensure((out / "system" / "arch.md").exists(), "gitlab export missing slug page")
        ensure((out / ".forge-export-manifest.json").exists(), "gitlab export missing manifest")
        # reproducible: second export to a fresh dir yields identical hashes
        out2 = repo / "out2"
        run(repo, hb, "gitlab-wiki", out2)
        import json as _j
        h1 = _j.loads((out / ".forge-export-manifest.json").read_text())["outputs"]
        h2 = _j.loads((out2 / ".forge-export-manifest.json").read_text())["outputs"]
        ensure(h1 == h2, "gitlab export is not reproducible")

    # obsidian near-identity + path safety (refuse unmanaged dir)
    with tempfile.TemporaryDirectory(prefix="forge-export-obs-") as td:
        repo = Path(td); hb = setup(repo, "internal", "fail")
        out = repo / "vault"
        r = run(repo, hb, "obsidian", out)
        ensure(r.returncode == 0 and (out / "system" / "arch.md").exists(),
               f"obsidian export failed:\n{r.stderr}")
        unmanaged = repo / "unmanaged"; unmanaged.mkdir()
        (unmanaged / "keep.txt").write_text("x")
        r = run(repo, hb, "obsidian", unmanaged)
        ensure(r.returncode == 1 and "refusing to overwrite" in r.stderr,
               "export overwrote an unmanaged destination")


def verify_release_check() -> None:
    script = SKILL_ROOT / "assets" / "scripts" / "forge_release_check.py"
    with tempfile.TemporaryDirectory(prefix="forge-rel-") as td:
        cl = Path(td) / "CHANGELOG.md"
        cl.write_text("# Changelog\n\n## [1.9.0] - 2026-07-31\n\n- x\n")
        ok = subprocess.run([sys.executable, str(script), "--version", "1.9.0",
                             "--changelog", str(cl)], capture_output=True, text=True)
        ensure(ok.returncode == 0, f"release check failed on a present version:\n{ok.stderr}")
        miss = subprocess.run([sys.executable, str(script), "--version", "2.0.0",
                               "--changelog", str(cl)], capture_output=True, text=True)
        ensure(miss.returncode == 1, "release check passed a missing changelog version")


def verify_gate_loop() -> None:
    """Design TASK-011: execute-task must conduct the gates; helper must agree."""
    execute = (SKILL_ROOT / "execute-task" / "SKILL.md").read_text()
    for needle in ("forge-review", "gates:", "critique: pass|fail",
                   "security: pass|n/a|escalated",
                   "evaluation: pass|handoff-required|fail",
                   "memory: entry|no-relevant-lesson|store-unavailable",
                   "execution-modes.md", "forge_next_gate.py"):
        ensure(needle in execute, f"execute-task lost gate-loop element: {needle}")

    helper = SKILL_ROOT / "assets" / "scripts" / "forge_next_gate.py"
    with tempfile.TemporaryDirectory(prefix="forge-gate-") as temp_dir:
        repo = Path(temp_dir)
        (repo / "docs" / "forge").mkdir(parents=True)
        task = repo / "task.yaml"
        cases = [
            ("id: T1\n", "critique", 0),
            ("id: T1\ngates:\n  critique: pass\n", "security", 0),
            ("id: T1\ngates:\n  critique: pass\n  security: n/a\n  evaluation: pass\n",
             "checkpoint-complete", 0),
            ("id: T1\ngates:\n  critique: fail\n", "blocked:critique", 1),
        ]
        for body, expected, code in cases:
            task.write_text(body.replace("\\n", "\n"))
            result = subprocess.run(
                [sys.executable, str(helper), str(task), "--repo", str(repo)],
                text=True, capture_output=True, check=False)
            ensure(result.stdout.strip() == expected and result.returncode == code,
                   f"next-gate mismatch for {body!r}: got {result.stdout.strip()!r} rc={result.returncode}")
        (repo / "docs" / "forge" / "MEMORY.md").write_text("# Memory\n")
        task.write_text("id: T1\ngates:\n  critique: pass\n  security: n/a\n  evaluation: pass\n")
        result = subprocess.run(
            [sys.executable, str(helper), str(task), "--repo", str(repo)],
            text=True, capture_output=True, check=False)
        ensure(result.stdout.strip() == "memory",
               f"next-gate ignored memory store: {result.stdout.strip()!r}")

        design = repo / "design.yaml"
        design.write_text("id: D1\ntask_type: design\nreview_state: accepted\n")
        result = subprocess.run(
            [sys.executable, str(helper), str(design), "--repo", str(repo)],
            text=True, capture_output=True, check=False)
        ensure("design-task" in result.stdout and result.returncode == 0,
               f"next-gate did not exempt design task: {result.stdout.strip()!r}")


def verify_commit_msg_hook() -> None:
    """Trailers optional (finding-1 fix): a bare Conventional Commit passes;
    AI attribution and bad subjects fail; invalid FORGE-mode fails if present."""
    hook = SKILL_ROOT / "assets" / "ci" / "hooks" / "commit-msg"
    with tempfile.TemporaryDirectory(prefix="forge-cmsg-") as temp_dir:
        msg = Path(temp_dir) / "m"

        def run_hook(text: str) -> int:
            msg.write_text(text)
            return subprocess.run(["bash", str(hook), str(msg)],
                                  capture_output=True, text=True, check=False).returncode

        ensure(run_hook("feat(ledger): add core ledger\n") == 0,
               "commit-msg rejected a valid trailerless Conventional Commit")
        ensure(run_hook("chore(forge): bootstrap governance\n") == 0,
               "commit-msg rejected a trailerless bootstrap commit")
        ensure(run_hook("feat: x\n\nFORGE-task: TASK-001\n") == 0,
               "commit-msg rejected an optional FORGE-task trailer")
        ensure(run_hook("update stuff\n") != 0,
               "commit-msg accepted a non-Conventional subject")
        ensure(run_hook("feat: x\n\nGenerated by Claude\n") != 0,
               "commit-msg accepted AI attribution")
        ensure(run_hook("feat: x\n\nFORGE-mode: Bogus\n") != 0,
               "commit-msg accepted an invalid FORGE-mode value")


def verify_install_flow() -> None:
    with tempfile.TemporaryDirectory(prefix="forge-verify-") as temp_dir:
        env = os.environ.copy()
        env["FORGE_SKILL_TARGET"] = str(Path(temp_dir) / "skills")

        run(["bash", "install.sh", "--force"], cwd=ROOT, env=env)
        run(["bash", "verify-install.sh"], cwd=ROOT, env=env)
        run(["bash", "uninstall.sh"], cwd=ROOT, env=env)


def main() -> int:
    try:
        verify_skill_frontmatter_yaml()
        verify_version_sync()
        verify_skill_names()
        verify_required_files()
        verify_manifests()
        verify_skill_anatomy()
        verify_size_budgets()
        verify_yaml_assets()
        verify_shell_scripts()
        verify_python_scripts()
        verify_context_validation()
        verify_generated_docs_validation()
        verify_dev_only_guards()
        verify_promote_flow()
        verify_surface_fallback()
        verify_gate_loop()
        verify_docs_staleness()
        verify_docs_export()
        verify_release_check()
        verify_commit_msg_hook()
        verify_install_flow()
    except CheckFailure as exc:
        print(f"FORGE verify failed: {exc}", file=sys.stderr)
        return 1

    print("FORGE verify passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
