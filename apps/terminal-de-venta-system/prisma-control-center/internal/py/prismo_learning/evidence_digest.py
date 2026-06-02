"""Compact evidence digests for UI."""
from __future__ import annotations
from collections import Counter
from typing import Any
from .evidence_registry import load_registry
from .public_redaction import endpoint_payload
from .noise_budget import take

STATUS_ORDER = ['FAIL','WARN','PARTIAL','PASS','UNKNOWN']

def evidence_digest(mode: str | None = None, public: bool = True) -> dict[str, Any]:
    registry = load_registry()
    records = list(registry.get('records') or [])
    by_type = Counter(str(r.get('type') or 'unknown') for r in records)
    by_status = Counter(str(r.get('status') or 'UNKNOWN').upper() for r in records)
    top = sorted(records, key=lambda r: float(r.get('authority_score') or r.get('authority_weight') or r.get('confidence') or 0), reverse=True)
    sample = []
    for r in take(top, 'visible_evidence', mode):
        sample.append({
            'id': r.get('id'), 'type': r.get('type'), 'status': r.get('status'),
            'confidence': r.get('confidence'), 'authority_score': r.get('authority_score') or r.get('authority_weight'),
            'safe_source_label': r.get('safe_source_label') or r.get('name') or r.get('source_name'),
            'metadata_only': bool(r.get('metadata_only')),
        })
    payload = {
        'evidence_count': len(records),
        'by_status': {k: by_status.get(k, 0) for k in STATUS_ORDER if by_status.get(k,0)},
        'by_type_top': dict(by_type.most_common(8)),
        'top_evidence': sample,
        'read_only': True,
        'mutation_allowed': False,
    }
    return endpoint_payload(payload, public=public)
