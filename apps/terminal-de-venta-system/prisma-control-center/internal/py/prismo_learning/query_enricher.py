"""Enrich a user query using local evidence and patterns."""
from __future__ import annotations
from typing import Any
from .evidence_registry import load_registry
from .pattern_reporter import high_priority_patterns
from .context_scoring import lexical_score, authority_boost
from .recommendation_engine import recommend

def enrich_query_context(query: str, limit: int = 8) -> dict[str, Any]:
    records = list(load_registry().get('records') or [])
    scored = []
    for r in records:
        s = lexical_score(query, r) + authority_boost(r)
        if s > 0: scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    evidence = [{'id':r.get('id'), 'type':r.get('type'), 'status':r.get('status'), 'score':round(s,3), 'label':r.get('safe_source_label') or r.get('source_path')} for s,r in scored[:limit]]
    return {'ok': True, 'status':'available', 'query':query, 'evidence': evidence, 'patterns': high_priority_patterns(5), 'recommendation': recommend(query), 'read_only': True, 'mutation_allowed': False}
