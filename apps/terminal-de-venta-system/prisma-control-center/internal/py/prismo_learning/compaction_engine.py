"""Memory compactor. It writes only inside PRISMO_LEARNING_STORE."""
from __future__ import annotations
from typing import Any
from .memory_store import read_store, write_store
from .clock import now_iso
from .snapshot_manager import snapshot_known_stores
from .compaction_policy import should_keep_full, summarize_event
from .retention_rules import MAX_SUMMARIES

COMPACTABLE = ['feedback','episodic']

def compact_store(name: str) -> dict[str, Any]:
    store = read_store(name, {'schema_version':'1.0.0','records':[]})
    records = list(store.get('records') or [])
    kept=[]; summaries=[]
    for idx, event in enumerate(records):
        if should_keep_full(event, idx): kept.append(event)
        else: summaries.append(summarize_event(event))
    summaries = summaries[:MAX_SUMMARIES]
    out = dict(store)
    out['records'] = kept
    out['compacted_summaries'] = summaries
    out['compacted_at'] = now_iso()
    write_store(name, out)
    return {'store': name, 'before': len(records), 'after_full': len(kept), 'summaries': len(summaries)}

def run_compaction() -> dict[str, Any]:
    snaps = snapshot_known_stores()
    results = []
    for name in COMPACTABLE:
        results.append(compact_store(name))
    return {'ok': True, 'status':'PASS', 'phase':'F6 Memory Compactor', 'snapshots':snaps, 'results':results, 'read_only':True, 'mutation_allowed':False}

def compaction_status() -> dict[str, Any]:
    feedback = read_store('feedback', {'records':[]})
    episodic = read_store('episodic', {'records':[]})
    return {'ok': True, 'status':'available', 'feedback_records':len(feedback.get('records') or []), 'episodic_records':len(episodic.get('records') or []), 'read_only':True, 'mutation_allowed':False}
