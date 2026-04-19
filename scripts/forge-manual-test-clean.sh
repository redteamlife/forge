#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRATCH_ROOT="$ROOT_DIR/.tmp/manual-tests"

if [ ! -d "$SCRATCH_ROOT" ]; then
  printf 'FORGE manual test scratch area not present: %s\n' "$SCRATCH_ROOT"
  exit 0
fi

rm -rf "$SCRATCH_ROOT"
printf 'FORGE manual test scratch area removed: %s\n' "$SCRATCH_ROOT"
