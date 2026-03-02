#!/bin/bash
# FORGE CI: Verify that required evidence artifacts were modified in the PR.
# Skipped for Lightweight mode. Required for Mid and above.

set -e

BASE_REF="${GITHUB_BASE_REF:-main}"
AI_MD="docs/forge/AI.md"

# Read FORGE mode and ci_enforcement from AI.md
FORGE_MODE=""
CI_ENFORCEMENT=""

if [ -f "$AI_MD" ]; then
  FORGE_MODE=$(grep 'FORGE_mode:' "$AI_MD" | sed 's/.*FORGE_mode: *//' | sed 's/[[:space:]]*$//')
  CI_ENFORCEMENT=$(grep 'ci_enforcement:' "$AI_MD" | sed 's/.*ci_enforcement: *//' | sed 's/[[:space:]]*$//')
fi

# Skip if ci_enforcement is not explicitly enabled
if [ "$CI_ENFORCEMENT" != "enabled" ]; then
  echo "FORGE: ci_enforcement not enabled in AI.md - evidence artifact check skipped."
  exit 0
fi

# Skip for Lightweight mode
if [ "$FORGE_MODE" = "Lightweight" ] || [ -z "$FORGE_MODE" ]; then
  echo "FORGE: Mode is Lightweight - evidence artifact check skipped."
  exit 0
fi

CHANGED_FILES=$(git diff "origin/${BASE_REF}..HEAD" --name-only)
FAILED=0

check_artifact() {
  local artifact="$1"
  if echo "$CHANGED_FILES" | grep -q "^${artifact}$"; then
    echo "FORGE: $artifact updated."
  else
    echo "FORGE: Required evidence artifact not updated: $artifact"
    FAILED=1
  fi
}

check_artifact "docs/forge/EVALUATION.md"
check_artifact "docs/forge/MEMORY.md"

# Strict and Full Discipline also require TASKS.yaml to be updated
if [ "$FORGE_MODE" = "Strict" ] || [ "$FORGE_MODE" = "Full Discipline" ]; then
  check_artifact "docs/forge/TASKS.yaml"
fi

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "FORGE: Evidence artifact validation failed."
  echo "  All required governance documents must be updated in the same PR as the task work."
  exit 1
fi

echo "FORGE: Evidence artifact validation passed."
