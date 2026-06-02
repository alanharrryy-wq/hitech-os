"""Pattern digests for safe UI."""
from __future__ import annotations
from typing import Any
from .pattern_reporter import load_patterns
from .noise_budget import take

PRIORITY_RANK = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}

def _score(p: dict[str, Any]) -> float:
    return PRIORITY_RANK.get(str(p.get('priority','')).lower(), 0) * 1000 + float(p.get('count') or p.get('evidence_count') or 0)

def pattern_digest(mode: str | None = None) -> dict[str, Any]:
    raw = load_patterns()
    patterns = list(raw.get('patterns') or [])
    patterns = sorted(patterns, key=_score, reverse=True)
    compact = []
    for p in take(patterns, 'visible_patterns', mode):
        compact.append({
            'id': p.get('id'),
            'label': p.get('label') or p.get('signal') or p.get('type'),
            'priority': p.get('priority') or 'medium',
            'count': p.get('count') or p.get('evidence_count') or 0,
            'recommended_protocols': list(p.get('recommended_protocols') or [])[:3],
        })
    return {'pattern_count': len(patterns), 'top_patterns': compact, 'read_only': True, 'mutation_allowed': False}
