# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Manifest and report name detectors."""
from __future__ import annotations
from pathlib import Path

MANIFEST_HINTS = ("manifest", "inventory", "package", "rollback", "result", "report", "summary")
REPORT_HINTS = ("report", "verification", "verify", "diagnostic", "fail", "result", "continuation")
PLAYWRIGHT_HINTS = ("playwright", "browser", "screenshot", "trace", "video", "visual")


def is_manifest_name(name: str) -> bool:
    low = Path(name).name.lower()
    return any(h in low for h in MANIFEST_HINTS) and low.endswith((".json", ".md", ".txt", ".csv"))


def is_report_name(name: str) -> bool:
    low = Path(name).name.lower()
    return any(h in low for h in REPORT_HINTS)


def is_playwright_name(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in PLAYWRIGHT_HINTS)


def classify_name(name: str) -> dict[str, bool]:
    return {
        "manifest_like": is_manifest_name(name),
        "report_like": is_report_name(name),
        "playwright_like": is_playwright_name(name),
    }
