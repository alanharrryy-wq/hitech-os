# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Decision trace builder."""
from __future__ import annotations
from typing import Any
from .clock import now_iso


def build_decision_trace(query: str, route: dict[str, Any], evidence: list[dict[str, Any]], authority: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "generated_at": now_iso(),
        "query_preview": (query or "")[:500],
        "steps": [
            {"step": "classify_query", "output": route.get("query_classification")},
            {"step": "select_protocols", "output": route.get("selected_protocols")},
            {"step": "rank_evidence", "output": {"evidence_count": len(evidence)}},
            {"step": "resolve_authority", "output": authority},
            {"step": "safe_next_action", "output": "recommend_read_only_protocol_chain"},
        ],
        "read_only": True,
        "mutation_allowed": False,
    }
