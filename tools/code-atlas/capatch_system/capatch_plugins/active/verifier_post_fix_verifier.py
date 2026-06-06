#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Post-fix verifier that summarizes Autofix Bridge runs."""

PLUGIN_ID = 'verifier.post-fix-verifier'
PLUGIN_VERSION = '6.0.0'
PLUGIN_DESCRIPTION = 'Resume el estado final del Autofix Bridge después del fix phase.'
PLUGIN_MIN_RUNTIME = '6.0.0'
PLUGIN_KIND = 'verifier'
PLUGIN_PHASE = 'verify'
PLUGIN_OUTPUTS = ['reports/verification/before_after_verification.json', 'reports/verification/before_after_verification.md']



def register(api):
    api.register_verifier(verify)



def verify(session, verification_results, **kwargs):
    bridge_results = list((getattr(session, 'options', {}) or {}).get('autofix_bridge_results') or [])
    rows = []
    if not bridge_results:
        return {
            'verification_results': [
                {
                    'verifier_id': f'{PLUGIN_ID}.noop',
                    'ok': True,
                    'title': 'Autofix Bridge verifier noop',
                    'detail': 'No hubo ejecuciones del Autofix Bridge para resumir en esta sesión.',
                    'source_plugin': PLUGIN_ID,
                    'verification_class': 'diagnostic',
                }
            ],
            'summary': 'Sin ejecuciones de Autofix Bridge para verificar.',
        }
    for item in bridge_results:
        verifier_rows = list(item.get('verifier_results') or []) + list(item.get('synthetic_verifier_results') or [])
        command_rows = list(item.get('command_results') or [])
        sandbox = item.get('sandbox') if isinstance(item.get('sandbox'), dict) else {}
        ok = bool(item.get('execution_ok', False))
        rows.append(
            {
                'verifier_id': f"{PLUGIN_ID}.{item.get('proposal_id')}",
                'ok': ok,
                'title': f"Post-fix summary: {item.get('proposal_id')}",
                'detail': f"family={item.get('family')} execution_status={item.get('execution_status')} sandbox={sandbox.get('status', 'skipped')} rollback={bool(item.get('rollback_event'))}",
                'source_plugin': PLUGIN_ID,
                'verification_class': 'post-fix',
                'metrics': {
                    'proposal_id': item.get('proposal_id'),
                    'family': item.get('family'),
                    'execution_status': item.get('execution_status'),
                    'verifier_count': len(verifier_rows),
                    'command_count': len(command_rows),
                    'rollback_applied': bool(item.get('rollback_event')),
                    'sandbox_status': sandbox.get('status', 'skipped'),
                },
            }
        )
    return {
        'verification_results': rows,
        'summary': f'Post-fix verifier resumió {len(rows)} execution(s) del Autofix Bridge.',
    }
