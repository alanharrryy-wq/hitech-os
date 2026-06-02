"""Feedback statistics for procedural learning."""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Any
from .memory_store import read_store, write_store
from .clock import now_iso

def build_feedback_stats() -> dict[str, Any]:
    records = list(read_store('feedback', {'schema_version':'1.0.0','records':[]}).get('records') or [])
    by_outcome = Counter(r.get('outcome','unknown') for r in records)
    by_protocol = Counter(r.get('protocol') or 'unknown' for r in records if r.get('protocol'))
    target_stats = defaultdict(lambda: {'count':0,'useful':0,'fail':0,'noise':0})
    for r in records:
        key = r.get('target_type') or 'unknown'
        target_stats[key]['count'] += 1
        if r.get('outcome') in {'useful','pass','confirmed'}: target_stats[key]['useful'] += 1
        if r.get('outcome') == 'fail': target_stats[key]['fail'] += 1
        if r.get('outcome') == 'noise': target_stats[key]['noise'] += 1
    payload = {
        'schema_version':'1.0.0', 'generated_at': now_iso(), 'feedback_count': len(records),
        'by_outcome': dict(by_outcome), 'top_protocols': dict(by_protocol.most_common(12)),
        'target_stats': dict(target_stats), 'read_only': True, 'mutation_allowed': False,
    }
    write_store('feedback_stats', payload)
    return payload

def feedback_stats_status() -> dict[str, Any]:
    return build_feedback_stats()
