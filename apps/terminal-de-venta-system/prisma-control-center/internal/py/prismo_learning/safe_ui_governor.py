"""Safe UI Governor for PRISMO Learning.

Turns the evidence/pattern firehose into a calm, layered UI contract.
"""
from __future__ import annotations
from typing import Any
from .ui_modes import mode_contract, normalize_mode
from .evidence_digest import evidence_digest
from .pattern_digest import pattern_digest
from .graph_digest import graph_digest
from .drawer_payloads import technical_drawer_payload
from .safe_response_composer import safe_summary
from .contracts import validate_read_only_envelope

def build_safe_ui_payload(mode: str | None = 'safe', public: bool = True) -> dict[str, Any]:
    mode = normalize_mode(mode)
    mc = mode_contract(mode)
    ev = evidence_digest(mode=mode, public=public)
    pats = pattern_digest(mode=mode)
    graph = graph_digest(mode=mode)
    summary = safe_summary(ev, pats, mc)
    payload = {
        'ok': True,
        'status': 'available',
        'phase': 'F4 Safe UI Governor',
        'safe_ui': summary,
        'evidence_digest': ev,
        'pattern_digest': pats,
        'graph_digest': graph,
        'technical_drawer': {'available': True, 'default_open': False, 'endpoint': '/api/prismo/learning/technical-drawer'},
        'read_only': True,
        'mutation_allowed': False,
    }
    ok, errors = validate_read_only_envelope(payload)
    if not ok:
        payload['ok'] = False; payload['status'] = 'contract_error'; payload['contract_errors'] = errors
    return payload

def build_technical_drawer_payload(mode: str | None = 'perito', public: bool = False) -> dict[str, Any]:
    payload = technical_drawer_payload(mode=mode)
    payload.update({'ok': True, 'status': 'available', 'phase': 'F4 Safe UI Governor', 'read_only': True, 'mutation_allowed': False})
    return payload
