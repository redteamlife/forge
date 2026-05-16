#!/bin/bash
# FORGE CI: Verify that every task referenced via FORGE-task trailer
# has the expected status in the configured local task ledger.

set -e

BASE_REF="${GITHUB_BASE_REF:-main}"
AI_MD="docs/forge/AI.md"
TASKS_FILE="docs/forge/TASKS.yaml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_RESOLVER="$SCRIPT_DIR/forge_task_resolver.py"

INTEGRATION_BRANCH="develop"
RELEASE_BRANCH="main"
TASK_SOURCE="local"

if [ -f "$AI_MD" ]; then
  INTEGRATION_BRANCH=$(grep -m1 -E '^[[:space:]]*integration_branch:' "$AI_MD" | sed 's/^[[:space:]]*integration_branch: *//' | sed 's/[[:space:]]*$//' || true)
  RELEASE_BRANCH=$(grep -m1 -E '^[[:space:]]*release_branch:' "$AI_MD" | sed 's/^[[:space:]]*release_branch: *//' | sed 's/[[:space:]]*$//' || true)
  TASK_SOURCE=$(grep -m1 -E '^[[:space:]]*task_source:' "$AI_MD" | sed 's/^[[:space:]]*task_source: *//' | sed 's/[[:space:]]*$//' || true)
  [ -z "$INTEGRATION_BRANCH" ] && INTEGRATION_BRANCH="develop"
  [ -z "$RELEASE_BRANCH" ] && RELEASE_BRANCH="main"
  [ -z "$TASK_SOURCE" ] && TASK_SOURCE="local"
fi

if [ "$TASK_SOURCE" != "local" ]; then
  echo "FORGE: task_source is $TASK_SOURCE - local task state validation skipped."
  exit 0
fi

if [ ! -f "$TASK_RESOLVER" ]; then
  echo "FORGE: task resolver not found: $TASK_RESOLVER"
  exit 1
fi

if [ ! -f "$TASKS_FILE" ] && [ ! -f "docs/forge/TASKS.index.yaml" ]; then
  echo "FORGE: no local task ledger found - skipping task state validation."
  exit 0
fi

COMMIT_HASHES=$(git log "origin/${BASE_REF}..HEAD" --format="%H")

if [ -z "$COMMIT_HASHES" ]; then
  echo "FORGE: No commits to validate."
  exit 0
fi

FAILED=0

while IFS= read -r hash; do
  SUBJECT=$(git log --format="%s" -1 "$hash")
  FULL_MSG=$(git log --format="%B" -1 "$hash")

  # Skip merge commits
  if echo "$SUBJECT" | grep -qE "^(Merge |Revert \")"; then
    continue
  fi

  # Extract FORGE-task trailer
  TASK_ID=$(echo "$FULL_MSG" | grep "^FORGE-task:" | sed 's/^FORGE-task: *//' | sed 's/[[:space:]]*$//')

  if [ -z "$TASK_ID" ]; then
    continue
  fi

  LEDGER=$(python3 "$TASK_RESOLVER" --task "$TASK_ID" --ledger 2>/dev/null || true)
  STATUS=$(python3 "$TASK_RESOLVER" --task "$TASK_ID" --field status 2>/dev/null || true)
  [ -z "$STATUS" ] && STATUS="not_found"
  [ -z "$LEDGER" ] && LEDGER="local task ledger"

  if [ "$BASE_REF" = "$RELEASE_BRANCH" ]; then
    if [ "$STATUS" = "integrated" ] || [ "$STATUS" = "complete" ]; then
      echo "FORGE: Task '$TASK_ID' is ready for release branch merge (status: $STATUS)."
    elif [ "$STATUS" = "not_found" ]; then
      echo "FORGE: Task '$TASK_ID' not found in $LEDGER."
      FAILED=1
    else
      echo "FORGE: Task '$TASK_ID' is not ready for release branch merge (status: $STATUS)."
      FAILED=1
    fi
  elif [ "$BASE_REF" = "$INTEGRATION_BRANCH" ]; then
    if [ "$STATUS" = "implemented" ] || [ "$STATUS" = "integrated" ] || [ "$STATUS" = "complete" ]; then
      echo "FORGE: Task '$TASK_ID' is ready for integration branch merge (status: $STATUS)."
    elif [ "$STATUS" = "not_found" ]; then
      echo "FORGE: Task '$TASK_ID' not found in $LEDGER."
      FAILED=1
    else
      echo "FORGE: Task '$TASK_ID' is not ready for integration branch merge (status: $STATUS)."
      FAILED=1
    fi
  elif [ "$STATUS" = "complete" ]; then
    echo "FORGE: Task '$TASK_ID' is complete."
  elif [ "$STATUS" = "not_found" ]; then
    echo "FORGE: Task '$TASK_ID' not found in $LEDGER."
    FAILED=1
  else
    echo "FORGE: Task '$TASK_ID' is not complete (status: $STATUS)."
    FAILED=1
  fi
done <<< "$COMMIT_HASHES"

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "FORGE: Task state validation failed. FORGE-task trailers must match the configured local task ledger."
  exit 1
fi

echo "FORGE: Task state validation passed."
