#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/skills/forge"
FORCE=0
MODE="${FORGE_INSTALL_MODE:-copy}"
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

install_one() {
  local agent="$1"
  local target_root="$2"
  local target_dir="$target_root/forge"

  if [ -e "$target_dir" ] && [ "$FORCE" -ne 1 ]; then
    echo "FORGE: skill already installed at $target_dir"
    echo "  Re-run with --force to replace it."
    return
  fi

  mkdir -p "$target_root"
  rm -rf "$target_dir"

  if [ "$MODE" = "link" ]; then
    ln -s "$SOURCE_DIR" "$target_dir"
    echo "FORGE: linked skill pack to $target_dir"
  else
    cp -R "$SOURCE_DIR" "$target_dir"
    echo "FORGE: installed skill pack to $target_dir"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --force|-f) FORCE=1 ;;
    --copy) MODE="copy" ;;
    --link) MODE="link" ;;
    --global-shared) AGENTS+=("shared") ;;
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
    --help|-h)
      cat <<'EOF'
Install the FORGE skill pack into the local Agent Skills directory.

Usage:
  bash install.sh
  bash install.sh --force
  bash install.sh --agent claude --link
  bash install.sh --agent codex --agent cursor --copy

Environment:
  FORGE_SKILL_TARGET   Override the skill install root for a single-target install
  FORGE_INSTALL_MODE   Default install mode: copy or link
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
  shift
done

if [ ! -d "$SOURCE_DIR" ]; then
  echo "FORGE: skill source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

if [ "$MODE" != "copy" ] && [ "$MODE" != "link" ]; then
  echo "FORGE: install mode must be 'copy' or 'link'" >&2
  exit 1
fi

if [ "${#AGENTS[@]}" -eq 0 ]; then
  AGENTS=("shared")
fi

for agent in "${AGENTS[@]}"; do
  target_root="$(resolve_target_root "$agent")"
  install_one "$agent" "$target_root"
done

echo ""
echo "Next steps:"
echo "  1. Open your project in a skill-aware agent."
echo "  2. Ask it to use the 'forge' skill."
echo "  3. If the repo has no FORGE docs yet, start with:"
echo "     Use the forge skill and bootstrap docs/forge for this project."
