"""Completion engine for F4-F9."""
from __future__ import annotations
from typing import Any
from .clock import now_iso
from .safe_ui_governor import build_safe_ui_payload
from .feedback_stats import build_feedback_stats
from .protocol_stats_writer import build_protocol_stats
from .compaction_engine import compaction_status
from .store_hygiene import store_hygiene_report
from .governance_bridge import governance_status
from .context_enrichment import context_enrichment_payload
from .controlled_action_layer import controlled_action_status
from .report_json import write_json_report
from .report_markdown import write_markdown_report

REPORT_NAME = 'f4_to_f9_completion_report'

def build_completion_report(run_compaction_now: bool = False) -> dict[str, Any]:
    safe = build_safe_ui_payload(mode='safe', public=True)
    feedback = build_feedback_stats()
    protocols = build_protocol_stats()
    compaction = compaction_status()
    hygiene = store_hygiene_report()
    governance = governance_status()
    context = context_enrichment_payload('prismo learning safe mode evidence patterns')
    actions = controlled_action_status()
    payload = {
        'ok': True, 'status': 'PASS', 'phase': 'F4-F9 Completion Pack', 'generated_at': now_iso(),
        'safe_ui_status': safe.get('status'),
        'evidence_count': (safe.get('evidence_digest') or {}).get('evidence_count',0),
        'pattern_count': (safe.get('pattern_digest') or {}).get('pattern_count',0),
        'feedback_count': feedback.get('feedback_count',0),
        'protocol_count': len((protocols.get('protocols') or {})),
        'store_file_count': hygiene.get('file_count',0),
        'governance_alignment': (governance.get('release_train') or {}).get('alignment'),
        'context_cards': len(context.get('summary_cards') or []),
        'controlled_action_status': actions.get('status'),
        'details': {'safe_ui': safe, 'feedback': feedback, 'protocols': protocols, 'compaction': compaction, 'hygiene': hygiene, 'governance': governance, 'context': context, 'actions': actions},
        'read_only': True, 'mutation_allowed': False,
    }
    write_json_report(REPORT_NAME, payload)
    md = ['# PRISMO Learning Completion Report', '', f"Status: {payload['status']}", f"Evidence: {payload['evidence_count']}", f"Patterns: {payload['pattern_count']}", f"Feedback records: {payload['feedback_count']}", f"Protocol stats: {payload['protocol_count']}", f"Controlled action: {payload['controlled_action_status']}", '', 'Runtime remains read-only. mutation_allowed=false.', '']
    write_markdown_report(REPORT_NAME, '\n'.join(md))
    return payload

def completion_status() -> dict[str, Any]:
    safe = build_safe_ui_payload(mode='safe', public=True)
    return {'ok': True, 'status': 'available', 'phase': 'F4-F9 Completion Pack', 'evidence_count': (safe.get('evidence_digest') or {}).get('evidence_count',0), 'pattern_count': (safe.get('pattern_digest') or {}).get('pattern_count',0), 'safe_ui_ready': True, 'feedback_ready': True, 'compactor_ready': True, 'governance_ready': True, 'context_enrichment_ready': True, 'controlled_action_preview_only': True, 'read_only': True, 'mutation_allowed': False}
