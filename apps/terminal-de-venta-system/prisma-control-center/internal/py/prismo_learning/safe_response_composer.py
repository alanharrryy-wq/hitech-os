"""Compose human-first safe response payloads."""
from __future__ import annotations
from typing import Any
from .ui_copy import status_sentence, next_action

def compose_safe_cards(evidence: dict[str, Any], patterns: dict[str, Any]) -> list[dict[str, Any]]:
    by_status = evidence.get('by_status') or {}
    cards = [
        {'id':'evidence','title':'Evidencia','primary': evidence.get('evidence_count', 0), 'detail': by_status},
        {'id':'patterns','title':'Patrones','primary': patterns.get('pattern_count', 0), 'detail': patterns.get('top_patterns', [])[:3]},
        {'id':'action','title':'Siguiente acción','primary': next_action(patterns.get('top_patterns') or [], evidence.get('evidence_count', 0)).get('title'), 'detail': next_action(patterns.get('top_patterns') or [], evidence.get('evidence_count', 0))},
    ]
    return cards

def safe_summary(evidence: dict[str, Any], patterns: dict[str, Any], mode_contract: dict[str, Any]) -> dict[str, Any]:
    evc = int(evidence.get('evidence_count') or 0)
    pc = int(patterns.get('pattern_count') or 0)
    return {
        'headline': 'PRISMO Learning',
        'summary': status_sentence(evc, pc),
        'badges': ['Read-only','Evidence Vault','Authority Brain'][:3],
        'cards': compose_safe_cards(evidence, patterns),
        'mode': mode_contract.get('mode','safe'),
        'read_only': True,
        'mutation_allowed': False,
    }
