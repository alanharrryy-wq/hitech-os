#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Autofix Bridge executor.

Runs only conservative, allowlisted, declarative proposals and persists:
- reports/findings/fix_execution.*
- reports/verification/before_after_verification.*
"""

import json
from pathlib import Path
from typing import Any

from capatch_engine import evaluate_fix_proposal, sandbox_apply, staged_apply
from plugin_lib.fs_utils import atomic_write_text, ensure_dir

PLUGIN_ID = 'fixer.safe-runtime-actions'
PLUGIN_VERSION = '6.0.0'
PLUGIN_DESCRIPTION = 'Ejecuta staged_apply/sandbox_apply del Autofix Bridge sobre proposals allowlisted.'
PLUGIN_MIN_RUNTIME = '6.0.0'
PLUGIN_KIND = 'fixer'
PLUGIN_PHASE = 'fix'
PLUGIN_OUTPUTS = [
    'reports/findings/fix_execution.json',
    'reports/findings/fix_execution.md',
    'reports/verification/before_after_verification.json',
    'reports/verification/before_after_verification.md',
]
MAX_FIXES = 2



def register(api):
    api.register_fixer(run_fixers)



def _to_rel_report(path_value: Path, base_dir: Path) -> str:
    try:
        return path_value.resolve().relative_to(base_dir.resolve()).as_posix()
    except Exception:
        return str(path_value.resolve())



def _write_json(path_value: Path, payload: Any) -> None:
    atomic_write_text(path_value, json.dumps(payload, indent=2, ensure_ascii=False) + '\n')



def _render_fix_md(payload: dict[str, Any]) -> str:
    lines = ['# Fix execution', '']
    lines.append(f"- execution_mode: `{payload.get('execution_mode')}`")
    lines.append(f"- selected_count: `{payload.get('selected_count')}`")
    lines.append(f"- applied_count: `{payload.get('applied_count')}`")
    lines.append(f"- blocked_count: `{payload.get('blocked_count')}`")
    lines.append('')
    lines.append('## Proposals')
    lines.append('')
    for row in list(payload.get('results') or []):
        lines.append(f"- `{row.get('proposal_id')}` family=`{row.get('family')}` status=`{row.get('execution_status')}` dry_run=`{row.get('dry_run')}`")
        lines.append(f"  - applicable: `{row.get('applicability', {}).get('ok')}`")
        lines.append(f"  - sandbox: `{(row.get('sandbox') or {}).get('status', 'skipped')}` / `{(row.get('sandbox') or {}).get('execution_status', 'n/a')}`")
        lines.append(f"  - required_verifiers: `{row.get('required_verifiers')}`")
        if row.get('rollback_decision'):
            lines.append(f"  - rollback_decision: `{row.get('rollback_decision')}`")
        if row.get('command_results'):
            for command_row in row['command_results']:
                lines.append(f"    - command: `{command_row.get('command')}` rc=`{command_row.get('returncode')}` allowlisted=`{command_row.get('allowlisted')}`")
    lines.append('')
    return '\n'.join(lines)



def _render_verify_md(payload: dict[str, Any]) -> str:
    lines = ['# Before / after verification', '']
    for row in list(payload.get('results') or []):
        lines.append(f"## {row.get('proposal_id')}")
        lines.append('')
        lines.append(f"- family: `{row.get('family')}`")
        lines.append(f"- execution_status: `{row.get('execution_status')}`")
        lines.append(f"- sandbox_status: `{(row.get('sandbox') or {}).get('status', 'skipped')}` / `{(row.get('sandbox') or {}).get('execution_status', 'n/a')}`")
        lines.append('')
        lines.append('### Verifier results')
        lines.append('')
        verifier_rows = list(row.get('verifier_results') or []) + list(row.get('synthetic_verifier_results') or [])
        if not verifier_rows:
            lines.append('- No verifier results.')
        else:
            for verifier in verifier_rows:
                status = 'PASS' if verifier.get('ok') else 'FAIL'
                lines.append(f"- **{status}** `{verifier.get('verifier_id')}` {verifier.get('title')}")
                detail = str(verifier.get('detail') or '').strip()
                if detail:
                    lines.append(f'  - {detail}')
        lines.append('')
    return '\n'.join(lines)



def _proposal_get(proposal: Any, name: str, default: Any = None) -> Any:
    if isinstance(proposal, dict):
        return proposal.get(name, default)
    return getattr(proposal, name, default)



def _empty_bridge_result(proposal: Any, execution_mode: str, *, execution_status: str, reason: str) -> dict[str, Any]:
    return {
        'proposal_id': str(_proposal_get(proposal, 'proposal_id', 'unknown')),
        'family': str(_proposal_get(proposal, 'family', 'general') or 'general'),
        'dry_run': execution_mode != 'apply-fixes',
        'target_files': list(_proposal_get(proposal, 'affected_paths', []) or []),
        'required_verifiers': [],
        'verifier_results': [],
        'rollback_decision': {},
        'rollback_event': None,
        'command_results': [],
        'operation_results': [],
        'preview': {'messages': [reason], 'diff_summary': {}},
        'execution_status': execution_status,
        'execution_ok': False,
        'verification_ok': False,
        'command_ok': True,
        'operation_ok': True,
        'rolled_back': False,
        'summary': reason,
    }



def _sandbox_allows_live_apply(execution_mode: str, sandbox: dict[str, Any]) -> bool:
    if execution_mode != 'apply-fixes':
        return True
    if not isinstance(sandbox, dict) or sandbox.get('status') != 'ok':
        return False
    if sandbox.get('rollback_event'):
        return False
    return bool(sandbox.get('execution_ok', False))



def _synthetic_verifier_rows(bridge_result: dict[str, Any], execution_mode: str) -> list[dict[str, Any]]:
    proposal_id = str(bridge_result.get('proposal_id') or 'unknown')
    sandbox = bridge_result.get('sandbox') if isinstance(bridge_result.get('sandbox'), dict) else {}
    rows: list[dict[str, Any]] = []
    if execution_mode == 'apply-fixes':
        sandbox_ok = sandbox.get('status') == 'ok' and bool(sandbox.get('execution_ok', False)) and not bool(sandbox.get('rollback_event'))
        rows.append(
            {
                'verifier_id': f'{PLUGIN_ID}.sandbox.{proposal_id}',
                'ok': sandbox_ok,
                'title': f'Sandbox gate: {proposal_id}',
                'detail': f"status={sandbox.get('status', 'skipped')} execution_status={sandbox.get('execution_status', 'n/a')} rollback={bool(sandbox.get('rollback_event'))}",
                'source_plugin': PLUGIN_ID,
                'verification_class': 'autofix-sandbox',
            }
        )
    rows.append(
        {
            'verifier_id': f'{PLUGIN_ID}.execution.{proposal_id}',
            'ok': bool(bridge_result.get('execution_ok', False)),
            'title': f'Autofix execution summary: {proposal_id}',
            'detail': f"status={bridge_result.get('execution_status')} rollback={bool(bridge_result.get('rollback_event'))}",
            'source_plugin': PLUGIN_ID,
            'verification_class': 'autofix-execution',
            'metrics': {
                'execution_status': bridge_result.get('execution_status'),
                'verification_ok': bool(bridge_result.get('verification_ok', False)),
                'command_ok': bool(bridge_result.get('command_ok', False)),
                'operation_ok': bool(bridge_result.get('operation_ok', False)),
            },
        }
    )
    return rows



def run_fixers(session, fix_proposals, verification_results, **kwargs):
    execution_mode = str(getattr(session, 'execution_mode', '') or '')
    target_root = Path(getattr(session, 'target_path', getattr(session, 'root_dir', '.'))).resolve()
    reports_root = ensure_dir(target_root / 'reports')
    findings_dir = ensure_dir(reports_root / 'findings')
    verification_dir = ensure_dir(reports_root / 'verification')

    selected = list(fix_proposals or [])[:MAX_FIXES]
    results = []
    emitted_verifications = []
    for proposal in selected:
        applicability = evaluate_fix_proposal(target_root, session, proposal)
        if not applicability.get('ok'):
            sandbox = {'status': 'skipped', 'reason': 'applicability-failed'}
            bridge_result = _empty_bridge_result(proposal, execution_mode, execution_status='blocked-applicability', reason='Applicability predicates blocked live apply.')
        elif execution_mode == 'apply-fixes':
            sandbox = sandbox_apply(target_root, proposal)
            if _sandbox_allows_live_apply(execution_mode, sandbox):
                bridge_result = staged_apply(target_root, proposal, dry_run=False)
            else:
                bridge_result = _empty_bridge_result(proposal, execution_mode, execution_status='blocked-by-sandbox', reason='Sandbox apply did not clear the live-apply gate.')
        else:
            sandbox = {'status': 'skipped', 'reason': 'preview-only'}
            bridge_result = staged_apply(target_root, proposal, dry_run=True)

        bridge_result['applicability'] = applicability
        bridge_result['sandbox'] = sandbox
        synthetic_rows = _synthetic_verifier_rows(bridge_result, execution_mode)
        bridge_result['synthetic_verifier_results'] = synthetic_rows
        results.append(bridge_result)
        emitted_verifications.extend(list(bridge_result.get('verifier_results') or []))
        emitted_verifications.extend(synthetic_rows)

    applied_count = sum(1 for item in results if item.get('execution_status') == 'applied')
    blocked_count = sum(1 for item in results if str(item.get('execution_status') or '').startswith('blocked') or str(item.get('execution_status') or '').startswith('failed') or str(item.get('execution_status') or '') == 'rolled_back')
    fix_execution_payload = {
        'execution_mode': execution_mode,
        'selected_count': len(selected),
        'applied_count': applied_count,
        'blocked_count': blocked_count,
        'results': results,
    }
    verification_payload = {
        'execution_mode': execution_mode,
        'results': results,
    }

    fix_json = findings_dir / 'fix_execution.json'
    fix_md = findings_dir / 'fix_execution.md'
    verify_json = verification_dir / 'before_after_verification.json'
    verify_md = verification_dir / 'before_after_verification.md'
    _write_json(fix_json, fix_execution_payload)
    atomic_write_text(fix_md, _render_fix_md(fix_execution_payload) + '\n')
    _write_json(verify_json, verification_payload)
    atomic_write_text(verify_md, _render_verify_md(verification_payload) + '\n')

    session.options['autofix_bridge_results'] = results
    session.options['autofix_bridge_fix_execution'] = str(fix_json)
    session.options['autofix_bridge_before_after_verification'] = str(verify_json)

    return {
        'artifacts': [
            {
                'artifact_id': 'autofix-bridge.fix-execution',
                'category': 'fixes',
                'source_plugin': PLUGIN_ID,
                'path': _to_rel_report(fix_json, target_root),
                'summary': 'Resultado detallado del staged_apply Autofix Bridge.',
                'mime_type': 'application/json',
            },
            {
                'artifact_id': 'autofix-bridge.before-after-verification',
                'category': 'verification',
                'source_plugin': PLUGIN_ID,
                'path': _to_rel_report(verify_json, target_root),
                'summary': 'Verificación before/after del Autofix Bridge.',
                'mime_type': 'application/json',
            },
        ],
        'verification_results': emitted_verifications,
        'summary': f'Autofix Bridge ejecutó {len(results)} proposal(s) en modo {execution_mode}.',
    }
