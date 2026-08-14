"""Neutrality gate for Code Atlas.

The detector intentionally contains examples of forbidden coupling patterns. Its own
source file is therefore excluded from findings; that exclusion applies only to the
detector definition, never to runtime modules.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

PATTERNS = {
    "WINDOWS_FIXED_DRIVE_REPO": re.compile(r"[A-Z]:[\\/]repos[\\/][A-Za-z0-9_.-]+", re.I),
    "WINDOWS_FIXED_OUTPUT_ROOT": re.compile(r"[A-Z]:[\\/](?:downloads?|output|artifacts?|results?)[A-Za-z0-9_.\\/-]*", re.I),
    "WINDOWS_USER_HOME": re.compile(r"[A-Z]:[\\/]Users[\\/][^\\/]+", re.I),
    "FIXED_LOCAL_URL": re.compile(r"(?:127\.0\.0\.1|localhost):\d{2,5}", re.I),
}
TEXT_SUFFIXES = {".py", ".json", ".jsonc", ".md", ".txt", ".csv", ".ts", ".tsx", ".js", ".mjs", ".mts", ".html", ".css", ".ps1", ".yaml", ".yml"}
EXCLUDED_PARTS = {"node_modules", ".git", "__pycache__", ".next", "dist", "build", "coverage"}
SELF_PATH = "src/code_atlas/core/neutrality_gate.py"


def classify(rel: str) -> str:
    normalized = rel.replace("\\", "/")
    if normalized == SELF_PATH:
        return "DETECTOR_PATTERN_DEFINITION"
    if normalized.startswith("profiles/") or normalized.endswith("NEUTRALITY_POLICY.md"):
        return "PROFILE_ALLOWED"
    if normalized.startswith("src/code_atlas/") or normalized.endswith("code-atlas.py"):
        return "CORE_SHOULD_NOT_HAVE_THIS"
    if "/reports/" in normalized or normalized.endswith(".md"):
        return "REPORT_CONTEXT_ONLY"
    if "fixture" in normalized.lower() or "example" in normalized.lower() or "/tests/" in normalized:
        return "TEST_OR_EXAMPLE_ALLOWED"
    return "NEEDS_REVIEW"


def scan_code_atlas(root: str | Path) -> Dict[str, object]:
    root = Path(root)
    findings: List[Dict[str, object]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        try:
            rel = path.relative_to(root).as_posix()
            if rel == SELF_PATH:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for name, rx in PATTERNS.items():
                if rx.search(line):
                    findings.append({
                        "file": rel,
                        "line": line_no,
                        "pattern": name,
                        "classification": classify(rel),
                        "excerpt": line.strip()[:220],
                    })
    hard_core = [item for item in findings if item["classification"] == "CORE_SHOULD_NOT_HAVE_THIS"]
    return {
        "status": "PASS_CODE_ATLAS_CORE_ENVIRONMENT_NEUTRAL" if not hard_core else "FAIL_CODE_ATLAS_CORE_HAS_LOCAL_ENV_REFERENCES",
        "hardCoreCount": len(hard_core),
        "findingCount": len(findings),
        "findings": findings,
    }
