# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Confidence, authority and priority scoring."""
from __future__ import annotations
from typing import Any

TYPE_AUTHORITY = {
    "governance_canon": 0.92,
    "prismo_verify_report": 0.88,
    "playwright_evidence": 0.84,
    "query_type_guard": 0.82,
    "dependency_atlas": 0.74,
    "repo_inventory": 0.66,
    "downloads_inventory": 0.58,
    "unknown_prismo_related": 0.32,
}
STATUS_CONFIDENCE = {"PASS": 0.86, "FAIL": 0.82, "PARTIAL": 0.62, "WARN": 0.56, "UNKNOWN": 0.34}
FRESHNESS_BOOST = {"fresh_hour": 0.1, "fresh_day": 0.08, "fresh_week": 0.05, "month": 0.02, "quarter": -0.02, "old": -0.08, "unknown": -0.04}


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def evidence_confidence(record: dict[str, Any]) -> float:
    etype = str(record.get("type") or "unknown_prismo_related")
    status = str(record.get("status") or "UNKNOWN").upper()
    freshness = str(record.get("freshness") or "unknown")
    base = TYPE_AUTHORITY.get(etype, 0.38) * 0.58 + STATUS_CONFIDENCE.get(status, 0.34) * 0.32
    base += FRESHNESS_BOOST.get(freshness, 0.0)
    if record.get("metadata_only"):
        base -= 0.09
    if record.get("warnings"):
        base -= min(0.12, len(record.get("warnings") or []) * 0.025)
    return round(clamp(base), 3)


def authority_weight(record: dict[str, Any]) -> float:
    etype = str(record.get("type") or "unknown_prismo_related")
    weight = TYPE_AUTHORITY.get(etype, 0.35)
    if record.get("status") == "FAIL":
        weight += 0.04  # failure evidence is important even if unpleasant.
    return round(clamp(weight), 3)


def priority_from_status(status: str) -> str:
    s = str(status or "UNKNOWN").upper()
    if s == "FAIL": return "high"
    if s in {"PARTIAL", "WARN"}: return "medium"
    if s == "PASS": return "low"
    return "unknown"
