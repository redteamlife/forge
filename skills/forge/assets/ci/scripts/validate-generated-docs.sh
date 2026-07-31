#!/bin/bash
# FORGE CI: Validate that generated documentation files are complete and not template artifacts.
# Checks for unfilled placeholders, empty required sections, and missing required files.
# Intended to run as a setup gate and on every PR.

set -e

FORGE_DIR="docs/forge"
FAILED=0

# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

check_file_exists() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo "FORGE: Missing required file: $file"
    FAILED=1
    return 1
  fi
  return 0
}

check_no_placeholders() {
  local file="$1"
  # Match common template placeholder patterns
  if grep -qE '\{\{[^}]+\}\}|<[A-Z][A-Z _]+>|\[TODO\]|\[PLACEHOLDER\]|\[YOUR_' "$file" 2>/dev/null; then
    echo "FORGE: Unfilled template placeholders found in: $file"
    grep -nE '\{\{[^}]+\}\}|<[A-Z][A-Z _]+>|\[TODO\]|\[PLACEHOLDER\]|\[YOUR_' "$file" | head -5
    FAILED=1
  fi
}

check_section_nonempty() {
  local file="$1"
  local heading="$2"
  # Find the heading line; check if the next non-blank line is another heading or EOF
  local content
  content=$(awk "
    /^#+ ${heading}/ { found=1; next }
    found && /^[[:space:]]*$/ { next }
    found && /^#/ { exit }
    found { print; exit }
  " "$file")
  if [ -z "$content" ]; then
    echo "FORGE: Required section '$heading' is empty in: $file"
    FAILED=1
  fi
}

check_yaml_field_nonempty() {
  local file="$1"
  local field="$2"
  local value
  value=$(python3 - "$file" "$field" <<'EOF'
import sys
import yaml

with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)

field = sys.argv[2]
val = data.get(field) if data else None
print("" if val is None else str(val).strip())
EOF
)
  if [ -z "$value" ]; then
    echo "FORGE: Required YAML field '$field' is missing or empty in: $file"
    FAILED=1
  fi
}

get_config_value() {
  local file="$1"
  local field="$2"
  grep -m1 -E "^[[:space:]]*${field}:" "$file" 2>/dev/null | sed "s/^[[:space:]]*${field}: *//" | sed 's/[[:space:]]*$//'
}

has_config_field() {
  local file="$1"
  local field="$2"
  grep -q -E "^[[:space:]]*${field}:" "$file" 2>/dev/null
}

# -----------------------------------------------------------------------
# Check required files exist
# -----------------------------------------------------------------------

REQUIRED_FILES=(
  "$FORGE_DIR/AI.md"
)

if [ -f "$FORGE_DIR/TASKS.index.yaml" ]; then
  REQUIRED_FILES+=("$FORGE_DIR/TASKS.index.yaml")
else
  REQUIRED_FILES+=("$FORGE_DIR/TASKS.yaml")
fi

AI_MD="$FORGE_DIR/AI.md"
FORGE_MODE=""
COLLABORATION_MODE=""
SECURITY_PROFILE=""

if [ -f "$AI_MD" ]; then
  FORGE_MODE=$(get_config_value "$AI_MD" "FORGE_mode")
  COLLABORATION_MODE=$(get_config_value "$AI_MD" "collaboration_mode")
  SECURITY_PROFILE=$(get_config_value "$AI_MD" "security_profile")
fi

# Mid and above require additional files
if [ "$FORGE_MODE" != "Lightweight" ] && [ -n "$FORGE_MODE" ]; then
  REQUIRED_FILES+=(
    "$FORGE_DIR/ARCHITECTURE.md"
    "$FORGE_DIR/EVALUATION.md"
    "$FORGE_DIR/MEMORY.md"
  )
  if [ ! -d "$FORGE_DIR/security-checklists" ]; then
    REQUIRED_FILES+=("$FORGE_DIR/SECURITY_CHECKLISTS.md")
  fi
fi

# Legacy Strict-era files (ARCHITECTURE_EXPLORATION.md, REVIEW_GUIDE.md,
# ROADMAP.md, TEST_STRATEGY.md) are optional: doc-minimums says do not
# generate them by default, so they are validated only for placeholders when
# present (below), never required.

# Team collaboration requires explicit coordination docs.
if [ "$COLLABORATION_MODE" = "team" ]; then
  REQUIRED_FILES+=(
    "$FORGE_DIR/TEAM.md"
    "$FORGE_DIR/EVALUATION.md"
    "$FORGE_DIR/MEMORY.md"
  )
  if [ ! -d "$FORGE_DIR/security-checklists" ]; then
    REQUIRED_FILES+=("$FORGE_DIR/SECURITY_CHECKLISTS.md")
  fi
fi

FILES_OK=1
for f in "${REQUIRED_FILES[@]}"; do
  check_file_exists "$f" || FILES_OK=0
done

# If files are missing, report and exit - no point checking content
if [ "$FILES_OK" -eq 0 ]; then
  echo ""
  echo "FORGE: Required documentation files are missing. Bootstrap or refresh docs/forge with the forge skill before proceeding."
  exit 1
fi

# -----------------------------------------------------------------------
# Check for unfilled template placeholders in each required file
# -----------------------------------------------------------------------

for f in "${REQUIRED_FILES[@]}"; do
  [ -f "$f" ] && check_no_placeholders "$f"
done

# -----------------------------------------------------------------------
# Check required sections are non-empty
# -----------------------------------------------------------------------

check_section_nonempty "$FORGE_DIR/AI.md" "Purpose"
check_section_nonempty "$FORGE_DIR/AI.md" "Constraints"

if [ -f "$FORGE_DIR/ARCHITECTURE.md" ]; then
  check_section_nonempty "$FORGE_DIR/ARCHITECTURE.md" "Overview"
fi

if [ -f "$FORGE_DIR/EVALUATION.md" ]; then
  check_section_nonempty "$FORGE_DIR/EVALUATION.md" "Definition of Done"
fi

if [ -f "$FORGE_DIR/TEAM.md" ]; then
  check_section_nonempty "$FORGE_DIR/TEAM.md" "Branch Policy"
  check_section_nonempty "$FORGE_DIR/TEAM.md" "Task Claiming"
  check_section_nonempty "$FORGE_DIR/TEAM.md" "Task Ledger Semantics"
  check_section_nonempty "$FORGE_DIR/TEAM.md" "Integration Flow"
  check_section_nonempty "$FORGE_DIR/TEAM.md" "File Scope"
  check_section_nonempty "$FORGE_DIR/TEAM.md" "Task Closeout"
  check_section_nonempty "$FORGE_DIR/TEAM.md" "Review And Merge"
fi

# SETUP.md sections are gated by security_profile (see the SETUP template):
# always: Local Hooks, CI Enforcement, Team Closeout, Release Reconciliation
# repo-fortress and above: Branch Protection
# ci-security and above: CI Security, Supply Chain
# full-devsecops: Continuous Delivery Security
if [ -f "$FORGE_DIR/SETUP.md" ]; then
  check_section_nonempty "$FORGE_DIR/SETUP.md" "Local Hooks"
  check_section_nonempty "$FORGE_DIR/SETUP.md" "CI Enforcement"
  check_section_nonempty "$FORGE_DIR/SETUP.md" "Team Closeout"
  check_section_nonempty "$FORGE_DIR/SETUP.md" "Release Reconciliation"
  case "$SECURITY_PROFILE" in
    repo-fortress|ci-security|full-devsecops)
      check_section_nonempty "$FORGE_DIR/SETUP.md" "Branch Protection"
      ;;
  esac
  case "$SECURITY_PROFILE" in
    ci-security|full-devsecops)
      check_section_nonempty "$FORGE_DIR/SETUP.md" "CI Security"
      check_section_nonempty "$FORGE_DIR/SETUP.md" "Supply Chain"
      ;;
  esac
  if [ "$SECURITY_PROFILE" = "full-devsecops" ]; then
    check_section_nonempty "$FORGE_DIR/SETUP.md" "Continuous Delivery Security"
  fi
fi

# -----------------------------------------------------------------------
# Clean-main: release-branch-guard workflow env must mirror dev_only_paths
# (the guard runs on the release branch, which has no AI.md by design, so
# the workflow carries a copy — drift between the two is a failing check)
# -----------------------------------------------------------------------

DEV_ONLY_PATHS_VALUE=$(get_config_value "$AI_MD" "dev_only_paths")
GUARD_WORKFLOW=".github/workflows/release-branch-guard.yml"
if [ -n "$DEV_ONLY_PATHS_VALUE" ] && [ -f "$GUARD_WORKFLOW" ]; then
  GUARD_LIST=$(grep -m1 -E '^[[:space:]]*DEV_ONLY_PATHS:' "$GUARD_WORKFLOW" \
    | sed 's/^[[:space:]]*DEV_ONLY_PATHS:[[:space:]]*//' | tr -d '"')
  for entry in $(echo "$DEV_ONLY_PATHS_VALUE" | tr ',' '\n'); do
    entry=$(echo "$entry" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//; s|/*$||')
    [ -n "$entry" ] || continue
    found=0
    for g in $GUARD_LIST; do
      g=$(echo "$g" | sed 's|/*$||')
      [ "$g" = "$entry" ] && found=1 && break
    done
    if [ "$found" -eq 0 ]; then
      echo "FORGE: dev_only_paths entry '$entry' is missing from DEV_ONLY_PATHS in $GUARD_WORKFLOW."
      echo "  The release-branch guard cannot read AI.md (stripped by design); keep its env list in sync."
      FAILED=1
    fi
  done
fi

# -----------------------------------------------------------------------
# Check security checklist layout is usable, not an index-only scaffold
# -----------------------------------------------------------------------

has_checklist_items() {
  grep -qE '^[[:space:]]*- \[[ xX]\]' "$1" 2>/dev/null
}

CHECKLIST_DIR="$FORGE_DIR/security-checklists"
CHECKLIST_FILE="$FORGE_DIR/SECURITY_CHECKLISTS.md"

if [ -d "$CHECKLIST_DIR" ]; then
  if [ ! -f "$CHECKLIST_DIR/general.md" ]; then
    echo "FORGE: $CHECKLIST_DIR exists but is missing the mandatory general.md baseline checklist."
    FAILED=1
  elif ! has_checklist_items "$CHECKLIST_DIR/general.md"; then
    echo "FORGE: $CHECKLIST_DIR/general.md contains no checklist items ('- [ ]')."
    FAILED=1
  fi
elif [ -f "$CHECKLIST_FILE" ]; then
  if grep -q 'security-checklists/' "$CHECKLIST_FILE"; then
    echo "FORGE: $CHECKLIST_FILE references docs/forge/security-checklists/ but that directory does not exist."
    echo "  Repair via forge-bootstrap: copy general.md plus relevant surface checklists from the skill pack's assets/security-checklists/."
    FAILED=1
  elif ! has_checklist_items "$CHECKLIST_FILE"; then
    echo "FORGE: $CHECKLIST_FILE contains no checklist items ('- [ ]'); an index-only or empty checklist file is not a usable security-review surface."
    FAILED=1
  fi
else
  case "$SECURITY_PROFILE" in
    repo-fortress|ci-security|full-devsecops)
      echo "FORGE: security_profile is '$SECURITY_PROFILE' but no security checklist layout exists (docs/forge/security-checklists/ or SECURITY_CHECKLISTS.md)."
      FAILED=1
      ;;
  esac
fi

# -----------------------------------------------------------------------
# Check TASKS.yaml structure
# -----------------------------------------------------------------------

TASKS_INDEX_FILE="$FORGE_DIR/TASKS.index.yaml"
TASKS_FILE="$FORGE_DIR/TASKS.yaml"
if [ -f "$TASKS_INDEX_FILE" ]; then
  python3 - "$TASKS_INDEX_FILE" "$FORGE_DIR" <<'EOF'
import sys
from pathlib import Path
import yaml

with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)

forge_dir = Path(sys.argv[2])
repo_root = forge_dir.parent.parent
tasks = data.get("tasks", []) if data else []
if not tasks:
    print("FORGE: TASKS.index.yaml contains no tasks.")
    sys.exit(1)

failed = False
valid_statuses = {"todo", "incomplete", "claimed", "in_progress", "implemented", "integrated", "blocked", "complete"}
for task in tasks:
    tid = task.get("id")
    title = task.get("title")
    status = task.get("status")
    task_file = task.get("task_file")
    if not tid or str(tid).strip() == "":
        print("FORGE: A task index entry is missing an 'id' field.")
        failed = True
    if not title or str(title).strip() == "":
        print(f"FORGE: Task index entry '{tid}' is missing a 'title'.")
        failed = True
    if status not in valid_statuses:
        print(f"FORGE: Task index entry '{tid}' has invalid status '{status}'.")
        failed = True
    if not task_file:
        print(f"FORGE: Task index entry '{tid}' is missing 'task_file'.")
        failed = True
    elif not (repo_root / task_file).is_file():
        print(f"FORGE: Task index entry '{tid}' points to missing task_file '{task_file}'.")
        failed = True

if failed:
    sys.exit(1)
EOF
  TASKS_OK=$?
  if [ "$TASKS_OK" -ne 0 ]; then
    FAILED=1
  fi
elif [ -f "$TASKS_FILE" ]; then
  python3 - "$TASKS_FILE" <<'EOF'
import sys
import yaml

with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)

tasks = data.get("tasks", []) if data else []
if not tasks:
    print("FORGE: TASKS.yaml contains no tasks.")
    sys.exit(1)

failed = False
for task in tasks:
    tid = task.get("id")
    desc = task.get("description")
    status = task.get("status")
    if not tid or str(tid).strip() == "":
        print(f"FORGE: A task is missing an 'id' field.")
        failed = True
    if not desc or str(desc).strip() == "":
        print(f"FORGE: Task '{tid}' is missing a 'description'.")
        failed = True
    if status not in ("todo", "incomplete", "claimed", "in_progress", "implemented", "integrated", "blocked", "complete"):
        print(f"FORGE: Task '{tid}' has invalid status '{status}'. Must be one of todo, incomplete, claimed, in_progress, implemented, integrated, blocked, complete.")
        failed = True

if failed:
    sys.exit(1)
EOF
  TASKS_OK=$?
  if [ "$TASKS_OK" -ne 0 ]; then
    FAILED=1
  fi
fi

# -----------------------------------------------------------------------
# Check AI.md FORGE-config block has required fields
# -----------------------------------------------------------------------

if grep -q 'FORGE-config' "$AI_MD"; then
  if ! has_config_field "$AI_MD" "FORGE_mode"; then
    echo "FORGE: FORGE-config block in AI.md is missing FORGE_mode."
    FAILED=1
  fi
  if ! has_config_field "$AI_MD" "execution_mode"; then
    echo "FORGE: FORGE-config block in AI.md is missing execution_mode."
    FAILED=1
  else
    EXECUTION_MODE_VALUE=$(get_config_value "$AI_MD" "execution_mode")
    case "$EXECUTION_MODE_VALUE" in
      manual|batch|auto)
        ;;
      *)
        echo "FORGE: execution_mode must be manual, batch, or auto."
        FAILED=1
        ;;
    esac
    if [ "$EXECUTION_MODE_VALUE" = "batch" ] && ! has_config_field "$AI_MD" "batch_size"; then
      echo "FORGE: execution_mode: batch requires batch_size."
      FAILED=1
    fi
  fi
  for field in coordination_branch integration_branch release_branch dev_only_paths; do
    if has_config_field "$AI_MD" "$field"; then
      FIELD_VALUE=$(get_config_value "$AI_MD" "$field")
      if [ -z "$FIELD_VALUE" ]; then
        echo "FORGE: ${field} must not be empty when present."
        FAILED=1
      fi
    fi
  done
  if has_config_field "$AI_MD" "collaboration_mode"; then
    COLLAB_MODE_VALUE=$(get_config_value "$AI_MD" "collaboration_mode")
    if [ "$COLLAB_MODE_VALUE" != "solo" ] && [ "$COLLAB_MODE_VALUE" != "team" ]; then
      echo "FORGE: collaboration_mode must be 'solo' or 'team' when present."
      FAILED=1
    fi
  fi
  if has_config_field "$AI_MD" "task_source"; then
    TASK_SOURCE_VALUE=$(get_config_value "$AI_MD" "task_source")
    case "$TASK_SOURCE_VALUE" in
      local|github|gitlab|external)
        ;;
      *)
        echo "FORGE: task_source must be local, github, gitlab, or external when present."
        FAILED=1
        ;;
    esac
  fi
  if has_config_field "$AI_MD" "repo_flavor"; then
    REPO_FLAVOR_VALUE=$(get_config_value "$AI_MD" "repo_flavor")
    case "$REPO_FLAVOR_VALUE" in
      contract-first|tooling)
        ;;
      *)
        echo "FORGE: repo_flavor must be contract-first or tooling when present."
        FAILED=1
        ;;
    esac
  fi
  if has_config_field "$AI_MD" "application_docs"; then
    APPLICATION_DOCS_VALUE=$(get_config_value "$AI_MD" "application_docs")
    case "$APPLICATION_DOCS_VALUE" in
      true|false)
        ;;
      *)
        echo "FORGE: application_docs must be true or false when present."
        FAILED=1
        ;;
    esac
  fi
  if has_config_field "$AI_MD" "security_profile"; then
    SECURITY_PROFILE_VALUE=$(get_config_value "$AI_MD" "security_profile")
    case "$SECURITY_PROFILE_VALUE" in
      baseline|repo-fortress|ci-security|full-devsecops)
        ;;
      *)
        echo "FORGE: security_profile must be baseline, repo-fortress, ci-security, or full-devsecops when present."
        FAILED=1
        ;;
    esac
  fi
  if has_config_field "$AI_MD" "agent_context_profile"; then
    AGENT_CONTEXT_PROFILE_VALUE=$(get_config_value "$AI_MD" "agent_context_profile")
    case "$AGENT_CONTEXT_PROFILE_VALUE" in
      lite|standard|full)
        ;;
      *)
        echo "FORGE: agent_context_profile must be lite, standard, or full when present."
        FAILED=1
        ;;
    esac
  fi
else
  echo "FORGE: AI.md is missing a FORGE-config block."
  FAILED=1
fi

# -----------------------------------------------------------------------
# Result
# -----------------------------------------------------------------------

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "FORGE: Documentation validation failed."
  echo "  Review and correct the issues above before starting a governed session."
  exit 1
fi

echo "FORGE: Documentation validation passed (mode: ${FORGE_MODE:-unknown})."
