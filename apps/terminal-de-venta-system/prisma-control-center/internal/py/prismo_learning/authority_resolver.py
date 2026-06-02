# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""F3 authority resolver for competing evidence."""
from __future__ import annotations
from typing import Any
from .f3_engine import evidence_authority_score, rank_evidence
from .authority_store import load_authority_summary

def resolve_authority(records: list[dict[str, Any]] | None = None, base=None) -> dict[str, Any]:
    if records is None:
        auth = load_authority_summary(base); top = list(auth.get("top_evidence") or []); winner = top[0] if top else None
        return {"winning_source": winner.get("safe_source_label") if winner else "none", "winning_source_type": winner.get("type") if winner else "none", "confidence": winner.get("confidence") if winner else 0, "authority_score": winner.get("authority_score") if winner else 0, "precedence_applied": auth.get("precedence_applied") or ["evidence_type","status","confidence","authority_weight"], "candidate_count": auth.get("record_count", 0), "top_evidence": top[:10], "read_only": True, "mutation_allowed": False}
    ranked = rank_evidence(records, 20); winner = ranked[0] if ranked else None
    return {"winning_source": winner.get("safe_source_label") if winner else "none", "winning_source_type": winner.get("type") if winner else "none", "confidence": winner.get("confidence") if winner else 0, "authority_score": winner.get("authority_score") if winner else 0, "precedence_applied": ["evidence_type","status","confidence","authority_weight","freshness"], "candidate_count": len(records), "top_evidence": ranked[:10], "read_only": True, "mutation_allowed": False}
def score_record(record: dict[str, Any]) -> float:
    return evidence_authority_score(record)
