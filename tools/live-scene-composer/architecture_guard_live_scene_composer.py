#!/usr/bin/env python3
"""
Live Scene Composer Architecture Guard
-------------------------------------
Self-contained guard script for boundary, docs, and dependency drift detection.

Usage:
  python architecture_guard_live_scene_composer.py --repo-root F:\repos\hitech-os
  python architecture_guard_live_scene_composer.py --repo-root . --json-out tools/live-scene-composer/_local/architecture_guard_report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional


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

CANONICAL_BOUNDARIES = [
    "console-core",
    "runtime-debug-console",
    "live-scene-composer",
    "runtime-mutation-bridge",
]

FORBIDDEN_IMPORT_PATTERNS = {
    "composer_imports_debug": [
        r"from\s+['\"][^'\"]*runtime-debug-console[^'\"]*['\"]",
        r"import\s+.*['\"][^'\"]*runtime-debug-console[^'\"]*['\"]",
    ],
    "debug_imports_composer": [
        r"from\s+['\"][^'\"]*live-scene-composer[^'\"]*['\"]",
        r"import\s+.*['\"][^'\"]*live-scene-composer[^'\"]*['\"]",
    ],
    # AGR-003 now only flags ACTIVE legacy references, not arbitrary strings.
    "legacy_core_active_refs": [
        r"from\s+['\"][^'\"]*dev-console/core[^'\"]*['\"]",
        r"import\s+.*['\"][^'\"]*dev-console/core[^'\"]*['\"]",
        r"require\s*\(\s*['\"][^'\"]*dev-console/core[^'\"]*['\"]\s*\)",
        r"from\s+['\"][^'\"]*apps/keystone/components/dev-console/core[^'\"]*['\"]",
        r"import\s+.*['\"][^'\"]*apps/keystone/components/dev-console/core[^'\"]*['\"]",
        r"require\s*\(\s*['\"][^'\"]*apps/keystone/components/dev-console/core[^'\"]*['\"]\s*\)",
    ],
    "bridge_bypass_smells": [
        r"setRuntimeState\s*\(",
        r"updateRuntimeState\s*\(",
        r"mutateRuntime\w*\s*\(",
        r"writeRuntime\w*\s*\(",
    ],
}


@dataclass
class Violation:
    rule: str
    severity: str
    message: str
    path: Optional[str] = None
    line: Optional[int] = None
    evidence: Optional[str] = None


class ProgressPrinter:
    def __init__(self) -> None:
        self.step = 0

    def log(self, message: str) -> None:
        self.step += 1
        print(f"[{self.step:02d}] {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def find_line_number(text: str, pattern: str) -> Optional[int]:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return None
    return text.count("\n", 0, match.start()) + 1


def iter_code_files(root: Path) -> Iterable[Path]:
    exts = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"}
    skip_parts = {
        ".git", "node_modules", ".next", "dist", "build", "coverage",
        ".venv", "venv", "__pycache__", "_local"
    }
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_parts for part in path.parts):
            continue
        if path.suffix.lower() in exts:
            yield path


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False


def collect_docs_root(repo_root: Path) -> Path:
    return repo_root / "docs" / "live-scene-composer"


def collect_boundary_roots(repo_root: Path) -> dict:
    candidates = {
        "composer": [
            repo_root / "live-scene-composer",
            repo_root / "apps" / "keystone" / "components" / "live-scene-composer",
            repo_root / "packages" / "live-scene-composer",
        ],
        "debug": [
            repo_root / "runtime-debug-console",
            repo_root / "apps" / "keystone" / "components" / "dev-console" / "runtime-debug-console",
            repo_root / "packages" / "runtime-debug-console",
        ],
        "tooling": [
            repo_root / "tools" / "live-scene-composer",
            repo_root / "docs" / "live-scene-composer",
        ],
    }
    resolved = {}
    for key, paths in candidates.items():
        resolved[key] = [p for p in paths if p.exists()]
    return resolved


def check_critical_docs(docs_root: Path, violations: List[Violation]) -> None:
    for name in CRITICAL_DOCS:
        path = docs_root / name
        if not path.exists():
            violations.append(Violation(
                rule="AGR-001",
                severity="error",
                message=f"Missing critical canonical doc: {name}",
                path=str(path),
            ))


def check_legacy_path(repo_root: Path, violations: List[Violation]) -> None:
    legacy_path = repo_root / "apps" / "keystone" / "components" / "dev-console" / "core"
    if legacy_path.exists():
        violations.append(Violation(
            rule="AGR-002",
            severity="error",
            message="Legacy shared-core path exists again and must not be active.",
            path=str(legacy_path),
        ))


def scan_code_import_drift(repo_root: Path, boundary_roots: dict, violations: List[Violation]) -> None:
    composer_roots = boundary_roots.get("composer", [])
    debug_roots = boundary_roots.get("debug", [])
    tooling_roots = boundary_roots.get("tooling", [])

    for path in iter_code_files(repo_root):
        text = read_text(path)

        in_composer = any(is_inside(path, root) for root in composer_roots)
        in_debug = any(is_inside(path, root) for root in debug_roots)
        in_tooling = any(is_inside(path, root) for root in tooling_roots)

        # AGR-003 only applies to ACTIVE code, not tooling/docs that merely mention the path.
        if not in_tooling:
            for pattern in FORBIDDEN_IMPORT_PATTERNS["legacy_core_active_refs"]:
                line = find_line_number(text, pattern)
                if line:
                    violations.append(Violation(
                        rule="AGR-003",
                        severity="error",
                        message="Active legacy core import/reference detected.",
                        path=str(path),
                        line=line,
                        evidence=pattern,
                    ))

        if in_debug:
            for pattern in FORBIDDEN_IMPORT_PATTERNS["debug_imports_composer"]:
                line = find_line_number(text, pattern)
                if line:
                    violations.append(Violation(
                        rule="AGR-004",
                        severity="error",
                        message="Runtime Debug Console imports Composer product logic.",
                        path=str(path),
                        line=line,
                        evidence=pattern,
                    ))

        if in_composer:
            for pattern in FORBIDDEN_IMPORT_PATTERNS["composer_imports_debug"]:
                line = find_line_number(text, pattern)
                if line:
                    violations.append(Violation(
                        rule="AGR-005",
                        severity="error",
                        message="Composer imports Runtime Debug Console product logic.",
                        path=str(path),
                        line=line,
                        evidence=pattern,
                    ))

            lower_path = str(path).replace("\\", "/").lower()
            if "runtime-mutation-bridge" not in lower_path:
                for pattern in FORBIDDEN_IMPORT_PATTERNS["bridge_bypass_smells"]:
                    line = find_line_number(text, pattern)
                    if line:
                        violations.append(Violation(
                            rule="AGR-BRIDGE-SMOKE",
                            severity="warning",
                            message="Possible runtime write bypass smell outside runtime-mutation-bridge.",
                            path=str(path),
                            line=line,
                            evidence=pattern,
                        ))


def check_index_consistency(docs_root: Path, violations: List[Violation]) -> None:
    targets = [
        docs_root / "README.md",
        docs_root / "00_TOC.md",
        docs_root / "00_READING_PATHS.md",
    ]
    critical_refs = [
        "05_SYSTEM_ARCHITECTURE.md",
        "06_SYSTEM_BOUNDARIES.md",
        "07_DOMAIN_MODEL.md",
        "10_MUTATION_MODEL.md",
        "18_RUNTIME_MUTATION_BRIDGE.md",
        "19_DEPENDENCY_POLICY.md",
        "40_ARCHITECTURAL_DECISIONS.md",
        "41_ARCHITECTURE_GUARD_DOC_RULES.md",
    ]
    for index_file in targets:
        if not index_file.exists():
            violations.append(Violation(
                rule="AGR-006",
                severity="error",
                message="Index/entry doc missing; cannot validate discoverability.",
                path=str(index_file),
            ))
            continue

        text = read_text(index_file)
        for ref in critical_refs:
            if ref not in text:
                violations.append(Violation(
                    rule="AGR-006",
                    severity="error",
                    message=f"Critical doc not referenced from index/readme: {ref}",
                    path=str(index_file),
                ))

        if index_file.name == "00_READING_PATHS.md" and "42_ARCHITECTURE_ARTIFACTS.md" not in text:
            violations.append(Violation(
                rule="AGR-006A",
                severity="warning",
                message="Reading paths missing architecture artifacts reference: 42_ARCHITECTURE_ARTIFACTS.md",
                path=str(index_file),
            ))


def check_guard_doc_boundaries(docs_root: Path, violations: List[Violation]) -> None:
    guard_doc = docs_root / "41_ARCHITECTURE_GUARD_DOC_RULES.md"
    if not guard_doc.exists():
        return
    text = read_text(guard_doc)
    for boundary in CANONICAL_BOUNDARIES:
        if boundary not in text:
            violations.append(Violation(
                rule="AGR-007",
                severity="error",
                message=f"Guard rules doc does not mention canonical boundary: {boundary}",
                path=str(guard_doc),
            ))


def build_report(repo_root: Path, docs_root: Path, violations: List[Violation]) -> dict:
    errors = [v for v in violations if v.severity == "error"]
    warnings = [v for v in violations if v.severity == "warning"]
    return {
        "repo_root": str(repo_root),
        "docs_root": str(docs_root),
        "status": "FAIL" if errors else "PASS",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "violations": [asdict(v) for v in violations],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Live Scene Composer architecture guard")
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--json-out", help="Optional JSON report output path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    docs_root = collect_docs_root(repo_root)
    boundary_roots = collect_boundary_roots(repo_root)
    progress = ProgressPrinter()

    if not repo_root.exists():
        print(f"Repo root does not exist: {repo_root}", file=sys.stderr)
        return 2

    violations: List[Violation] = []

    progress.log(f"Repo root: {repo_root}")
    progress.log(f"Docs root: {docs_root}")

    progress.log("Checking critical canonical docs")
    check_critical_docs(docs_root, violations)

    progress.log("Checking legacy shared-core path drift")
    check_legacy_path(repo_root, violations)

    progress.log("Scanning imports and boundary drift")
    scan_code_import_drift(repo_root, boundary_roots, violations)

    progress.log("Checking index and reading-path discoverability")
    check_index_consistency(docs_root, violations)

    progress.log("Checking guard doc canonical boundary names")
    check_guard_doc_boundaries(docs_root, violations)

    report = build_report(repo_root, docs_root, violations)

    if args.json_out:
        json_out = Path(args.json_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        progress.log(f"Wrote JSON report: {json_out}")

    print("\n" + "=" * 72)
    print("LIVE SCENE COMPOSER ARCHITECTURE GUARD")
    print("=" * 72)
    print(f"Status   : {report['status']}")
    print(f"Errors   : {report['error_count']}")
    print(f"Warnings : {report['warning_count']}")
    print("=" * 72)

    for item in report["violations"]:
        loc = f"{item['path']}:{item['line']}" if item.get("path") and item.get("line") else item.get("path", "")
        sev = item["severity"].upper()
        print(f"[{sev}] {item['rule']} {item['message']}")
        if loc:
            print(f"        at {loc}")
        if item.get("evidence"):
            print(f"        evidence: {item['evidence']}")
    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
