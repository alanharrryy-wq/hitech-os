#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
OUTPUT_DIR="${2:-docs/live-scene-composer/architecture-artifacts}"

python "$REPO_ROOT/tools/live-scene-composer/generate_architecture_artifacts.py" \
  --repo-root "$REPO_ROOT" \
  --output-dir "$OUTPUT_DIR"
