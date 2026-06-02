# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""PASS/FAIL detector used by classifiers, ZIP inspector and reports."""
from __future__ import annotations
import re
from typing import Any

FAIL_RE = re.compile(r"\b(FAIL|FAILED|ERROR|TRACEBACK|EXCEPTION|BLOCKED|RED|NO-LEAK SCANNER FAILED)\b", re.I)
PASS_RE = re.compile(r"\b(PASS|PASSED|GREEN|SUCCESS|OK|VERIFIED|NO-LEAK SCANNER PASSED)\b", re.I)
WARN_RE = re.compile(r"\b(WARN|WARNING|PARTIAL|DEGRADED|STALE|SKIPPED)\b", re.I)


def detect_status_from_text(text: str) -> str:
    sample = text or ""
    fail = len(FAIL_RE.findall(sample))
    passed = len(PASS_RE.findall(sample))
    warn = len(WARN_RE.findall(sample))
    if fail:
        return "FAIL"
    if passed and warn:
        return "PARTIAL"
    if passed:
        return "PASS"
    if warn:
        return "WARN"
    return "UNKNOWN"


def status_counts(text: str) -> dict[str, int]:
    return {
        "fail": len(FAIL_RE.findall(text or "")),
        "pass": len(PASS_RE.findall(text or "")),
        "warn": len(WARN_RE.findall(text or "")),
    }


def merge_status(records: list[dict[str, Any]]) -> str:
    statuses = [str(r.get("status", "UNKNOWN")).upper() for r in records]
    if "FAIL" in statuses:
        return "FAIL"
    if "PARTIAL" in statuses or "WARN" in statuses:
        return "PARTIAL"
    if "PASS" in statuses:
        return "PASS"
    return "UNKNOWN"
