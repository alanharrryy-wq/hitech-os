"""
Lightweight validator for the mandatory UI creation path.

This is intentionally heuristic, not perfect.
It is meant to catch the most common drift patterns early.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS = [
    (r"\bsetStyleSheet\s*\(", "Hardcoded stylesheet path detected"),
    (r"\bQMainWindow\s*\(", "Raw QMainWindow composition detected"),
    (r"\bQDialog\s*\(", "Raw QDialog composition detected"),
]

REQUIRED_HINT = "VisualScreenTemplate"


def scan_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[str] = []

    for pattern, message in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            issues.append(f"{path}: {message}")

    if path.name.endswith("_screen.py") and REQUIRED_HINT not in text:
        issues.append(f"{path}: screen file does not inherit from {REQUIRED_HINT}")

    return issues


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src")
    py_files = list(root.rglob("*.py"))
    all_issues: list[str] = []

    for path in py_files:
        if "ui_foundation" in path.parts:
            continue
        all_issues.extend(scan_file(path))

    if all_issues:
        print("[FAIL] UI baseline violations found:")
        for issue in all_issues:
            print(f" - {issue}")
        return 1

    print("[OK] UI baseline validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
