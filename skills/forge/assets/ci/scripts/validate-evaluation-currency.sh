#!/bin/bash
# FORGE CI: Verify that EVALUATION.md is updated in the SAME commit as any
# local task-ledger state transition, not just somewhere in the PR.
#
# This complements validate-evidence-artifacts.sh: that script checks the
# whole PR; this one checks each commit individually so an agent cannot
# transition a task to complete in one commit and append evidence in
# another, unrelated commit.
#
# Skipped for Lightweight mode. Skipped when ci_enforcement is not enabled.

set -e

BASE_REF="${GITHUB_BASE_REF:-main}"
AI_MD="docs/forge/AI.md"

FORGE_MODE=""
CI_ENFORCEMENT=""

if [ -f "$AI_MD" ]; then
  FORGE_MODE=$(grep -m1 -E '^[[:space:]]*FORGE_mode:' "$AI_MD" | sed 's/^[[:space:]]*FORGE_mode: *//' | sed 's/[[:space:]]*$//')
  CI_ENFORCEMENT=$(grep -m1 -E '^[[:space:]]*ci_enforcement:' "$AI_MD" | sed 's/^[[:space:]]*ci_enforcement: *//' | sed 's/[[:space:]]*$//')
fi

if [ "$CI_ENFORCEMENT" != "enabled" ]; then
  exit 0
fi

if [ "$FORGE_MODE" = "Lightweight" ] || [ -z "$FORGE_MODE" ]; then
  exit 0
fi

FAILED=0
COMMITS=$(git rev-list "origin/${BASE_REF}..HEAD")

for commit in $COMMITS; do
  TASK_FILES=$(git show --name-only --format= "$commit" | grep -E '^docs/forge/(TASKS.yaml|TASKS.index.yaml|tasks/.*[.]ya?ml)$' || true)
  if [ -z "$TASK_FILES" ]; then
    continue
  fi

  # Did this commit move a task into a terminal-ish state? Look for added lines
  # that set status: implemented|integrated|complete in local task files.
  STATE_TRANSITION=$(git show "$commit" -- $TASK_FILES | grep -E '^\+[[:space:]]*status: (implemented|integrated|complete)' || true)

  if [ -z "$STATE_TRANSITION" ]; then
    continue
  fi

  if ! git show --name-only --format= "$commit" | grep -q '^docs/forge/EVALUATION.md$'; then
    SHORT=$(echo "$commit" | cut -c1-8)
    echo "FORGE: Commit $SHORT transitions local task state but does not update docs/forge/EVALUATION.md in the same commit."
    FAILED=1
  fi
done

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "FORGE: Evaluation currency check failed."
  echo "  Task-state transitions and their evidence must be recorded in the same commit, not split across commits."
  exit 1
fi

exit 0
