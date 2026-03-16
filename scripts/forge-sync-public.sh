#!/usr/bin/env bash
# forge-sync-public.sh — Import an accepted public PR into the private dev repo.
#
# Usage:
#   ./scripts/forge-sync-public.sh --pr <number> [--dry-run]
#   ./scripts/forge-sync-public.sh --merge-commit <sha> [--pr <number>] [--dry-run]

set -euo pipefail

PR_NUMBER=""
MERGE_COMMIT=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pr) PR_NUMBER="$2"; shift 2 ;;
    --merge-commit) MERGE_COMMIT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "ERROR: Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$PR_NUMBER" && -z "$MERGE_COMMIT" ]]; then
  echo "ERROR: Pass --pr <number> or --merge-commit <sha>." >&2
  exit 1
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: '$1' is required but not found in PATH." >&2
    exit 1
  fi
}

yaml_get() {
  local file="$1" key="$2"
  grep -E "^${key}:" "$file" | head -1 | sed "s/^${key}:[[:space:]]*//" | tr -d '"'"'"
}

yaml_nested() {
  local file="$1" parent="$2" key="$3"
  awk "/^${parent}:/{found=1; next} found && /^  ${key}:/{print \$2; exit} found && !/^  /{found=0}" "$file"
}

append_task_stub() {
  local tasks_file="$1" task_id="$2" description="$3"
  if [[ ! -f "$tasks_file" ]]; then
    echo "NOTE: $tasks_file not found. Skipping task stub creation."
    return
  fi
  if grep -q "id: $task_id" "$tasks_file"; then
    echo "NOTE: Task '$task_id' already exists in $tasks_file."
    return
  fi
  printf '\n  - id: %s\n    description: %s\n    status: incomplete\n' "$task_id" "$description" >> "$tasks_file"
  echo "Added intake task stub to $tasks_file"
}

require_cmd git

FORGE_YAML="$(pwd)/forge.yaml"
if [[ ! -f "$FORGE_YAML" ]]; then
  echo "ERROR: forge.yaml not found in the current directory." >&2
  exit 1
fi

VISIBILITY="$(yaml_get "$FORGE_YAML" visibility)"
SRC_DIR="$(yaml_get "$FORGE_YAML" src_dir)"
PUBLIC_REPO="$(yaml_nested "$FORGE_YAML" repos public)"

if [[ "$VISIBILITY" != "open-source" ]]; then
  echo "ERROR: forge-sync-public is only valid for open-source tools." >&2
  exit 1
fi

if ! git remote get-url public >/dev/null 2>&1; then
  echo "ERROR: git remote 'public' is not configured." >&2
  exit 1
fi

if [[ -n "$(git status --short)" ]]; then
  echo "ERROR: Working tree is not clean. Commit or stash changes before importing a public PR." >&2
  exit 1
fi

PUBLIC_URL="$(git remote get-url public)"
PUBLIC_REPO_FULL="$PUBLIC_REPO"
if [[ "$PUBLIC_REPO_FULL" != */* ]]; then
  PUBLIC_REPO_FULL="$(echo "$PUBLIC_URL" | sed -E 's#(git@[^:]+:|https?://[^/]+/)##; s#\.git$##')"
fi

if [[ -n "$PR_NUMBER" ]]; then
  require_cmd gh
  MERGED_AT="$(gh api "repos/$PUBLIC_REPO_FULL/pulls/$PR_NUMBER" --jq '.merged_at')"
  if [[ "$MERGED_AT" == "null" || -z "$MERGED_AT" ]]; then
    echo "ERROR: PR #$PR_NUMBER is not merged in $PUBLIC_REPO_FULL." >&2
    exit 1
  fi
  MERGE_COMMIT="$(gh api "repos/$PUBLIC_REPO_FULL/pulls/$PR_NUMBER" --jq '.merge_commit_sha')"
fi

if [[ -z "$MERGE_COMMIT" ]]; then
  echo "ERROR: Could not resolve merge commit." >&2
  exit 1
fi

TASK_ID="intake-public-commit-${MERGE_COMMIT:0:7}"
TASK_DESC="Review, validate, and integrate accepted public commit ${MERGE_COMMIT:0:7} from $PUBLIC_REPO_FULL into the private dev workflow."
if [[ -n "$PR_NUMBER" ]]; then
  TASK_ID="intake-public-pr-$PR_NUMBER"
  TASK_DESC="Review, validate, and integrate accepted public PR #$PR_NUMBER from $PUBLIC_REPO_FULL into the private dev workflow."
fi

echo "Fetching public remote..."
git fetch public

PARENT_COUNT="$(git show --no-patch --format=%P "$MERGE_COMMIT" | awk '{print NF}')"
PATCH_FILE="$(mktemp)"
trap 'rm -f "$PATCH_FILE"' EXIT

if [[ "$DRY_RUN" == true ]]; then
  echo "[dry-run] Would import $MERGE_COMMIT from $PUBLIC_REPO_FULL into $(git branch --show-current)"
  echo "[dry-run] Would map public repo paths into $SRC_DIR/"
  echo "[dry-run] Would append task stub '$TASK_ID' to docs/forge/TASKS.yaml if missing"
  exit 0
fi

if [[ "$PARENT_COUNT" -gt 1 ]]; then
  git diff "${MERGE_COMMIT}^1" "$MERGE_COMMIT" > "$PATCH_FILE"
else
  git diff "${MERGE_COMMIT}^" "$MERGE_COMMIT" > "$PATCH_FILE"
fi

sed -E -i "s# a/# a/${SRC_DIR%/}/#g; s# b/# b/${SRC_DIR%/}/#g" "$PATCH_FILE"
git apply --index "$PATCH_FILE"

append_task_stub "$(pwd)/docs/forge/TASKS.yaml" "$TASK_ID" "$TASK_DESC"

echo ""
echo "Imported public change into the working tree without committing."
echo "Next steps:"
echo "  1. Review and test the imported change."
echo "  2. Complete the intake task '$TASK_ID' in docs/forge/TASKS.yaml."
echo "  3. Commit it under normal FORGE governance."
