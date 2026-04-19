#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRATCH_ROOT="$ROOT_DIR/.tmp/manual-tests"

create_repo() {
  local profile="$1"
  local description="$2"
  local prompt="$3"
  local repo_dir="$SCRATCH_ROOT/$profile"

  rm -rf "$repo_dir"
  mkdir -p "$repo_dir"

  git init "$repo_dir" >/dev/null
  git -C "$repo_dir" checkout -b main >/dev/null 2>&1 || true

  cat >"$repo_dir/PROJECT.md" <<EOF
# Manual Test Repo

Profile: $profile
Description: $description
EOF

  cat >"$repo_dir/PROMPT.txt" <<EOF
$prompt
EOF

  cat >"$repo_dir/README.manual-test.md" <<EOF
# FORGE Manual Test

1. Open this repo in your agent.
2. Confirm the \`forge\` skill is installed and available.
3. Paste the prompt from \`PROMPT.txt\`.
4. Review the generated \`docs/forge/\` files.
5. Confirm the output matches the expected profile:

- $profile

Expected focus:
- $description
EOF
}

mkdir -p "$SCRATCH_ROOT"

create_repo \
  "solo-simple" \
  "Minimal solo governance with direct branch work and per-task checkpoints." \
  "Use the forge skill to bootstrap this repo in solo-simple mode for a new project. This is a small internal utility and I am the only operator."

create_repo \
  "solo-governed" \
  "Solo governance with one task branch per governed task and no merge into main without explicit human instruction." \
  "Use the forge skill to bootstrap this repo in solo-governed mode. I want one task branch per governed task, and the agent must never merge into main unless I say so explicitly."

create_repo \
  "team-full" \
  "Full team setup with repo agent surfaces, CI enforcement scaffolding, and team coordination from the start." \
  "Use the forge skill to bootstrap this repo in team-full mode for a SaaS web app. We want repo agent surfaces, CI enforcement scaffolding, and team coordination from the start."

printf 'FORGE manual test repos created under %s\n' "$SCRATCH_ROOT"
printf '  - %s\n' "$SCRATCH_ROOT/solo-simple"
printf '  - %s\n' "$SCRATCH_ROOT/solo-governed"
printf '  - %s\n' "$SCRATCH_ROOT/team-full"
