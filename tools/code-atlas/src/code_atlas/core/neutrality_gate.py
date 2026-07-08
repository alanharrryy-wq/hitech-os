"""Neutrality gate for Code Atlas core.

Scans Code Atlas source/report files for hardcoded local environment values.
It classifies findings instead of rewriting source blindly.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List

PATTERNS = {
    "WINDOWS_REPO_ROOT": re.compile(r"F:\\repos\\hitech-os|F:/repos/hitech-os", re.I),
    "WINDOWS_OUTPUT_ROOT": re.compile(r"F:\\descargasf|F:/descargasf", re.I),
    "USER_HOME": re.compile(r"C:\\Users\\alanh|C:/Users/alanh", re.I),
    "PROJECT_SPECIFIC_APP_PATH": re.compile(r"apps[/\\]terminal-de-venta-system|terminal-de-venta-system", re.I),
    "PROJECT_DOMAIN": re.compile(r"app\.hitechrts\.com", re.I),
    "LOCAL_PORT_DEFAULT": re.compile(r"127\.0\.0\.1:(?:3000|3110|3120|3130|3140|3150|3160)|localhost:(?:3000|3110|3120|3130|3140|3150|3160)", re.I),
}
TEXT_SUFFIXES = {".py", ".json", ".jsonc", ".md", ".txt", ".csv", ".ts", ".tsx", ".js", ".mjs", ".mts", ".html", ".css", ".ps1", ".yaml", ".yml"}
EXCLUDED_PARTS = {"node_modules", ".git", "__pycache__", ".next", "dist", "build", "coverage"}


def classify(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel.startswith("profiles/") or rel.endswith("NEUTRALITY_POLICY.md"):
        return "PROFILE_ALLOWED"
    if rel.startswith("src/code_atlas/") or rel.endswith("code-atlas.py"):
        return "CORE_SHOULD_NOT_HAVE_THIS"
    if "/reports/" in rel or rel.endswith(".md"):
        return "REPORT_CONTEXT_ONLY"
    if "fixture" in rel.lower() or "example" in rel.lower() or "/tests/" in rel:
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
    hard_core = [f for f in findings if f["classification"] == "CORE_SHOULD_NOT_HAVE_THIS"]
    return {
        "status": "PASS_CODE_ATLAS_CORE_ENVIRONMENT_NEUTRAL" if not hard_core else "WARN_CODE_ATLAS_CORE_HAS_LOCAL_ENV_REFERENCES",
        "hardCoreCount": len(hard_core),
        "findingCount": len(findings),
        "findings": findings,
    }
