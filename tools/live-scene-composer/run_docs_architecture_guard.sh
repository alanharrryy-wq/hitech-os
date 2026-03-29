#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
DOCS_ROOT="${2:-docs/live-scene-composer}"

python "$REPO_ROOT/tools/live-scene-composer/validate_docs_architecture_guard.py" \
  --repo-root "$REPO_ROOT" \
  --docs-root "$DOCS_ROOT" \
  --write-report
