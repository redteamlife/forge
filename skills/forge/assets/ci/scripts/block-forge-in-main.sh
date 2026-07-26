#!/bin/bash
# FORGE governance check
# Ensures dev-only governance paths are never merged into the release branch.
# The path set comes from `dev_only_paths` in docs/forge/AI.md (comma-separated;
# entries ending in / are prefixes, others exact files). Default: docs/forge/
# The release branch comes from `release_branch` in the same config; default: main.

set -e

forge_config_value() {
  local file="docs/forge/AI.md" field="$1"
  [ -f "$file" ] || return 0
  grep -m1 -E "^[[:space:]]*${field}:" "$file" 2>/dev/null \
    | sed "s/^[[:space:]]*${field}:[[:space:]]*//" | sed 's/[[:space:]]*$//'
}

forge_dev_only_pattern() {
  local raw pattern="" entry escaped
  raw=$(forge_config_value "dev_only_paths")
  [ -n "$raw" ] || raw="docs/forge/"
  while IFS= read -r entry; do
    entry=$(echo "$entry" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
    [ -n "$entry" ] || continue
    escaped=$(printf '%s' "$entry" | sed 's/[.[\*^$()+?{|]/\\&/g')
    case "$entry" in
      */) pattern="${pattern}^${escaped}|" ;;
      *)  pattern="${pattern}^${escaped}\$|" ;;
    esac
  done < <(printf '%s\n' "$raw" | tr ',' '\n')
  echo "${pattern%|}"
}

RELEASE_BRANCH=$(forge_config_value "release_branch")
RELEASE_BRANCH="${RELEASE_BRANCH:-main}"

BASE_BRANCH="${GITHUB_BASE_REF}"

# Only enforce when the target branch is the release branch.
if [ "$BASE_BRANCH" != "$RELEASE_BRANCH" ]; then
  exit 0
fi

PATTERN=$(forge_dev_only_pattern)

echo "FORGE: Checking that dev-only governance paths are not introduced into $RELEASE_BRANCH..."

CHANGED_FILES=$(git diff --name-only "origin/$BASE_BRANCH...HEAD" | grep -E "$PATTERN" || true)

if [ -n "$CHANGED_FILES" ]; then
  echo ""
  echo "FORGE: Governance violation detected."
  echo ""
  echo "Dev-only governance paths cannot be merged into $RELEASE_BRANCH."
  echo ""
  echo "Detected files:"
  echo "$CHANGED_FILES"
  echo ""
  echo "These paths are development-branch governance artifacts"
  echo "(dev_only_paths in docs/forge/AI.md; default docs/forge/)."
  echo ""
  echo "Resolution:"
  echo "  Remove them from the PR, retarget the merge, or promote via the"
  echo "  clean-main flow (forge-promote) that strips them."
  echo ""
  exit 1
fi

echo "FORGE: Governance check passed."
