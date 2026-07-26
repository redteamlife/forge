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
        SKILL_ROOT / "assets" / "ci" / "scripts" / "verify-team-closeout.sh",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "forge_task_resolver.py",
        SKILL_ROOT / "assets" / "ci" / "scripts" / "validate-generated-docs.sh",
        SKILL_ROOT / "assets" / "templates" / "AGENTS.narrative.md",
        SKILL_ROOT / "assets" / "templates" / "SECURITY.md",
        SKILL_ROOT / "assets" / "templates" / "dependabot.yml",
        SKILL_ROOT / "assets" / "templates" / "CODEOWNERS",
        SKILL_ROOT / "assets" / "templates" / "contracts" / "openapi" / "openapi.yaml",
        SKILL_ROOT / "assets" / "templates" / "contracts" / "protobuf" / "api.proto",
        SKILL_ROOT / "assets" / "templates" / "contracts" / "graphql" / "schema.graphql",
        SKILL_ROOT / "assets" / "agent-surfaces" / ".cursor" / "rules-scoped" / "project-conventions.mdc",
        SKILL_ROOT / "assets" / "agent-surfaces" / ".cursor" / "rules-scoped" / "security.mdc",
        SKILL_ROOT / "assets" / "security-checklists" / "general.md",
        SKILL_ROOT / "bootstrap" / "references" / "scaffolding.md",
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
        verify_install_flow()
    except CheckFailure as exc:
        print(f"FORGE verify failed: {exc}", file=sys.stderr)
        return 1

    print("FORGE verify passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
