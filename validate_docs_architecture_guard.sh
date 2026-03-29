#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
DOCS_ROOT="${2:-docs/live-scene-composer}"
REPORT_FILE="${3:-tools/_local/evidence/live_scene_composer_docs_arch_guard_report.txt}"

REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"
DOCS_PATH="$REPO_ROOT/$DOCS_ROOT"
REPORT_PATH="$REPO_ROOT/$REPORT_FILE"

mkdir -p "$(dirname "$REPORT_PATH")"

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

TMP_REPORT="$(mktemp)"
trap 'rm -f "$TMP_REPORT"' EXIT

log_line() {
  printf "%s\n" "$1" | tee -a "$TMP_REPORT" >/dev/null
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  log_line "[PASS] $1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  log_line "[FAIL] $1"
}

warn() {
  WARN_COUNT=$((WARN_COUNT + 1))
  log_line "[WARN] $1"
}

check_file_exists() {
  local file="$1"
  local label="$2"
  if [ -f "$file" ]; then
    pass "$label"
  else
    fail "$label :: missing file: ${file#$REPO_ROOT/}"
  fi
}

check_dir_absent() {
  local dir="$1"
  local label="$2"
  if [ -d "$dir" ]; then
    fail "$label :: forbidden path exists: ${dir#$REPO_ROOT/}"
  else
    pass "$label"
  fi
}

check_contains_all_tokens() {
  local file="$1"
  local label="$2"
  shift 2
  local missing=0
  for token in "$@"; do
    if ! grep -Fq "$token" "$file"; then
      log_line "  - missing token in ${file#$REPO_ROOT/}: $token"
      missing=1
    fi
  done

  if [ "$missing" -eq 0 ]; then
    pass "$label"
  else
    fail "$label"
  fi
}

scan_sources() {
  find "$REPO_ROOT/apps/keystone/components" "$REPO_ROOT/apps/keystone/tests" \
    -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.mjs" -o -name "*.cjs" \) 2>/dev/null
}

print_header() {
  log_line "========================================================================"
  log_line "LIVE SCENE COMPOSER DOCS ARCHITECTURE GUARD (BASH)"
  log_line "========================================================================"
  log_line "Repo root : $REPO_ROOT"
  log_line "Docs root : ${DOCS_PATH#$REPO_ROOT/}"
  log_line "Report    : ${REPORT_PATH#$REPO_ROOT/}"
  log_line ""
}

print_summary() {
  log_line ""
  log_line "------------------------------------------------------------------------"
  log_line "SUMMARY"
  log_line "------------------------------------------------------------------------"
  log_line "Passes   : $PASS_COUNT"
  log_line "Fails    : $FAIL_COUNT"
  log_line "Warnings : $WARN_COUNT"
  if [ "$FAIL_COUNT" -eq 0 ]; then
    log_line "Result   : PASS"
  else
    log_line "Result   : FAIL"
  fi
  log_line "------------------------------------------------------------------------"
}

print_header

# -------------------------------------------------------------------------
# AGR-001 :: docs root and canonical docs
# -------------------------------------------------------------------------

if [ -d "$DOCS_PATH" ]; then
  pass "AGR-001 :: docs root exists"
else
  fail "AGR-001 :: docs root missing: ${DOCS_PATH#$REPO_ROOT/}"
fi

EXPECTED_DOCS=(
  "README.md"
  "00_TOC.md"
  "00_READING_PATHS.md"
  "01_PROJECT_OVERVIEW.md"
  "02_PRODUCT_VISION.md"
  "03_GOALS_AND_NON_GOALS.md"
  "04_CORE_CONCEPTS.md"
  "05_SYSTEM_ARCHITECTURE.md"
  "06_SYSTEM_BOUNDARIES.md"
  "07_DOMAIN_MODEL.md"
  "08_STATE_MODEL.md"
  "09_RUNTIME_MODEL.md"
  "10_MUTATION_MODEL.md"
  "11_MODULE_SYSTEM.md"
  "12_MODULE_SDK.md"
  "13_WIDGET_SYSTEM.md"
  "14_SLOT_SYSTEM.md"
  "15_LAYOUT_SYSTEM.md"
  "16_PREFAB_SYSTEM.md"
  "17_CUSTOM_WIDGET_SANDBOX.md"
  "18_RUNTIME_MUTATION_BRIDGE.md"
  "19_DEPENDENCY_POLICY.md"
  "20_PROTECTED_NODES.md"
  "21_DEVELOPER_GUIDE.md"
  "22_CONTRIBUTING.md"
  "23_CODE_STYLE.md"
  "24_TESTING_STRATEGY.md"
  "25_DEBUGGING_GUIDE.md"
  "26_ERROR_HANDLING.md"
  "27_PERFORMANCE_MODEL.md"
  "28_SECURITY_MODEL.md"
  "29_OPERATIONS_GUIDE.md"
  "30_DEPLOYMENT_MODEL.md"
  "31_USER_MANUAL.md"
  "32_WORKFLOW_GUIDE.md"
  "33_FEATURE_REFERENCE.md"
  "34_UI_INTERACTION_MODEL.md"
  "35_THEME_AND_STYLE_SYSTEM.md"
  "36_DATA_BINDING_MODEL.md"
  "37_VERSIONING_MODEL.md"
  "38_CHANGELOG.md"
  "39_ROADMAP.md"
  "40_ARCHITECTURAL_DECISIONS.md"
  "41_ARCHITECTURE_GUARD_DOC_RULES.md"
)

CRITICAL_DOCS=(
  "README.md"
  "00_TOC.md"
  "00_READING_PATHS.md"
  "01_PROJECT_OVERVIEW.md"
  "05_SYSTEM_ARCHITECTURE.md"
  "06_SYSTEM_BOUNDARIES.md"
  "07_DOMAIN_MODEL.md"
  "10_MUTATION_MODEL.md"
  "18_RUNTIME_MUTATION_BRIDGE.md"
  "19_DEPENDENCY_POLICY.md"
  "20_PROTECTED_NODES.md"
  "40_ARCHITECTURAL_DECISIONS.md"
  "41_ARCHITECTURE_GUARD_DOC_RULES.md"
)

MISSING_EXPECTED=0
for doc in "${EXPECTED_DOCS[@]}"; do
  if [ ! -f "$DOCS_PATH/$doc" ]; then
    log_line "  - missing expected doc: $DOCS_ROOT/$doc"
    MISSING_EXPECTED=1
  fi
done
if [ "$MISSING_EXPECTED" -eq 0 ]; then
  pass "AGR-001A :: all expected docs are present"
else
  fail "AGR-001A :: some expected docs are missing"
fi

MISSING_CRITICAL=0
for doc in "${CRITICAL_DOCS[@]}"; do
  if [ ! -f "$DOCS_PATH/$doc" ]; then
    log_line "  - missing critical doc: $DOCS_ROOT/$doc"
    MISSING_CRITICAL=1
  fi
done
if [ "$MISSING_CRITICAL" -eq 0 ]; then
  pass "AGR-001B :: all critical docs are present"
else
  fail "AGR-001B :: some critical docs are missing"
fi

# -------------------------------------------------------------------------
# AGR-002 :: legacy shared-core path must not exist
# -------------------------------------------------------------------------

LEGACY_CORE_DIR="$REPO_ROOT/apps/keystone/components/dev-console/core"
check_dir_absent "$LEGACY_CORE_DIR" "AGR-002 :: legacy dev-console/core path must be absent"

# -------------------------------------------------------------------------
# AGR-003 :: legacy core imports must not exist
# -------------------------------------------------------------------------

LEGACY_IMPORT_HITS=0
while IFS= read -r file; do
  HITS="$(grep -nE "^[[:space:]]*(import|export)[[:space:]].*from[[:space:]]*['\"][^'\"]*(dev-console/core|components/dev-console/core|/core/|\\./core/)[^'\"]*['\"]|require\\([[:space:]]*['\"][^'\"]*(dev-console/core|components/dev-console/core|/core/|\\./core/)[^'\"]*['\"][[:space:]]*\\)" "$file" || true)"
  if [ -n "$HITS" ]; then
    log_line "  - legacy core import hit: ${file#$REPO_ROOT/}"
    printf "%s\n" "$HITS" | sed 's/^/      /' | tee -a "$TMP_REPORT" >/dev/null
    LEGACY_IMPORT_HITS=1
  fi
done < <(scan_sources)

if [ "$LEGACY_IMPORT_HITS" -eq 0 ]; then
  pass "AGR-003 :: no legacy dev-console/core imports detected"
else
  fail "AGR-003 :: legacy dev-console/core imports detected"
fi

# -------------------------------------------------------------------------
# AGR-004 :: runtime debug must not import composer
# -------------------------------------------------------------------------

DEBUG_TO_COMPOSER=0
RUNTIME_DEBUG_DIR="$REPO_ROOT/apps/keystone/components/dev-console"
if [ -d "$RUNTIME_DEBUG_DIR" ]; then
  while IFS= read -r file; do
    if grep -nE "live-scene-composer" "$file" >/dev/null 2>&1; then
      log_line "  - runtime-debug to composer import suspicion: ${file#$REPO_ROOT/}"
      grep -nE "live-scene-composer" "$file" | sed 's/^/      /' | tee -a "$TMP_REPORT" >/dev/null
      DEBUG_TO_COMPOSER=1
    fi
  done < <(find "$RUNTIME_DEBUG_DIR" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null)
fi

if [ "$DEBUG_TO_COMPOSER" -eq 0 ]; then
  pass "AGR-004 :: runtime-debug boundary does not import composer product logic"
else
  fail "AGR-004 :: runtime-debug boundary imports composer product logic"
fi

# -------------------------------------------------------------------------
# AGR-005 :: composer must not import runtime debug product logic
# -------------------------------------------------------------------------

COMPOSER_TO_DEBUG=0
COMPOSER_TO_PITCH_DEBUG=0
COMPOSER_DIR="$REPO_ROOT/apps/keystone/components/live-scene-composer"

if [ -d "$COMPOSER_DIR" ]; then
  while IFS= read -r file; do
    if grep -nE "runtime-debug-console|dev-console" "$file" >/dev/null 2>&1; then
      FILTERED="$(grep -nE "runtime-debug-console|dev-console" "$file" | grep -v "console-core" || true)"
      if [ -n "$FILTERED" ]; then
        log_line "  - composer to debug import suspicion: ${file#$REPO_ROOT/}"
        printf "%s\n" "$FILTERED" | sed 's/^/      /' | tee -a "$TMP_REPORT" >/dev/null
        COMPOSER_TO_DEBUG=1
      fi
    fi

    if grep -nE "pitch/debug" "$file" >/dev/null 2>&1; then
      log_line "  - composer to pitch/debug warning: ${file#$REPO_ROOT/}"
      grep -nE "pitch/debug" "$file" | sed 's/^/      /' | tee -a "$TMP_REPORT" >/dev/null
      COMPOSER_TO_PITCH_DEBUG=1
    fi
  done < <(find "$COMPOSER_DIR" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null)
fi

if [ "$COMPOSER_TO_DEBUG" -eq 0 ]; then
  pass "AGR-005 :: composer does not import runtime-debug product logic"
else
  fail "AGR-005 :: composer imports runtime-debug or non-console-core dev-console product logic"
fi

if [ "$COMPOSER_TO_PITCH_DEBUG" -eq 0 ]; then
  pass "AGR-W001 :: no direct composer imports to pitch/debug paths detected"
else
  warn "AGR-W001 :: composer imports pitch/debug paths directly; review whether these should be explicit adapter seams"
fi

# -------------------------------------------------------------------------
# AGR-006 :: README / TOC / READING_PATHS must reference critical docs
# -------------------------------------------------------------------------

INDEX_FILES=(
  "$DOCS_PATH/README.md"
  "$DOCS_PATH/00_TOC.md"
  "$DOCS_PATH/00_READING_PATHS.md"
)

CRITICAL_REFERENCES=(
  "01_PROJECT_OVERVIEW.md"
  "05_SYSTEM_ARCHITECTURE.md"
  "06_SYSTEM_BOUNDARIES.md"
  "07_DOMAIN_MODEL.md"
  "10_MUTATION_MODEL.md"
  "18_RUNTIME_MUTATION_BRIDGE.md"
  "19_DEPENDENCY_POLICY.md"
  "20_PROTECTED_NODES.md"
  "40_ARCHITECTURAL_DECISIONS.md"
)

for index_file in "${INDEX_FILES[@]}"; do
  if [ ! -f "$index_file" ]; then
    fail "AGR-006 :: missing index file: ${index_file#$REPO_ROOT/}"
    continue
  fi

  MISSING_REFS=0
  for ref in "${CRITICAL_REFERENCES[@]}"; do
    if ! grep -Fq "$ref" "$index_file"; then
      log_line "  - missing reference in ${index_file#$REPO_ROOT/}: $ref"
      MISSING_REFS=1
    fi
  done

  if [ "$MISSING_REFS" -eq 0 ]; then
    pass "AGR-006 :: ${index_file#$REPO_ROOT/} references critical docs"
  else
    fail "AGR-006 :: ${index_file#$REPO_ROOT/} is missing one or more critical doc references"
  fi
done

# -------------------------------------------------------------------------
# AGR-007 :: guard rules doc must name canonical boundaries
# -------------------------------------------------------------------------

GUARD_DOC="$DOCS_PATH/41_ARCHITECTURE_GUARD_DOC_RULES.md"
if [ -f "$GUARD_DOC" ]; then
  check_contains_all_tokens "$GUARD_DOC" \
    "AGR-007 :: guard rules doc names canonical boundaries" \
    "console-core" \
    "runtime-debug-console" \
    "live-scene-composer" \
    "runtime-mutation-bridge"
else
  fail "AGR-007 :: missing guard rules doc: ${GUARD_DOC#$REPO_ROOT/}"
fi

print_summary
cp "$TMP_REPORT" "$REPORT_PATH"
printf "\nReport written to: %s\n" "${REPORT_PATH#$REPO_ROOT/}"

if [ "$FAIL_COUNT" -eq 0 ]; then
  exit 0
else
  exit 1
fi
