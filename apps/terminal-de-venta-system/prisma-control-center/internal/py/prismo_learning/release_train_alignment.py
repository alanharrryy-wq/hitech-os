"""Release train alignment signals."""
from __future__ import annotations
from typing import Any
from .evidence_registry import query_evidence

def release_train_status(limit: int = 20) -> dict[str, Any]:
    rows = query_evidence({'type':'release_train'}, limit=limit)
    pass_count = sum(1 for r in rows if str(r.get('status')).upper() == 'PASS')
    fail_count = sum(1 for r in rows if str(r.get('status')).upper() == 'FAIL')
    return {'release_train_evidence': len(rows), 'pass': pass_count, 'fail': fail_count, 'alignment': 'needs_review' if fail_count else 'clear_or_unknown', 'read_only': True, 'mutation_allowed': False}
