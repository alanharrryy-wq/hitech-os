# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""Recommendation engine powered by F3 pattern and authority stores."""
from __future__ import annotations
from typing import Any
from .evidence_registry import query_evidence
from .authority_resolver import resolve_authority
from .pattern_reporter import protocol_recommendations_from_patterns, high_priority_patterns
from .protocol_router import route_protocols

def recommend(query: str, base=None) -> dict[str, Any]:
    rows = query_evidence({}, base=base, limit=120)
    routed = route_protocols(query, rows)
    merged = []
    for p in protocol_recommendations_from_patterns(query, 5, base) + list(routed.get("selected_protocols") or []):
        if p not in merged: merged.append(p)
    patterns = high_priority_patterns(8, base)
    confidence = max(float(routed.get("confidence") or 0.0), min(.96, .58 + .03*len(patterns)))
    return {"ok": True, "status": "available", "query": query, "selected_protocols": merged[:8] or ["evidence_trail", "decision_checklist"], "reason": "F3 combined protocol router, mined patterns and authority-ranked evidence.", "confidence": round(confidence, 4), "authority": resolve_authority(rows, base=base), "top_patterns": patterns, "evidence_count_considered": len(rows), "read_only": True, "mutation_allowed": False}
