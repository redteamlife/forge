#!/bin/bash
set -euo pipefail

TARGET_ROOT_OVERRIDE="${FORGE_SKILL_TARGET:-}"
declare -a AGENTS=()

resolve_target_root() {
  local agent="$1"
  if [ -n "$TARGET_ROOT_OVERRIDE" ]; then
    printf '%s\n' "$TARGET_ROOT_OVERRIDE"
    return
  fi

  case "$agent" in
    shared) printf '%s\n' "$HOME/.agents/skills" ;;
    claude|claude-code) printf '%s\n' "$HOME/.claude/skills" ;;
    codex) printf '%s\n' "$HOME/.codex/skills" ;;
    cursor) printf '%s\n' "$HOME/.cursor/skills" ;;
    windsurf) printf '%s\n' "$HOME/.windsurf/skills" ;;
    *)
      echo "Unknown agent target: $agent" >&2
      exit 1
      ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --agent)
      shift
      if [ "$#" -eq 0 ]; then
        echo "Missing value for --agent" >&2
        exit 1
      fi
      AGENTS+=("$1")
      ;;
    --agent=*)
      AGENTS+=("${1#--agent=}")
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
  shift
done

if [ "${#AGENTS[@]}" -eq 0 ]; then
  AGENTS=("shared")
fi

for agent in "${AGENTS[@]}"; do
  TARGET_ROOT="$(resolve_target_root "$agent")"
  TARGET_DIR="$TARGET_ROOT/forge"

  if [ ! -e "$TARGET_DIR" ]; then
    echo "FORGE: not installed at $TARGET_DIR" >&2
    exit 1
  fi

  REQUIRED=(
    "$TARGET_DIR/SKILL.md"
    "$TARGET_DIR/bootstrap/SKILL.md"
    "$TARGET_DIR/plan/SKILL.md"
    "$TARGET_DIR/build/SKILL.md"
    "$TARGET_DIR/review/SKILL.md"
    "$TARGET_DIR/ship/SKILL.md"
    "$TARGET_DIR/execute-task/SKILL.md"
    "$TARGET_DIR/critique/SKILL.md"
    "$TARGET_DIR/security-review/SKILL.md"
    "$TARGET_DIR/evaluation/SKILL.md"
    "$TARGET_DIR/memory/SKILL.md"
    "$TARGET_DIR/cross-project/SKILL.md"
    "$TARGET_DIR/references/cross-project.md"
    "$TARGET_DIR/references/lifecycle-map.md"
    "$TARGET_DIR/references/skill-anatomy.md"
    "$TARGET_DIR/assets/templates/AI.md"
    "$TARGET_DIR/assets/templates/CONTEXT.md"
    "$TARGET_DIR/assets/templates/MEMORY.index.yaml"
    "$TARGET_DIR/assets/templates/SKILL-ANATOMY.md"
    "$TARGET_DIR/assets/templates/TASKS.yaml"
    "$TARGET_DIR/assets/templates/TASKS.index.yaml"
    "$TARGET_DIR/assets/templates/tasks/TASK-001.yaml"
    "$TARGET_DIR/assets/templates/team/claiming.md"
    "$TARGET_DIR/assets/templates/team/release.md"
    "$TARGET_DIR/assets/templates/team/trackers.md"
    "$TARGET_DIR/assets/templates/team/contracts.md"
    "$TARGET_DIR/assets/templates/memory/decisions.md"
    "$TARGET_DIR/assets/templates/memory/failures.md"
    "$TARGET_DIR/assets/templates/memory/conventions.md"
    "$TARGET_DIR/assets/templates/memory/project-facts.md"
    "$TARGET_DIR/assets/cross-project/templates/COORDINATION.yaml"
    "$TARGET_DIR/assets/cross-project/templates/decisions/XPD-0001-template.md"
    "$TARGET_DIR/assets/cross-project/templates/sister-repo-pointer.md"
    "$TARGET_DIR/assets/ci/hooks/pre-commit"
    "$TARGET_DIR/assets/ci/hooks/commit-msg"
    "$TARGET_DIR/assets/ci/docs/commit-format.md"
    "$TARGET_DIR/assets/ci/docs/validators.md"
    "$TARGET_DIR/assets/ci/docs/governance-patterns.md"
    "$TARGET_DIR/assets/ci/workflows/forge-governance.yml"
    "$TARGET_DIR/assets/ci/workflows/forge-quality.yml"
    "$TARGET_DIR/assets/ci/workflows/security/scorecard.yml"
    "$TARGET_DIR/assets/ci/workflows/security/codeql.yml"
    "$TARGET_DIR/assets/ci/workflows/security/semgrep.yml"
    "$TARGET_DIR/assets/ci/workflows/security/dependency-review.yml"
    "$TARGET_DIR/assets/ci/workflows/security/osv-scanner.yml"
    "$TARGET_DIR/assets/ci/workflows/security/sbom.yml"
    "$TARGET_DIR/assets/ci/workflows/security/zap-baseline.yml"
    "$TARGET_DIR/assets/ci/gitlab/security.gitlab-ci.yml"
    "$TARGET_DIR/assets/ci/scripts/forge_task_resolver.py"
    "$TARGET_DIR/assets/ci/scripts/validate-generated-docs.sh"
    "$TARGET_DIR/assets/templates/AGENTS.narrative.md"
    "$TARGET_DIR/assets/templates/SECURITY.md"
    "$TARGET_DIR/assets/templates/dependabot.yml"
    "$TARGET_DIR/assets/templates/CODEOWNERS"
    "$TARGET_DIR/assets/templates/contracts/openapi/openapi.yaml"
    "$TARGET_DIR/assets/templates/contracts/protobuf/api.proto"
    "$TARGET_DIR/assets/templates/contracts/graphql/schema.graphql"
    "$TARGET_DIR/assets/agent-surfaces/.cursor/rules-scoped/project-conventions.mdc"
    "$TARGET_DIR/assets/security-checklists/general.md"
    "$TARGET_DIR/bootstrap/references/scaffolding.md"
    "$TARGET_DIR/assets/scripts/install-forge-hooks.sh"
    "$TARGET_DIR/assets/scripts/install-forge-hooks.ps1"
    "$TARGET_DIR/assets/scripts/forge_context_budget.py"
    "$TARGET_DIR/assets/scripts/forge_generate_agent_surfaces.py"
    "$TARGET_DIR/assets/scripts/forge_scaffold_contract.py"
    "$TARGET_DIR/assets/scripts/forge_migrate_context.py"
    "$TARGET_DIR/assets/scripts/forge_validate_context.py"
  )

  for path in "${REQUIRED[@]}"; do
    if [ ! -e "$path" ]; then
      echo "FORGE: missing installed file: $path" >&2
      exit 1
    fi
  done

  echo "FORGE: install looks good at $TARGET_DIR"
done
