"""Resolve governance canon evidence from registry."""
from __future__ import annotations
from typing import Any
from .evidence_registry import query_evidence

def governance_canon_summary(limit: int = 25) -> dict[str, Any]:
    rows = query_evidence({'type':'governance_canon'}, limit=limit)
    return {'canon_count': len(rows), 'examples': [{'id':r.get('id'), 'status':r.get('status'), 'label':r.get('safe_source_label') or r.get('source_path')} for r in rows[:5]], 'read_only': True, 'mutation_allowed': False}
