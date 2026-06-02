# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""Pattern reporting helpers for API payloads."""
from __future__ import annotations
from typing import Any
from .memory_store import read_store

def load_patterns(base=None) -> dict[str, Any]:
    return read_store("patterns", {"schema_version": "1.2.0", "patterns": [], "read_only": True, "mutation_allowed": False}, base)
def high_priority_patterns(limit: int = 20, base=None) -> list[dict[str, Any]]:
    patterns = list(load_patterns(base).get("patterns") or [])
    rank = {"high": 3, "medium": 2, "low": 1}
    patterns.sort(key=lambda p: (rank.get(str(p.get("priority")), 0), int(p.get("count") or 0)), reverse=True)
    return patterns[:limit]
def protocol_recommendations_from_patterns(query: str = "", limit: int = 5, base=None) -> list[str]:
    q = (query or "").lower(); scores: dict[str, int] = {}
    for p in high_priority_patterns(80, base):
        weight = {"high":5,"medium":3,"low":1}.get(str(p.get("priority")), 1)
        signal = str(p.get("signal") or "").lower()
        if q and any(tok in signal for tok in q.split() if len(tok)>3): weight += 3
        for proto in p.get("recommended_protocols") or []: scores[str(proto)] = scores.get(str(proto), 0) + weight
    return [k for k,_ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]]
