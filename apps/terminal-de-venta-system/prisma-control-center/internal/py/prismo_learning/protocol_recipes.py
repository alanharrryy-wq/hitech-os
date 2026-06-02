# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Protocol recipe catalog."""
from __future__ import annotations
from .constants import *

RECIPES = [
    {"id": "visual_qa_failure", "signals": ["playwright", "screenshot", "visual", "fail"], "protocols": [PROTOCOL_VISUAL_QA_SUMMARY, PROTOCOL_DIAGNOSTIC, PROTOCOL_EVIDENCE_TRAIL, PROTOCOL_DECISION_CHECKLIST], "reason": "Visual QA evidence or Playwright failure present."},
    {"id": "evidence_status_report", "signals": ["pass", "fail", "report", "verify"], "protocols": [PROTOCOL_EVIDENCE_TRAIL, PROTOCOL_RISK_MATRIX], "reason": "Status-bearing report evidence present."},
    {"id": "client_demo", "signals": ["cliente", "demo", "presentación", "executive"], "protocols": [PROTOCOL_EXECUTIVE_BRIEF, PROTOCOL_PUBLIC_SAFE_SUMMARY], "reason": "External/client phrasing should prefer executive summary."},
    {"id": "next_step", "signals": ["qué sigue", "next", "siguiente", "recomienda"], "protocols": [PROTOCOL_DECISION_CHECKLIST, PROTOCOL_RISK_MATRIX], "reason": "User asks for next safe action."},
    {"id": "multi_surface", "signals": ["pc", "tablet", "mobile", "sync"], "protocols": [PROTOCOL_MULTISURFACE_IMPACT, PROTOCOL_EVIDENCE_TRAIL], "reason": "Multiple surfaces mentioned."},
    {"id": "learning_graph", "signals": ["graph", "grafo", "patron", "learning", "memoria"], "protocols": [PROTOCOL_NEURAL_GRAPH, PROTOCOL_EVIDENCE_TRAIL], "reason": "Learning/memory graph requested."},
]


def recipe_catalog() -> list[dict[str, object]]:
    return [dict(item) for item in RECIPES]
