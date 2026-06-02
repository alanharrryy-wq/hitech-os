"""Scoring helpers for query context enrichment."""
from __future__ import annotations
from typing import Any

def lexical_score(query: str, row: dict[str, Any]) -> float:
    q = set((query or '').lower().replace('_',' ').split())
    text = ' '.join(str(row.get(k,'')).lower() for k in ('type','status','safe_source_label','source_path','surface'))
    if not q: return 0.0
    hits = sum(1 for t in q if t and t in text)
    return hits / max(len(q), 1)

def authority_boost(row: dict[str, Any]) -> float:
    try: base = float(row.get('authority_score') or row.get('authority_weight') or row.get('confidence') or 0)
    except Exception: base = 0.0
    if str(row.get('status','')).upper() == 'PASS': base += 0.1
    if bool(row.get('metadata_only')): base -= 0.15
    return max(0.0, min(1.0, base))
