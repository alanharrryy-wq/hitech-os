#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs/live-scene-composer}"
TOOLS_DIR="${2:-tools/live-scene-composer}"

mkdir -p "$DOCS_DIR"
mkdir -p "$TOOLS_DIR"

cat > "$DOCS_DIR/41_ARCHITECTURE_GUARD_DOC_RULES.md" <<'EOF'
# 41_ARCHITECTURE_GUARD_DOC_RULES

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation, Reviewers
- Scope: Enforceable documentation-to-code rules for Live Scene Composer and sibling boundaries

---

## Purpose

This document defines the architecture guard rules that must remain true for the Live Scene Composer ecosystem.

Its purpose is not only to describe architecture.
Its purpose is to define the rules that tooling and review should enforce so the documentation cannot silently drift away from the codebase.

This document is meant to have teeth.

---

## Why This Exists

Large systems do not usually rot because someone wrote one bad function.
They rot because:

- boundaries blur slowly
- "temporary" shortcuts survive
- old paths reappear
- docs stop matching reality
- protected seams change without review
- sibling products start importing each other because it was convenient one afternoon

This document exists so the project can detect that drift early.

---

## Core Principle

If the code and the documentation disagree on foundational architecture, that is a real defect.

The response should not be:
"the docs are probably stale"

The response should be:
"identify the truth, fix the mismatch, and restore alignment"

---

## Canonical Boundary Model

The system must preserve these top-level boundaries:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

These are not naming suggestions.
They are the intended top-level architectural seams.

---

## Canonical Project Truths

The following truths are treated as non-negotiable unless explicitly re-decided through a documented architecture decision.

### Truth 1

**Runtime Debug Console and Live Scene Composer are sibling products, not one product with two moods.**

### Truth 2

**`console-core` is the only canonical shared infrastructure layer.**

### Truth 3

**Legacy shared-core paths must not be reintroduced.**

### Truth 4

**Live Scene Composer must not directly mutate runtime-facing state outside `runtime-mutation-bridge`.**

### Truth 5

**`runtime-debug-console` must not register or absorb Composer authoring logic.**

### Truth 6

**The canonical authoring model is: Scene -> Layout -> Slots -> Widgets.**

### Truth 7

**Protected nodes and mutation boundaries require stronger review and stronger evidence.**

---

## What the Guard Must Protect

The architecture/docs guard should protect at minimum:

- canonical docs presence
- canonical shared-core path discipline
- sibling boundary separation
- no legacy `dev-console/core` path drift
- no composer/debug cross-import drift
- existence of the critical architecture docs
- index and reading path consistency for core documents
- explicit rule ownership for protected seams

The guard is not meant to prove the whole product is correct.
It is meant to detect foundational drift.

---

## Rule Catalog

### AGR-001: Canonical docs must exist

The project must contain the canonical Live Scene Composer documentation set in the expected docs location.

At minimum, the following files are critical and must exist:

- `README.md`
- `00_TOC.md`
- `00_READING_PATHS.md`
- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`
- `41_ARCHITECTURE_GUARD_DOC_RULES.md`

A project can survive missing nice-to-have docs for a short time.
It should not normalize missing foundation docs.

---

### AGR-002: Legacy shared-core path must not exist

The following path must not reappear as active canonical code:

- `apps/keystone/components/dev-console/core/`

If that path exists again, the guard should fail unless there is an explicit, documented, reviewed architecture reversal.

---

### AGR-003: Legacy core imports must not exist

Imports referencing the old dev-console core path must fail the guard.

Examples of forbidden import forms include:

- `dev-console/core`
- `./core/`
- `/core/`

when they refer to the legacy shared-core path inside the dev-console boundary.

---

### AGR-004: Runtime Debug Console must not import Composer product logic

Code inside the Runtime Debug Console boundary must not import `live-scene-composer` product logic.

This includes direct and obvious imports into Composer product paths.

The reason is simple:
diagnostics must not quietly become authoring hosts.

---

### AGR-005: Live Scene Composer must not import Runtime Debug Console product logic

Code inside the Composer boundary must not import Runtime Debug Console product logic.

The Composer may reuse `console-core`.
It may not consume debug product internals as if they were its platform.

---

### AGR-006: The docs index must reflect the critical docs

`README.md`, `00_TOC.md`, and `00_READING_PATHS.md` must continue to reference the critical architectural documents.

This exists to prevent onboarding drift and the slow disappearance of the actual rules that keep the project sane.

---

### AGR-007: Guard rules doc must name the canonical boundaries

This file must continue to mention the canonical boundary names:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

If that stops being true, the guard itself is drifting away from the architecture.

---

### AGR-008: Docs/code drift is a failure, not just a note

When a foundational doc is wrong or a foundational code rule is broken, the expected response is to fix the mismatch.

The guard should be treated as a quality gate for foundational alignment.

---

## Protected Areas Covered by This Guard

This guard is especially concerned with the following high-impact seams:

- shared-core boundary discipline
- sibling product separation
- mutation governance boundary presence
- dependency policy stability
- documentation discoverability for critical architecture rules

This does not replace protected-node review.
It reinforces it.

---

## Evidence Expectations

Changes that affect the guard should normally provide evidence such as:

- architecture guard output
- targeted tests
- typecheck where relevant
- explicit explanation of why a rule changed
- updated docs if the rule meaning changed

This is one of the places where "it compiles" is nowhere near enough.

---

## CI and Local Use

This guard should be runnable:

- locally by contributors
- in CI
- before or during review for risky changes

Suggested usage:

- run it after documentation generation
- run it after boundary refactors
- run it whenever shared-core, bridge, provider, or sibling-product seams change

---

## What This Guard Intentionally Does Not Guarantee

This guard does not guarantee:

- perfect product behavior
- perfect runtime correctness
- perfect mutation semantics
- complete dependency-graph proof of all architecture assumptions

That is not its job.

Its job is to catch a specific class of high-value architectural/documentation drift.

---

## Process for Changing a Guard Rule

A rule in this document should not be changed casually.

When a rule must change:

1. explain why the old rule is no longer valid
2. update related architecture docs
3. update the validator logic
4. update tests or evidence expectations if needed
5. record the reasoning in `40_ARCHITECTURAL_DECISIONS.md` if the change is architectural in nature

This keeps the guard from becoming random.

---

## Failure Philosophy

A guard failure should be treated as one of these:

- architecture drift
- documentation drift
- forbidden dependency drift
- canonical path regression
- missing critical documentation

That means a failure is meaningful.
It is not a decorative warning.

---

## Long-Term Value

If maintained seriously, this guard makes the project much harder to corrupt by accident.

It helps preserve:

- product identity
- boundary discipline
- safer onboarding
- better review quality
- lower architecture entropy over time

That is exactly what a serious system needs.

---

## Summary

This document defines the architecture guard rules that keep Live Scene Composer aligned with its own foundations. It protects canonical docs, canonical boundaries, legacy path discipline, sibling-product separation, and critical documentation discoverability. It exists so the project's rules do not dissolve into tribal memory and wishful thinking.
EOF

cat > "$TOOLS_DIR/validate_docs_architecture_guard.py" <<'EOF'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any


SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
CRITICAL_DOCS = [
    "README.md",
    "00_TOC.md",
    "00_READING_PATHS.md",
    "01_PROJECT_OVERVIEW.md",
    "05_SYSTEM_ARCHITECTURE.md",
    "06_SYSTEM_BOUNDARIES.md",
    "07_DOMAIN_MODEL.md",
    "10_MUTATION_MODEL.md",
    "18_RUNTIME_MUTATION_BRIDGE.md",
    "19_DEPENDENCY_POLICY.md",
    "20_PROTECTED_NODES.md",
    "40_ARCHITECTURAL_DECISIONS.md",
    "41_ARCHITECTURE_GUARD_DOC_RULES.md",
]

ALL_EXPECTED_DOCS = [
    "README.md",
    "00_TOC.md",
    "00_READING_PATHS.md",
] + [f"{i:02d}_{name}.md" for i, name in [
    (1, "PROJECT_OVERVIEW"),
    (2, "PRODUCT_VISION"),
    (3, "GOALS_AND_NON_GOALS"),
    (4, "CORE_CONCEPTS"),
    (5, "SYSTEM_ARCHITECTURE"),
    (6, "SYSTEM_BOUNDARIES"),
    (7, "DOMAIN_MODEL"),
    (8, "STATE_MODEL"),
    (9, "RUNTIME_MODEL"),
    (10, "MUTATION_MODEL"),
    (11, "MODULE_SYSTEM"),
    (12, "MODULE_SDK"),
    (13, "WIDGET_SYSTEM"),
    (14, "SLOT_SYSTEM"),
    (15, "LAYOUT_SYSTEM"),
    (16, "PREFAB_SYSTEM"),
    (17, "CUSTOM_WIDGET_SANDBOX"),
    (18, "RUNTIME_MUTATION_BRIDGE"),
    (19, "DEPENDENCY_POLICY"),
    (20, "PROTECTED_NODES"),
    (21, "DEVELOPER_GUIDE"),
    (22, "CONTRIBUTING"),
    (23, "CODE_STYLE"),
    (24, "TESTING_STRATEGY"),
    (25, "DEBUGGING_GUIDE"),
    (26, "ERROR_HANDLING"),
    (27, "PERFORMANCE_MODEL"),
    (28, "SECURITY_MODEL"),
    (29, "OPERATIONS_GUIDE"),
    (30, "DEPLOYMENT_MODEL"),
    (31, "USER_MANUAL"),
    (32, "WORKFLOW_GUIDE"),
    (33, "FEATURE_REFERENCE"),
    (34, "UI_INTERACTION_MODEL"),
    (35, "THEME_AND_STYLE_SYSTEM"),
    (36, "DATA_BINDING_MODEL"),
    (37, "VERSIONING_MODEL"),
    (38, "CHANGELOG"),
    (39, "ROADMAP"),
    (40, "ARCHITECTURAL_DECISIONS"),
    (41, "ARCHITECTURE_GUARD_DOC_RULES"),
]]

CRITICAL_REFERENCES = [
    "01_PROJECT_OVERVIEW.md",
    "05_SYSTEM_ARCHITECTURE.md",
    "06_SYSTEM_BOUNDARIES.md",
    "07_DOMAIN_MODEL.md",
    "10_MUTATION_MODEL.md",
    "18_RUNTIME_MUTATION_BRIDGE.md",
    "19_DEPENDENCY_POLICY.md",
    "20_PROTECTED_NODES.md",
    "40_ARCHITECTURAL_DECISIONS.md",
]

GUARD_RULE_TOKENS = [
    "console-core",
    "runtime-debug-console",
    "live-scene-composer",
    "runtime-mutation-bridge",
]

IMPORT_RE = re.compile(
    r"(?:import|export)\s+[^;]*?\s+from\s+['\"]([^'\"]+)['\"]|require\(\s*['\"]([^'\"]+)['\"]\s*\)",
    re.MULTILINE | re.DOTALL,
)


def normalize_import_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def iter_source_files(paths: Iterable[Path]) -> Iterable[Path]:
    for base in paths:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in SOURCE_EXTENSIONS:
                yield path


def extract_imports(file_path: Path) -> List[str]:
    text = read_text(file_path)
    values: List[str] = []
    for match in IMPORT_RE.findall(text):
        raw = match[0] or match[1]
        if raw:
            values.append(normalize_import_path(raw))
    return values


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def record(results: List[Dict[str, Any]], rule_id: str, status: str, message: str, files: List[str] | None = None) -> None:
    results.append({
        "rule_id": rule_id,
        "status": status,
        "message": message,
        "files": files or [],
    })


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Live Scene Composer docs against key architecture guard rules.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--docs-root", default="docs/live-scene-composer", help="Docs root path relative to repo root or absolute")
    parser.add_argument("--report-file", default="tools/_local/evidence/live_scene_composer_docs_arch_guard_report.json", help="Output report file")
    parser.add_argument("--write-report", action="store_true", help="Write JSON report to disk")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    docs_root = (repo_root / args.docs_root).resolve() if not Path(args.docs_root).is_absolute() else Path(args.docs_root).resolve()
    report_file = (repo_root / args.report_file).resolve() if not Path(args.report_file).is_absolute() else Path(args.report_file).resolve()

    components_root = repo_root / "apps" / "keystone" / "components"
    dev_console_root = components_root / "dev-console"
    runtime_debug_root = dev_console_root / "runtime-debug-console"
    composer_root = components_root / "live-scene-composer"
    legacy_core_root = dev_console_root / "core"

    results: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    # AGR-001 docs root and canonical docs
    if docs_root.exists():
        record(results, "AGR-001", "PASS", f"Docs root exists: {relative(docs_root, repo_root)}")
    else:
        record(results, "AGR-001", "FAIL", f"Docs root missing: {relative(docs_root, repo_root)}")

    missing_all = [name for name in ALL_EXPECTED_DOCS if not (docs_root / name).exists()]
    if missing_all:
        record(results, "AGR-001A", "FAIL", "Expected documentation files are missing", missing_all)
    else:
        record(results, "AGR-001A", "PASS", "All expected docs 00-41 and index files are present")

    missing_critical = [name for name in CRITICAL_DOCS if not (docs_root / name).exists()]
    if missing_critical:
        record(results, "AGR-001B", "FAIL", "Critical architecture docs are missing", missing_critical)
    else:
        record(results, "AGR-001B", "PASS", "All critical architecture docs are present")

    # AGR-002 legacy core path
    if legacy_core_root.exists():
        record(results, "AGR-002", "FAIL", "Legacy shared-core path exists and must not be reintroduced", [relative(legacy_core_root, repo_root)])
    else:
        record(results, "AGR-002", "PASS", "Legacy shared-core path is absent")

    # Gather imports
    source_files = list(iter_source_files([components_root, repo_root / "apps" / "keystone" / "tests"]))
    legacy_import_hits: List[str] = []
    debug_to_composer_hits: List[str] = []
    composer_to_debug_hits: List[str] = []
    composer_to_pitch_debug_warns: List[str] = []

    for file_path in source_files:
        imports = extract_imports(file_path)
        rel = relative(file_path, repo_root)

        for item in imports:
            item_norm = normalize_import_path(item)

            # AGR-003 legacy core imports
            if "dev-console/core" in item_norm:
                legacy_import_hits.append(f"{rel} -> {item_norm}")
            elif "apps/keystone/components/dev-console" in rel.replace("\\", "/"):
                if item_norm.startswith("./core/") or item_norm == "./core" or "/core/" in item_norm or item_norm.endswith("/core"):
                    legacy_import_hits.append(f"{rel} -> {item_norm}")

            # AGR-004 runtime debug must not import composer
            if "apps/keystone/components/dev-console" in rel.replace("\\", "/"):
                if "live-scene-composer" in item_norm:
                    debug_to_composer_hits.append(f"{rel} -> {item_norm}")

            # AGR-005 composer must not import runtime debug
            if "apps/keystone/components/live-scene-composer" in rel.replace("\\", "/"):
                if "runtime-debug-console" in item_norm or "dev-console" in item_norm and "console-core" not in item_norm:
                    composer_to_debug_hits.append(f"{rel} -> {item_norm}")

            # Warning: composer importing pitch/debug is suspicious
            if "apps/keystone/components/live-scene-composer" in rel.replace("\\", "/"):
                if "pitch/debug" in item_norm:
                    composer_to_pitch_debug_warns.append(f"{rel} -> {item_norm}")

    if legacy_import_hits:
        record(results, "AGR-003", "FAIL", "Legacy dev-console core import references detected", legacy_import_hits)
    else:
        record(results, "AGR-003", "PASS", "No legacy dev-console core imports detected")

    if debug_to_composer_hits:
        record(results, "AGR-004", "FAIL", "Runtime Debug Console boundary imports Composer product logic", debug_to_composer_hits)
    else:
        record(results, "AGR-004", "PASS", "Runtime Debug Console boundary does not import Composer product logic")

    if composer_to_debug_hits:
        record(results, "AGR-005", "FAIL", "Composer imports Runtime Debug Console or non-console-core dev-console product logic", composer_to_debug_hits)
    else:
        record(results, "AGR-005", "PASS", "Composer does not import Runtime Debug Console product logic")

    if composer_to_pitch_debug_warns:
        record(warnings, "AGR-W001", "WARN", "Composer imports pitch/debug paths directly; review whether this should be replaced by an explicit adapter seam", composer_to_pitch_debug_warns)

    # AGR-006 index consistency
    for file_name in ["README.md", "00_TOC.md", "00_READING_PATHS.md"]:
        file_path = docs_root / file_name
        if not file_path.exists():
            continue
        text = read_text(file_path)
        missing_refs = [ref for ref in CRITICAL_REFERENCES if ref not in text]
        if missing_refs:
            record(results, "AGR-006", "FAIL", f"{file_name} is missing references to one or more critical docs", missing_refs)
        else:
            record(results, "AGR-006", "PASS", f"{file_name} references the critical docs")

    # AGR-007 guard rules doc tokens
    guard_doc = docs_root / "41_ARCHITECTURE_GUARD_DOC_RULES.md"
    if guard_doc.exists():
        text = read_text(guard_doc)
        missing_tokens = [token for token in GUARD_RULE_TOKENS if token not in text]
        if missing_tokens:
            record(results, "AGR-007", "FAIL", "Guard rules doc is missing canonical boundary tokens", missing_tokens)
        else:
            record(results, "AGR-007", "PASS", "Guard rules doc names all canonical boundaries")
    else:
        record(results, "AGR-007", "FAIL", "Guard rules doc is missing", ["41_ARCHITECTURE_GUARD_DOC_RULES.md"])

    failures = [r for r in results if r["status"] == "FAIL"]
    passes = [r for r in results if r["status"] == "PASS"]

    summary = {
        "repo_root": str(repo_root),
        "docs_root": str(docs_root),
        "result": "FAIL" if failures else "PASS",
        "pass_count": len(passes),
        "fail_count": len(failures),
        "warn_count": len(warnings),
        "checks": results,
        "warnings": warnings,
    }

    print("=" * 72)
    print("LIVE SCENE COMPOSER DOCS ARCHITECTURE GUARD")
    print("=" * 72)
    print(f"Repo root : {repo_root}")
    print(f"Docs root : {docs_root}")
    print(f"Result    : {summary['result']}")
    print(f"Passes    : {summary['pass_count']}")
    print(f"Fails     : {summary['fail_count']}")
    print(f"Warnings  : {summary['warn_count']}")
    print("")

    for item in results + warnings:
        print(f"[{item['status']}] {item['rule_id']} :: {item['message']}")
        for file_entry in item.get("files", []):
            print(f"  - {file_entry}")
        print("")

    if args.write_report:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"JSON report written to: {report_file}")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
EOF

cat > "$TOOLS_DIR/run_docs_architecture_guard.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
DOCS_ROOT="${2:-docs/live-scene-composer}"

python "$REPO_ROOT/tools/live-scene-composer/validate_docs_architecture_guard.py" \
  --repo-root "$REPO_ROOT" \
  --docs-root "$DOCS_ROOT" \
  --write-report
EOF

cat > "$TOOLS_DIR/run_docs_architecture_guard.bat" <<'EOF'
@echo off
setlocal

set REPO_ROOT=%1
if "%REPO_ROOT%"=="" set REPO_ROOT=.

set DOCS_ROOT=%2
if "%DOCS_ROOT%"=="" set DOCS_ROOT=docs\live-scene-composer

python "%REPO_ROOT%\tools\live-scene-composer\validate_docs_architecture_guard.py" --repo-root "%REPO_ROOT%" --docs-root "%DOCS_ROOT%" --write-report

endlocal
EOF

echo "[OK] Generated architecture-doc guard artifacts:"
echo "  - $DOCS_DIR/41_ARCHITECTURE_GUARD_DOC_RULES.md"
echo "  - $TOOLS_DIR/validate_docs_architecture_guard.py"
echo "  - $TOOLS_DIR/run_docs_architecture_guard.sh"
echo "  - $TOOLS_DIR/run_docs_architecture_guard.bat"