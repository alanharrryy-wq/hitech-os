"""Feedback payload schema normalization."""
from __future__ import annotations
from typing import Any
ALLOWED_OUTCOMES = {'useful','not_useful','pass','fail','partial','noise','confirmed'}
ALLOWED_TARGETS = {'protocol','evidence','pattern','recommendation','report','unknown'}

def normalize_feedback(payload: dict[str, Any] | None) -> dict[str, Any]:
    p = dict(payload or {})
    outcome = str(p.get('outcome') or p.get('result') or 'confirmed').lower()
    if outcome not in ALLOWED_OUTCOMES: outcome = 'confirmed'
    target_type = str(p.get('target_type') or 'unknown').lower()
    if target_type not in ALLOWED_TARGETS: target_type = 'unknown'
    return {
        'target_type': target_type,
        'target_id': str(p.get('target_id') or p.get('id') or '')[:160],
        'outcome': outcome,
        'protocol': str(p.get('protocol') or '')[:120],
        'note': str(p.get('note') or '')[:500],
        'confidence_delta': float(p.get('confidence_delta') or 0),
        'metadata': {k:v for k,v in (p.get('metadata') or {}).items() if isinstance(k,str)} if isinstance(p.get('metadata'), dict) else {},
    }
