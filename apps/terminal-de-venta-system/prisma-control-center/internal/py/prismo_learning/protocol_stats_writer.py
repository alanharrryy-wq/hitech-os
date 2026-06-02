"""Update protocol stats using feedback and pattern evidence.

Fix1 hardens legacy store-shape handling. Previous package assumed
`protocol_stats.protocols` was always a dict, but existing stores may contain
a list of protocol names or rows. That made dict(list_of_strings) explode.
"""
from __future__ import annotations
from typing import Any
from .memory_store import read_store, write_store
from .feedback_stats import build_feedback_stats
from .clock import now_iso

DEFAULT_PROTOCOLS = [
    'diagnostic', 'evidence_trail', 'visual_qa_summary', 'decision_checklist',
    'risk_matrix', 'governance_review', 'safe_ui_summary'
]


def _empty_row() -> dict[str, Any]:
    return {'uses': 0, 'success_score': 0.5, 'last_updated': now_iso()}


def _normalize_protocol_row(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        row = dict(value)
    else:
        row = {}
    row['uses'] = int(row.get('uses') or 0)
    try:
        row['success_score'] = float(row.get('success_score') if row.get('success_score') is not None else 0.5)
    except Exception:
        row['success_score'] = 0.5
    row['success_score'] = min(0.95, max(0.1, row['success_score']))
    row.setdefault('last_updated', now_iso())
    return row


def _protocol_name_from_row(row: dict[str, Any]) -> str | None:
    for key in ('id', 'protocol', 'protocol_id', 'name', 'slug'):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalize_protocols(value: Any) -> dict[str, dict[str, Any]]:
    """Accept dict, list[str], list[dict], tuple forms, or malformed legacy data."""
    protocols: dict[str, dict[str, Any]] = {}
    if isinstance(value, dict):
        for name, row in value.items():
            if isinstance(name, str) and name.strip():
                protocols[name.strip()] = _normalize_protocol_row(row)
        return protocols
    if isinstance(value, (list, tuple, set)):
        for item in value:
            if isinstance(item, str) and item.strip():
                protocols[item.strip()] = _empty_row()
            elif isinstance(item, dict):
                name = _protocol_name_from_row(item)
                if name:
                    protocols[name] = _normalize_protocol_row(item)
            elif isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], str):
                protocols[item[0].strip()] = _normalize_protocol_row(item[1])
        return protocols
    return protocols


def build_protocol_stats() -> dict[str, Any]:
    feedback = build_feedback_stats()
    existing = read_store('protocol_stats', {'schema_version': '1.0.0', 'protocols': {}})
    protocols = _normalize_protocols(existing.get('protocols') if isinstance(existing, dict) else {})

    for p in DEFAULT_PROTOCOLS:
        row = _normalize_protocol_row(protocols.get(p))
        protocols[p] = row

    top_protocols = feedback.get('top_protocols') if isinstance(feedback, dict) else {}
    if not isinstance(top_protocols, dict):
        top_protocols = {}
    for proto, count in top_protocols.items():
        if not isinstance(proto, str) or not proto.strip():
            continue
        row = _normalize_protocol_row(protocols.get(proto.strip()))
        try:
            inc = int(count or 0)
        except Exception:
            inc = 0
        row['uses'] = int(row.get('uses') or 0) + inc
        row['success_score'] = min(0.95, max(0.1, float(row.get('success_score') or 0.5) + 0.02))
        row['last_updated'] = now_iso()
        protocols[proto.strip()] = row

    payload = {
        'schema_version': '1.0.1',
        'generated_at': now_iso(),
        'protocols': protocols,
        'read_only': True,
        'mutation_allowed': False,
        'fix1': True,
        'normalization': 'accepts dict/list/string legacy protocol stores',
    }
    write_store('protocol_stats', payload)
    return payload
