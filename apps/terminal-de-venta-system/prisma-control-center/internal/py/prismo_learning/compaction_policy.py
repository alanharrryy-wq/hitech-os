"""Policy for safe local memory compaction."""
from __future__ import annotations
from typing import Any
from .retention_rules import RECENT_FULL_EVENTS, MAX_SUMMARIES, CRITICAL_OUTCOMES

def should_keep_full(event: dict[str, Any], index: int) -> bool:
    if index < RECENT_FULL_EVENTS: return True
    if str(event.get('outcome') or '').lower() in CRITICAL_OUTCOMES: return True
    if str(event.get('event_type') or '').lower() in {'validation_fail','security_warning'}: return True
    return False

def summarize_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        'id': event.get('id'), 'timestamp': event.get('timestamp'),
        'summary': event.get('summary') or event.get('note') or event.get('outcome') or 'event',
        'target_type': event.get('target_type'), 'outcome': event.get('outcome'),
        'source_ref': event.get('target_id') or event.get('evidence_ids'),
    }
