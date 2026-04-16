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
  target_root="$(resolve_target_root "$agent")"
  target_dir="$target_root/forge"

  if [ ! -e "$target_dir" ]; then
    echo "FORGE: no installed skill pack found at $target_dir"
    continue
  fi

  rm -rf "$target_dir"
  echo "FORGE: removed skill pack from $target_dir"
done
