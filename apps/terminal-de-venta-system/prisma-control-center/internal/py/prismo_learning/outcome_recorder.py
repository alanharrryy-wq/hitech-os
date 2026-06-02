"""Record local feedback outcomes into episodic and procedural memory."""
from __future__ import annotations
from typing import Any
from .clock import now_iso
from .feedback_schema import normalize_feedback
from .memory_store import read_store, write_store
from .hashes import stable_json_hash

MAX_EVENTS = 2000

def record_outcome(payload: dict[str, Any] | None) -> dict[str, Any]:
    norm = normalize_feedback(payload)
    event = {'id':'fb_' + stable_json_hash(norm)[:16], 'timestamp': now_iso(), **norm}
    store = read_store('feedback', {'schema_version':'1.0.0','records':[]})
    records = [r for r in store.get('records', []) if r.get('id') != event['id']]
    records.insert(0, event)
    store['records'] = records[:MAX_EVENTS]
    write_store('feedback', store)
    return {'ok': True, 'status': 'recorded', 'feedback_id': event['id'], 'outcome': norm['outcome'], 'read_only': True, 'mutation_allowed': False}
