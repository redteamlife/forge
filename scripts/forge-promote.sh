#!/usr/bin/env bash
# forge-promote.sh — Promote dev to main as a single squash commit, stripping
# FORGE governance files so main contains no docs/forge content or history.
#
# Usage:
#   ./scripts/forge-promote.sh -m "release: <summary>" [--tag vX.Y.Z] [--dry-run]
#
# Flow: squash-merge dev into main, remove docs/forge from the staged tree,
# commit, optionally tag. Dev keeps the full detailed history; main reads as
# one clean commit per promotion.

set -euo pipefail

DEV_BRANCH="dev"
MAIN_BRANCH="main"
STRIP_PATHS=("docs/forge")

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

if [[ -z "$MESSAGE" && "$DRY_RUN" == false ]]; then
  echo "ERROR: A commit message is required: -m \"release: <summary>\"" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Working tree is not clean. Commit or stash first." >&2
  exit 1
fi

START_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if $DRY_RUN; then
  echo "DRY RUN: would squash-merge '$DEV_BRANCH' into '$MAIN_BRANCH', stripping: ${STRIP_PATHS[*]}"
  echo "Files that would land on $MAIN_BRANCH:"
  git diff --name-status "$MAIN_BRANCH".."$DEV_BRANCH" -- . \
    | grep -vE "^[A-Z][0-9]*\s+docs/forge/" || true
  [[ -n "$TAG" ]] && echo "Would tag: $TAG"
  exit 0
fi

cleanup() {
  # On failure, abort any half-done squash and return to the starting branch.
  git merge --abort 2>/dev/null || true
  git reset --hard HEAD 2>/dev/null || true
  git checkout "$START_BRANCH" 2>/dev/null || true
}
trap cleanup ERR

git checkout "$MAIN_BRANCH"
git merge --squash "$DEV_BRANCH"

for path in "${STRIP_PATHS[@]}"; do
  if git ls-files --cached --error-unmatch "$path" >/dev/null 2>&1 || [[ -e "$path" ]]; then
    git rm -r -f -q --cached "$path" 2>/dev/null || true
    rm -rf "$path"
  fi
done

if git diff --cached --quiet; then
  echo "Nothing to promote: $MAIN_BRANCH is already up to date with $DEV_BRANCH (excluding stripped paths)."
  git checkout "$START_BRANCH"
  exit 0
fi

git commit -m "$MESSAGE"

if [[ -n "$TAG" ]]; then
  git tag -a "$TAG" -m "$MESSAGE"
fi

echo ""
echo "Promoted $DEV_BRANCH -> $MAIN_BRANCH as a single commit."
[[ -n "$TAG" ]] && echo "Tagged: $TAG"
echo "Next: git push origin $MAIN_BRANCH${TAG:+ && git push origin $TAG}"
echo "Returning to $START_BRANCH."
git checkout "$START_BRANCH"
