#!/usr/bin/env bash
# forge-promote.sh — Promote the integration branch to the release branch as a
# single snapshot commit, stripping dev-only governance paths (clean-main model).
#
# Reads from docs/forge/AI.md on the integration branch:
#   release_branch      (default: main)
#   integration_branch  (default: dev)
#   dev_only_paths      (default: docs/forge/; comma-separated, trailing / = prefix)
#
# Usage:
#   forge-promote.sh -m "release: <summary>" [--tag vX.Y.Z] [--dry-run]
#
# Promotion is a tree SNAPSHOT (git read-tree), never a squash merge: squash
# reuses the original merge-base forever, so a second edit to the same line
# conflicts on the next promotion. The release branch must be fully derived
# from the integration branch (never committed to directly) for this model.

set -euo pipefail

config_value() {
  local field="$1" file="docs/forge/AI.md"
  [ -f "$file" ] || return 0
  grep -m1 -E "^[[:space:]]*${field}:" "$file" 2>/dev/null \
    | sed "s/^[[:space:]]*${field}:[[:space:]]*//" | sed 's/[[:space:]]*$//'
}

MESSAGE=""
TAG=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message) MESSAGE="$2"; shift 2 ;;
    --tag)        TAG="$2"; shift 2 ;;
    --dry-run)    DRY_RUN=true; shift ;;
    *) echo "ERROR: Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Working tree is not clean. Commit or stash first." >&2
  exit 1
fi

RELEASE_BRANCH="$(config_value release_branch)"; RELEASE_BRANCH="${RELEASE_BRANCH:-main}"
DEV_BRANCH="$(config_value integration_branch)"; DEV_BRANCH="${DEV_BRANCH:-dev}"
RAW_PATHS="$(config_value dev_only_paths)"; RAW_PATHS="${RAW_PATHS:-docs/forge/}"

STRIP_PATHS=()
while IFS= read -r entry; do
  entry="$(echo "$entry" | sed 's/^[[:space:]]*//; s|/*[[:space:]]*$||')"
  [ -n "$entry" ] && STRIP_PATHS+=("$entry")
done < <(printf '%s\n' "$RAW_PATHS" | tr ',' '\n')

if [[ -z "$MESSAGE" && "$DRY_RUN" == false ]]; then
  echo "ERROR: A commit message is required: -m \"release: <summary>\"" >&2
  exit 1
fi

START_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if $DRY_RUN; then
  echo "DRY RUN: would snapshot '$DEV_BRANCH' onto '$RELEASE_BRANCH', stripping: ${STRIP_PATHS[*]}"
  echo "Files that would land on $RELEASE_BRANCH:"
  git ls-tree -r --name-only "$DEV_BRANCH" | while IFS= read -r f; do
    keep=1
    for p in "${STRIP_PATHS[@]}"; do
      case "$f" in "$p"|"$p"/*) keep=0; break ;; esac
    done
    [ "$keep" = 1 ] && echo "  $f"
  done | head -100
  [[ -n "$TAG" ]] && echo "Would tag: $TAG"
  exit 0
fi

cleanup() {
  git reset --hard HEAD 2>/dev/null || true
  git checkout "$START_BRANCH" 2>/dev/null || true
}
trap cleanup ERR

git checkout "$RELEASE_BRANCH"
# Snapshot: index and worktree become the integration branch's exact tree.
git read-tree -u --reset "$DEV_BRANCH"

for path in "${STRIP_PATHS[@]}"; do
  if git ls-files --cached --error-unmatch "$path" >/dev/null 2>&1 || [[ -e "$path" ]]; then
    git rm -r -f -q --cached "$path" 2>/dev/null || true
    rm -rf "$path"
  fi
done

if git diff --cached --quiet; then
  echo "Nothing to promote: $RELEASE_BRANCH already matches $DEV_BRANCH (excluding stripped paths)."
  git checkout "$START_BRANCH"
  exit 0
fi

git commit -m "$MESSAGE"

if [[ -n "$TAG" ]]; then
  git tag -a "$TAG" -m "$MESSAGE"
fi

echo ""
echo "Promoted $DEV_BRANCH -> $RELEASE_BRANCH as a single commit."
[[ -n "$TAG" ]] && echo "Tagged: $TAG"
echo "Next: git push origin $RELEASE_BRANCH${TAG:+ && git push origin $TAG}"
echo "Returning to $START_BRANCH."
git checkout "$START_BRANCH"
