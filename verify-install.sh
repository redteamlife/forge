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
    "$TARGET_DIR/execute-task/SKILL.md"
    "$TARGET_DIR/critique/SKILL.md"
    "$TARGET_DIR/security-review/SKILL.md"
    "$TARGET_DIR/evaluation/SKILL.md"
    "$TARGET_DIR/memory/SKILL.md"
    "$TARGET_DIR/assets/templates/AI.md"
    "$TARGET_DIR/assets/templates/TASKS.yaml"
    "$TARGET_DIR/assets/ci/hooks/pre-commit"
    "$TARGET_DIR/assets/ci/hooks/commit-msg"
    "$TARGET_DIR/assets/ci/workflows/forge-governance.yml"
    "$TARGET_DIR/assets/scripts/install-forge-hooks.sh"
    "$TARGET_DIR/assets/scripts/install-forge-hooks.ps1"
  )

  for path in "${REQUIRED[@]}"; do
    if [ ! -e "$path" ]; then
      echo "FORGE: missing installed file: $path" >&2
      exit 1
    fi
  done

  echo "FORGE: install looks good at $TARGET_DIR"
done
