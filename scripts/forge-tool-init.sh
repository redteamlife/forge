#!/usr/bin/env bash
# forge-tool-init.sh — Scaffold a new FORGE-governed tool development repository.
#
# Usage:
#   ./scripts/forge-tool-init.sh [ToolName]
#
# If ToolName is not provided as an argument, the script will prompt for it.
# Requires: git. Optional: gh (GitHub CLI) for repo creation.

set -euo pipefail

FORGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FORGE_TEMPLATES_DIR="$FORGE_ROOT/templates"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

print_step() { echo ""; echo "==> $1"; }
prompt()      { read -rp "$1: " "$2"; }
to_lower()    { echo "$1" | tr '[:upper:]' '[:lower:]'; }

require_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo "ERROR: '$1' is required but not found in PATH." >&2
    exit 1
  fi
}

# ---------------------------------------------------------------------------
# Collect inputs
# ---------------------------------------------------------------------------

TOOL_NAME="${1:-}"

if [[ -z "$TOOL_NAME" ]]; then
  prompt "Tool name (no spaces)" TOOL_NAME
fi

if [[ -z "$TOOL_NAME" ]]; then
  echo "ERROR: Tool name is required." >&2
  exit 1
fi

echo ""
echo "Select tool type:"
echo "  1) web-tool"
echo "  2) cli-tool"
echo "  3) script"
prompt "Choice [1-3]" TYPE_CHOICE

case "$TYPE_CHOICE" in
  1) TOOL_TYPE="web-tool" ;;
  2) TOOL_TYPE="cli-tool" ;;
  3) TOOL_TYPE="script" ;;
  *) echo "ERROR: Invalid choice." >&2; exit 1 ;;
esac

echo ""
echo "Select tool visibility:"
echo "  1) Open source  (source code published to public repo)"
echo "  2) Closed source (compiled binaries published as GitHub Release assets)"
prompt "Choice [1-2]" VIS_CHOICE

case "$VIS_CHOICE" in
  1) VISIBILITY="open-source" ;;
  2) VISIBILITY="closed-source" ;;
  *) echo "ERROR: Invalid choice." >&2; exit 1 ;;
esac

DEV_REPO="${TOOL_NAME}-dev"
PUBLIC_REPO="${TOOL_NAME}"
TARGET_DIR="$(pwd)/${DEV_REPO}"

echo ""
echo "Summary:"
echo "  Tool name  : $TOOL_NAME"
echo "  Type       : $TOOL_TYPE"
echo "  Visibility : $VISIBILITY"
echo "  Dev repo   : $DEV_REPO  (local directory: $TARGET_DIR)"
echo "  Public repo: $PUBLIC_REPO"
echo ""

# Guard against overwriting an existing directory
if [[ -d "$TARGET_DIR" ]]; then
  echo "ERROR: Directory '$TARGET_DIR' already exists." >&2
  echo "       Choose a different tool name or remove the existing directory first." >&2
  exit 1
fi

prompt "Proceed? [y/N]" CONFIRM

if [[ "$(to_lower "$CONFIRM")" != "y" ]]; then
  echo "Aborted."
  exit 0
fi

# ---------------------------------------------------------------------------
# Create directory structure
# ---------------------------------------------------------------------------

require_cmd git

print_step "Creating directory structure in $TARGET_DIR"

mkdir -p "$TARGET_DIR/src"
mkdir -p "$TARGET_DIR/docs/forge"
mkdir -p "$TARGET_DIR/release"
mkdir -p "$TARGET_DIR/scripts"

if [[ "$VISIBILITY" == "closed-source" ]]; then
  mkdir -p "$TARGET_DIR/bin"
fi

# ---------------------------------------------------------------------------
# Copy FORGE templates
# ---------------------------------------------------------------------------

print_step "Copying FORGE templates into docs/forge/"

if [[ ! -d "$FORGE_TEMPLATES_DIR" ]]; then
  echo "ERROR: FORGE templates directory not found at $FORGE_TEMPLATES_DIR" >&2
  exit 1
fi

for template in "$FORGE_TEMPLATES_DIR"/*.template.md "$FORGE_TEMPLATES_DIR"/*.template.yaml; do
  [[ -e "$template" ]] || continue
  filename="$(basename "$template")"
  dest="${filename//.template/}"
  cp "$template" "$TARGET_DIR/docs/forge/$dest"
  echo "  Copied: $dest"
done

if [[ -f "$FORGE_TEMPLATES_DIR/TOOL_WORKFLOW.template.md" ]]; then
  cp "$FORGE_TEMPLATES_DIR/TOOL_WORKFLOW.template.md" "$TARGET_DIR/docs/forge/TOOL_WORKFLOW.md"
  echo "  Copied: TOOL_WORKFLOW.md"
fi

# ---------------------------------------------------------------------------
# Generate forge.yaml
# ---------------------------------------------------------------------------

print_step "Generating forge.yaml"

TOOL_NAME_LOWER="$(to_lower "$TOOL_NAME")"

if [[ "$VISIBILITY" == "open-source" ]]; then
cat > "$TARGET_DIR/forge.yaml" <<EOF
project: $TOOL_NAME

type: $TOOL_TYPE

visibility: open-source

src_dir: src
release_dir: release

docs_dir: docs/forge

repos:
  dev: $DEV_REPO
  public: $PUBLIC_REPO
EOF
else
cat > "$TARGET_DIR/forge.yaml" <<EOF
project: $TOOL_NAME

type: $TOOL_TYPE

visibility: closed-source

src_dir: src
release_dir: release

docs_dir: docs/forge

build_output:
  - bin/${TOOL_NAME_LOWER}-linux
  - bin/${TOOL_NAME_LOWER}-macos
  - bin/${TOOL_NAME_LOWER}-win.exe

repos:
  dev: $DEV_REPO
  public: $PUBLIC_REPO
EOF
fi

echo "  Created: forge.yaml"

# ---------------------------------------------------------------------------
# Copy publish scripts
# ---------------------------------------------------------------------------

print_step "Copying release scripts"

for script in forge-publish.sh forge-publish.ps1; do
  if [[ -f "$FORGE_ROOT/scripts/$script" ]]; then
    cp "$FORGE_ROOT/scripts/$script" "$TARGET_DIR/scripts/$script"
    echo "  Copied: scripts/$script"
  fi
done

# ---------------------------------------------------------------------------
# Create README placeholder
# ---------------------------------------------------------------------------

cat > "$TARGET_DIR/README.md" <<EOF
# $TOOL_NAME

<!-- Replace this with a description of your tool. -->

## Development

This project uses [FORGE](https://github.com/redteamlife/forge) for AI-assisted development governance.

All development occurs in this repository. Releases are published to \`$PUBLIC_REPO\` via \`./scripts/forge-publish.sh\`.
EOF

# ---------------------------------------------------------------------------
# Create .gitignore
# ---------------------------------------------------------------------------

cat > "$TARGET_DIR/.gitignore" <<EOF
# Release staging directory — populated by forge-publish, not committed
/release/

# Compiled binaries
/bin/

# OS and editor noise
.DS_Store
Thumbs.db
*.swp
EOF

# ---------------------------------------------------------------------------
# Initialize git
# ---------------------------------------------------------------------------

print_step "Initializing git repository"

git -C "$TARGET_DIR" init
# Rename to main regardless of git version (works even if already on main)
git -C "$TARGET_DIR" symbolic-ref HEAD refs/heads/main

git -C "$TARGET_DIR" add .
git -C "$TARGET_DIR" commit -m "chore: initial FORGE scaffold for $TOOL_NAME

FORGE-mode: Lightweight
FORGE-task: INIT-001
FORGE-gate: pass"

echo "  Git repository initialized with initial commit."

# ---------------------------------------------------------------------------
# Optional: create GitHub repos
# ---------------------------------------------------------------------------

echo ""
if command -v gh &>/dev/null; then
  prompt "Create GitHub repositories with 'gh'? [y/N]" CREATE_GH

  if [[ "$(to_lower "$CREATE_GH")" == "y" ]]; then
    print_step "Creating GitHub repositories"

    gh repo create "$DEV_REPO" --private 2>/dev/null \
      && echo "  Created private repo: $DEV_REPO" \
      || echo "  WARN: Could not create $DEV_REPO (may already exist or insufficient permissions)"

    gh repo create "$PUBLIC_REPO" --public 2>/dev/null \
      && echo "  Created public repo: $PUBLIC_REPO" \
      || echo "  WARN: Could not create $PUBLIC_REPO (may already exist or insufficient permissions)"

    GH_USER="$(gh api user -q .login 2>/dev/null || echo '')"
    if [[ -n "$GH_USER" ]]; then
      git -C "$TARGET_DIR" remote add origin "https://github.com/$GH_USER/$DEV_REPO.git"
      git -C "$TARGET_DIR" remote add public "https://github.com/$GH_USER/$PUBLIC_REPO.git"
      echo "  Remotes configured: origin ($DEV_REPO), public ($PUBLIC_REPO)"
    fi
  fi
else
  echo "NOTE: 'gh' CLI not found. Add GitHub remotes manually:"
  echo "  git remote add origin  https://github.com/<org>/$DEV_REPO.git"
  echo "  git remote add public  https://github.com/<org>/$PUBLIC_REPO.git"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
echo "================================================================"
echo "  $TOOL_NAME scaffold created at: $TARGET_DIR"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. cd $DEV_REPO"
echo "  2. Generate FORGE project docs — point your AI at:"
echo "     $FORGE_TEMPLATES_DIR/GENERATE_PROJECT_DOCS.md"
echo "     and tell it to generate docs for your project."
echo "  3. Review and update docs/forge/AI.md with your project scope"
echo "  4. Add tasks to docs/forge/TASKS.yaml"
echo "  5. Start a FORGE session"
echo ""
if [[ "$VISIBILITY" == "closed-source" ]]; then
  echo "  When ready to release:"
  echo "  Compile your binaries to the paths in forge.yaml build_output,"
  echo "  then run: ./scripts/forge-publish.sh --tag v0.1.0"
  echo ""
fi
