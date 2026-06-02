# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Automatic protocol router."""
from __future__ import annotations
from typing import Any
from .protocol_recipes import recipe_catalog
from .query_classifier import classify_query
from .constants import PROTOCOL_EVIDENCE_TRAIL, PROTOCOL_DECISION_CHECKLIST, PROTOCOL_RISK_MATRIX


def route_protocols(query: str, evidence: list[dict[str, Any]] | None = None, patterns: list[dict[str, Any]] | None = None, mode: str = "ASK") -> dict[str, Any]:
    text = (query or "") + "\n" + "\n".join(str(e.get("type", "")) + " " + str(e.get("status", "")) for e in (evidence or [])[:20])
    low = text.lower()
    selected: list[str] = []
    reasons: list[str] = []
    for recipe in recipe_catalog():
        if any(str(signal).lower() in low for signal in recipe.get("signals", [])):
            for protocol in recipe.get("protocols", []):
                if protocol not in selected:
                    selected.append(str(protocol))
            reasons.append(str(recipe.get("reason")))
    if not selected:
        selected = [PROTOCOL_EVIDENCE_TRAIL, PROTOCOL_DECISION_CHECKLIST]
        reasons.append("Fallback: general query gets evidence trail and decision checklist.")
    cls = classify_query(query)
    if cls.get("risk_words") and PROTOCOL_RISK_MATRIX not in selected:
        selected.append(PROTOCOL_RISK_MATRIX)
        reasons.append("Risk terms detected; risk matrix added.")
    confidence = min(0.95, 0.48 + 0.09 * len(selected) + 0.05 * len(reasons))
    return {"selected_protocols": selected[:6], "reason": " ".join(reasons), "confidence": round(confidence, 3), "mode": mode, "query_classification": cls}
