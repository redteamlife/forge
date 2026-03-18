#!/usr/bin/env bash
# forge-publish.sh — Publish a FORGE-governed tool to its public repository.
#
# Usage:
#   ./scripts/forge-publish.sh [--tag <version>] [--dry-run]
#
# Options:
#   --tag <version>   Release tag (e.g. v1.0.0). Required for closed-source.
#                     Prompted interactively if not provided.
#   --dry-run         Print what would happen without making changes.
#
# Reads forge.yaml from the project root. Requires git.
# Closed-source releases require the gh CLI.
# Open-source releases require a configured 'public' remote.

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

TAG=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag)     TAG="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) echo "ERROR: Unknown argument: $1" >&2; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

print_step() { echo ""; echo "==> $1"; }
dry()         { echo "[dry-run] $*"; }

require_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo "ERROR: '$1' is required but not found in PATH." >&2
    exit 1
  fi
}

release_dir_ignore_present() {
  local gitignore="$1" ignore_entry="$2"
  [[ -f "$gitignore" ]] && {
    grep -qxF "$ignore_entry" "$gitignore" || grep -qxF "/$ignore_entry" "$gitignore"
  }
}

# ---------------------------------------------------------------------------
# Minimal forge.yaml parser
# Extracts top-level scalar values and list items.
# ---------------------------------------------------------------------------

yaml_get() {
  local file="$1" key="$2"
  grep -E "^${key}:" "$file" | head -1 | sed "s/^${key}:[[:space:]]*//" | tr -d '"'"'"
}

yaml_list() {
  local file="$1" key="$2"
  awk "/^${key}:/{found=1; next} found && /^  - /{print \$2} found && !/^  /{found=0}" "$file"
}

yaml_nested() {
  local file="$1" parent="$2" key="$3"
  awk "/^${parent}:/{found=1; next} found && /^  ${key}:/{print \$2; exit} found && !/^  /{found=0}" "$file"
}

# ---------------------------------------------------------------------------
# Validate forge.yaml
# ---------------------------------------------------------------------------

FORGE_YAML="$(pwd)/forge.yaml"

if [[ ! -f "$FORGE_YAML" ]]; then
  echo "ERROR: forge.yaml not found in the current directory." >&2
  echo "       Run this script from the project root." >&2
  exit 1
fi

print_step "Reading forge.yaml"

PROJECT="$(yaml_get "$FORGE_YAML" project)"
VISIBILITY="$(yaml_get "$FORGE_YAML" visibility)"
PUBLISH_STRATEGY="$(yaml_get "$FORGE_YAML" publish_strategy)"
SRC_DIR="$(yaml_get "$FORGE_YAML" src_dir)"
RELEASE_DIR="$(yaml_get "$FORGE_YAML" release_dir)"
PUBLIC_REPO="$(yaml_nested "$FORGE_YAML" repos public)"

if [[ -z "$PROJECT" || -z "$VISIBILITY" || -z "$SRC_DIR" || -z "$RELEASE_DIR" || -z "$PUBLIC_REPO" ]]; then
  echo "ERROR: forge.yaml is missing required fields (project, visibility, src_dir, release_dir, repos.public)." >&2
  exit 1
fi

echo "  project    : $PROJECT"
echo "  visibility : $VISIBILITY"
if [[ "$VISIBILITY" == "open-source" ]]; then
  echo "  strategy   : ${PUBLISH_STRATEGY:-snapshot-force-push}"
fi
echo "  src_dir    : $SRC_DIR"
echo "  release_dir: $RELEASE_DIR"
echo "  public repo: $PUBLIC_REPO"

# ---------------------------------------------------------------------------
# Route by visibility
# ---------------------------------------------------------------------------

require_cmd git
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

if [[ "$VISIBILITY" == "open-source" ]]; then

  # -------------------------------------------------------------------------
  # Open source: copy src -> release, then push ONLY release content to
  # public/main using a temporary isolated git repository. This ensures no
  # dev-repo files (FORGE docs, architecture, etc.) are ever pushed to the
  # public repo.
  # -------------------------------------------------------------------------

  print_step "Open source publish: copying $SRC_DIR -> $RELEASE_DIR"

  if [[ ! -d "$SRC_DIR" ]]; then
    echo "ERROR: src_dir '$SRC_DIR' does not exist." >&2
    exit 1
  fi

  if ! git remote get-url public &>/dev/null; then
    echo "ERROR: git remote 'public' is not configured." >&2
    echo "       Add it with: git remote add public https://github.com/<org>/$PUBLIC_REPO.git" >&2
    exit 1
  fi

  REMOTE_URL="$(git remote get-url public)"
  GITIGNORE="$REPO_ROOT/.gitignore"
  RELEASE_IGNORE_ENTRY="${RELEASE_DIR%/}/"
  PUBLISH_STRATEGY="${PUBLISH_STRATEGY:-snapshot-force-push}"
  PUBLIC_SYNC_REQUIRED="$(yaml_nested "$FORGE_YAML" public_sync required)"
  LAST_IMPORTED_PUBLIC_COMMIT="$(yaml_nested "$FORGE_YAML" public_sync last_imported_public_commit | tr -d '"')"

  if [[ "$PUBLISH_STRATEGY" != "snapshot-force-push" && "$PUBLISH_STRATEGY" != "preserve-history" ]]; then
    echo "ERROR: Unknown publish_strategy '$PUBLISH_STRATEGY'. Must be 'snapshot-force-push' or 'preserve-history'." >&2
    exit 1
  fi

  if [[ "$PUBLISH_STRATEGY" == "preserve-history" ]] && git ls-remote --exit-code public refs/heads/main >/dev/null 2>&1; then
    git fetch public main:refs/remotes/public/main >/dev/null 2>&1
    PUBLIC_HEAD="$(git rev-parse public/main)"
    if [[ "${PUBLIC_SYNC_REQUIRED:-false}" == "true" && "$LAST_IMPORTED_PUBLIC_COMMIT" != "$PUBLIC_HEAD" ]]; then
      RANGE_SPEC="public/main"
      if [[ -n "$LAST_IMPORTED_PUBLIC_COMMIT" ]]; then
        if ! git cat-file -e "${LAST_IMPORTED_PUBLIC_COMMIT}^{commit}" 2>/dev/null || ! git merge-base --is-ancestor "$LAST_IMPORTED_PUBLIC_COMMIT" public/main; then
          echo "ERROR: last_imported_public_commit '$LAST_IMPORTED_PUBLIC_COMMIT' is not present in public/main history." >&2
          echo "       Run forge-sync-public to re-establish sync state before publishing." >&2
          exit 1
        fi
        RANGE_SPEC="$LAST_IMPORTED_PUBLIC_COMMIT..public/main"
      fi

      NON_RELEASE_COUNT="$(git log --format=%s "$RANGE_SPEC" | grep -Fvx "release: publish $PROJECT" | wc -l | tr -d ' ')"
      if [[ "$NON_RELEASE_COUNT" != "0" ]]; then
        echo "ERROR: public/main contains merged public changes that have not been imported into private dev." >&2
        echo "       Run forge-sync-public before publishing again." >&2
        exit 1
      fi
    fi
  fi

  if [[ "$DRY_RUN" == true ]]; then
    if ! release_dir_ignore_present "$GITIGNORE" "$RELEASE_IGNORE_ENTRY"; then
      echo "[dry-run] WARNING: '$RELEASE_IGNORE_ENTRY' is not in .gitignore. A non-dry-run publish will add it automatically."
    fi
    dry "rm -rf $RELEASE_DIR && mkdir -p $RELEASE_DIR"
    dry "cp -r $SRC_DIR/. $RELEASE_DIR/"
    dry "TMPDIR=\$(mktemp -d)"
    if [[ "$PUBLISH_STRATEGY" == "snapshot-force-push" ]]; then
      dry "cp -r $RELEASE_DIR/. \$TMPDIR/"
      dry "cd \$TMPDIR && git init && git add . && git commit -m 'release: publish $PROJECT'"
      dry "git remote add public $REMOTE_URL"
      dry "git push public HEAD:main --force"
    else
      dry "cd \$TMPDIR && git init && git remote add public $REMOTE_URL"
      dry "git fetch public main && git checkout -B main FETCH_HEAD"
      dry "rm -rf \$TMPDIR/* and copy $RELEASE_DIR into the working tree"
      dry "git add -A && git commit -m 'release: publish $PROJECT'"
      dry "git push public main"
    fi
    dry "rm -rf \$TMPDIR"
    echo ""
    echo "[dry-run] Open source publish complete — no changes made."
    exit 0
  fi

  # Stash uncommitted dev work so src/ is clean
  DIRTY=false
  if ! git diff --quiet || ! git diff --staged --quiet; then
    DIRTY=true
    git stash
  fi

  if ! release_dir_ignore_present "$GITIGNORE" "$RELEASE_IGNORE_ENTRY"; then
    echo "WARNING: '$RELEASE_IGNORE_ENTRY' is not in .gitignore. Adding it now to prevent release artifacts from being committed."
    if [[ -f "$GITIGNORE" && -s "$GITIGNORE" ]]; then
      LAST_CHAR="$(tail -c 1 "$GITIGNORE" 2>/dev/null || true)"
      if [[ "$LAST_CHAR" != "" && "$LAST_CHAR" != $'\n' ]]; then
        printf '\n' >> "$GITIGNORE"
      fi
    fi
    printf '%s\n' "$RELEASE_IGNORE_ENTRY" >> "$GITIGNORE"
  fi

  # Populate release staging dir
  rm -rf "$RELEASE_DIR"
  mkdir -p "$RELEASE_DIR"
  cp -r "$SRC_DIR/." "$RELEASE_DIR/"
  RELEASE_DIR_ABS="$REPO_ROOT/${RELEASE_DIR%/}"

  TMPDIR_RELEASE="$(mktemp -d)"
  trap 'rm -rf "$TMPDIR_RELEASE"' EXIT

  FORGE_MODE="$(grep -E '^FORGE_mode:' "$(pwd)/docs/forge/AI.md" 2>/dev/null | head -1 | awk '{print $2}' || echo 'Mid')"

  pushd "$TMPDIR_RELEASE" > /dev/null
  git init
  git remote add public "$REMOTE_URL"

  if [[ "$PUBLISH_STRATEGY" == "snapshot-force-push" ]]; then
    cp -r "$RELEASE_DIR_ABS/." "$TMPDIR_RELEASE/"
    git symbolic-ref HEAD refs/heads/main
  else
    if git ls-remote --exit-code public refs/heads/main >/dev/null 2>&1; then
      git fetch public main
      git checkout -B main FETCH_HEAD
    else
      git symbolic-ref HEAD refs/heads/main
    fi

    find "$TMPDIR_RELEASE" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
    cp -r "$RELEASE_DIR_ABS/." "$TMPDIR_RELEASE/"
  fi

  git add -A
  if git diff --cached --quiet; then
    popd > /dev/null
    if [[ "$DIRTY" == true ]]; then
      git stash pop || true
    fi
    echo ""
    echo "No publishable changes detected for $PUBLIC_REPO."
    exit 0
  fi

  git commit -m "release: publish $PROJECT

FORGE-mode: $FORGE_MODE
FORGE-task: RELEASE
FORGE-gate: pass"

  print_step "Pushing to public/$PUBLIC_REPO main"
  if [[ "$PUBLISH_STRATEGY" == "snapshot-force-push" ]]; then
    git push public main --force
  else
    git push public main
  fi
  popd > /dev/null

  # Restore stashed dev work
  if [[ "$DIRTY" == true ]]; then
    git stash pop || true
  fi

  echo ""
  echo "Published $PROJECT to public repo: $PUBLIC_REPO"

elif [[ "$VISIBILITY" == "closed-source" ]]; then

  # -------------------------------------------------------------------------
  # Closed source: upload build_output paths as GitHub Release assets.
  # No source or dev files are pushed anywhere.
  # -------------------------------------------------------------------------

  require_cmd gh

  mapfile -t BUILD_OUTPUT < <(yaml_list "$FORGE_YAML" build_output)

  if [[ ${#BUILD_OUTPUT[@]} -eq 0 ]]; then
    echo "ERROR: No build_output entries found in forge.yaml." >&2
    exit 1
  fi

  print_step "Verifying build outputs"
  for bin in "${BUILD_OUTPUT[@]}"; do
    if [[ ! -f "$bin" ]]; then
      echo "ERROR: Binary not found: $bin" >&2
      echo "       Compile your project before publishing." >&2
      exit 1
    fi
    echo "  Found: $bin"
  done

  if [[ -z "$TAG" ]]; then
    read -rp "Release tag (e.g. v1.0.0): " TAG
  fi

  if [[ -z "$TAG" ]]; then
    echo "ERROR: Release tag is required for closed-source publish." >&2
    exit 1
  fi

  REPO_FULL="$(gh repo view "$PUBLIC_REPO" --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "$PUBLIC_REPO")"

  if [[ "$DRY_RUN" == true ]]; then
    dry "gh release create $TAG --repo $REPO_FULL --title '$PROJECT $TAG' --notes 'Release $TAG'"
    for bin in "${BUILD_OUTPUT[@]}"; do
      dry "gh release upload $TAG $bin --repo $REPO_FULL"
    done
    echo ""
    echo "[dry-run] Closed source publish complete — no changes made."
    exit 0
  fi

  print_step "Creating GitHub Release $TAG on $PUBLIC_REPO"

  gh release create "$TAG" \
    --repo "$REPO_FULL" \
    --title "$PROJECT $TAG" \
    --notes "Release $TAG"

  print_step "Uploading release assets"
  for bin in "${BUILD_OUTPUT[@]}"; do
    gh release upload "$TAG" "$bin" --repo "$REPO_FULL"
    echo "  Uploaded: $bin"
  done

  echo ""
  echo "Published $PROJECT $TAG to GitHub Releases on $PUBLIC_REPO"

else
  echo "ERROR: Unknown visibility '$VISIBILITY' in forge.yaml. Must be 'open-source' or 'closed-source'." >&2
  exit 1
fi
