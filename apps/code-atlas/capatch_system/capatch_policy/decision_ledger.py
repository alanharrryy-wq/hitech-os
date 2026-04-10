#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Decision ledger and support bundle v2."""

import json
from pathlib import Path
from typing import Any

from plugin_lib.diagnostic_rules import sort_finding_rows
from plugin_lib.fs_utils import atomic_write_text, ensure_dir


def _to_rows(findings: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for item in list(findings or []):
        rows.append(
            {
                'finding_id': getattr(item, 'finding_id', ''),
                'severity': getattr(item, 'severity', 'info'),
                'title': getattr(item, 'title', ''),
                'detail': getattr(item, 'detail', ''),
                'source_plugin': getattr(item, 'source_plugin', ''),
                'confidence': getattr(item, 'confidence_score', getattr(item, 'confidence', 0.0)),
            }
        )
    return sort_finding_rows(rows, limit=12)


def write_operator_trust_outputs(base_dir: Path, session: Any) -> dict[str, str]:
    base_dir = Path(base_dir).resolve()
    reports_root = ensure_dir(base_dir / 'reports')
    bundles_dir = ensure_dir(reports_root / 'bundles')
    ledger_dir = ensure_dir(reports_root / 'decision_ledger')
    confidence_summary_path = Path(str((getattr(session, 'options', {}) or {}).get('confidence_summary_path') or ''))
    confidence_summary = {}
    if confidence_summary_path.exists():
        try:
            confidence_summary = json.loads(confidence_summary_path.read_text(encoding='utf-8', errors='replace'))
        except Exception:
            confidence_summary = {}
    noisy = list((getattr(session, 'options', {}) or {}).get('noise_artifacts') or [])
    gates = (getattr(session, 'options', {}) or {}).get('intervention_gates') or {}
    finding_rows = _to_rows(list(getattr(session, 'findings', []) or []))
    proposals = []
    for item in list(getattr(session, 'fix_proposals', []) or []):
        proposals.append(
            {
                'proposal_id': getattr(item, 'proposal_id', ''),
                'title': getattr(item, 'title', ''),
                'risk_level': getattr(item, 'risk_level', 'low'),
                'risk_tier': getattr(item, 'risk_tier', 'guarded'),
                'confidence_score': getattr(item, 'confidence_score', None),
                'confidence_reason': getattr(item, 'confidence_reason', ''),
                'commands': list(getattr(item, 'commands', []) or []),
                'verification_steps': list(getattr(item, 'verification_steps', []) or []),
            }
        )
    patch_history_path = reports_root / 'patch_history' / 'index.json'
    patch_history = {}
    if patch_history_path.exists():
        try:
            patch_history = json.loads(patch_history_path.read_text(encoding='utf-8', errors='replace'))
        except Exception:
            patch_history = {}
    payload = {
        'session_id': getattr(session, 'session_id', None),
        'execution_mode': getattr(session, 'execution_mode', None),
        'target_path': getattr(session, 'target_path', None),
        'app_kind': getattr(session, 'app_kind', None),
        'decision_ledger': {
            'what_it_saw': finding_rows,
            'what_it_discarded': noisy,
            'what_it_concluded': [row.get('title') for row in finding_rows[:5]],
            'why_this_fix': [{'proposal_id': item['proposal_id'], 'confidence_reason': item['confidence_reason']} for item in proposals[:5]],
            'intervention_gates': gates,
            'confidence_summary_ref': str(confidence_summary_path) if confidence_summary_path.exists() else None,
            'patch_history_ref': str(patch_history_path) if patch_history_path.exists() else None,
        },
        'confidence_summary': confidence_summary,
        'fix_proposals': proposals,
        'verification_results': [
            {
                'verifier_id': getattr(item, 'verifier_id', ''),
                'ok': getattr(item, 'ok', False),
                'title': getattr(item, 'title', ''),
                'detail': getattr(item, 'detail', ''),
            }
            for item in list(getattr(session, 'verification_results', []) or [])
        ],
        'patch_history': patch_history,
    }
    bundle_json = bundles_dir / 'support_bundle_v2.json'
    bundle_md = bundles_dir / 'support_bundle_v2.md'
    atomic_write_text(bundle_json, json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    lines = ['# Support Bundle v2', '', f"- session_id: `{payload['session_id']}`", f"- execution_mode: `{payload['execution_mode']}`", f"- target_path: `{payload['target_path']}`", '', '## Priority findings', '']
    for row in finding_rows:
        lines.append(f"- **{row.get('severity','info').upper()}** {row.get('title')} | confidence=`{row.get('confidence')}`")
        detail = str(row.get('detail') or '').strip()
        if detail:
            lines.append(f'  - {detail}')
    lines.append('')
    lines.append('## Decision Ledger')
    lines.append('')
    lines.append('### What it discarded')
    lines.append('')
    if not noisy:
        lines.append('- No noisy artifacts discarded.')
    else:
        for item in noisy[:20]:
            lines.append(f"- `{item.get('artifact_id')}` -> `{item.get('reason')}`")
    lines.append('')
    lines.append('### Intervention gates')
    lines.append('')
    if not gates:
        lines.append('- No intervention gates recorded.')
    else:
        lines.append(f"- status: `{gates.get('status')}`")
        lines.append(f"- risk_tier: `{gates.get('risk_tier')}`")
        for item in gates.get('checks', [])[:12]:
            lines.append(f"  - {'PASS' if item.get('ok') else 'FAIL'} {item.get('title')}: {item.get('detail')}")
    lines.append('')
    lines.append('### Fix proposals')
    lines.append('')
    if not proposals:
        lines.append('- No fix proposals.')
    else:
        for item in proposals[:10]:
            lines.append(f"- `{item.get('proposal_id')}` {item.get('title')} | tier=`{item.get('risk_tier')}` score=`{item.get('confidence_score')}`")
            lines.append(f"  - {item.get('confidence_reason')}")
    lines.append('')
    atomic_write_text(bundle_md, '\n'.join(lines))
    ledger_md = ledger_dir / f"{payload['session_id'] or 'session'}_decision_ledger.md"
    atomic_write_text(ledger_md, '\n'.join(lines))
    return {'bundle_json': str(bundle_json), 'bundle_md': str(bundle_md), 'decision_ledger_md': str(ledger_md)}
