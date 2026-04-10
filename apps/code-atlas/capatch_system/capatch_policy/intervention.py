#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Intervention gates aligned to the Phase 0 master spec."""

import json
from pathlib import Path
from typing import Any

from plugin_lib.fs_utils import atomic_write_text, ensure_dir
from plugin_lib.git_utils import collect_git_snapshot

from .verification_requirements import compute_required_verifiers

DEFAULT_GIT_DIRTY_FILE_SOFT_LIMIT = 40


def _proposal_payload(proposal: Any) -> dict[str, Any]:
    if isinstance(proposal, dict):
        return proposal
    return {
        'proposal_id': getattr(proposal, 'proposal_id', ''),
        'risk_level': getattr(proposal, 'risk_level', 'low'),
        'reversible': bool(getattr(proposal, 'reversible', True)),
        'affected_paths': list(getattr(proposal, 'affected_paths', []) or []),
        'commands': list(getattr(proposal, 'commands', []) or []),
    }


def evaluate_intervention_gates(session: Any, base_dir: Path) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    target_path = Path(getattr(session, 'target_path', base_dir)).resolve()
    git_snapshot = collect_git_snapshot(target_path)
    proposals = [_proposal_payload(item) for item in list(getattr(session, 'fix_proposals', []) or [])]
    affected_paths = [path for item in proposals for path in list(item.get('affected_paths', []) or [])]
    command_based = any(item.get('commands') for item in proposals)
    risk_summary = {
        'command_based': command_based,
        'touches_packaging': any(Path(path).name.lower() in {'pyproject.toml', 'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'} for path in affected_paths),
    }
    required_verifiers = compute_required_verifiers(risk_summary, affected_paths)
    checks: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []

    def add(ok: bool, title: str, detail: str, *, hard: bool = False) -> None:
        row = {'ok': bool(ok), 'title': title, 'detail': detail}
        checks.append(row)
        if hard and not ok:
            blocked_reasons.append(f'{title}: {detail}')

    add(target_path.exists(), 'Target resuelto', f'target_path={target_path}', hard=True)
    add(bool(proposals), 'Hay fix proposals', f'proposal_count={len(proposals)}', hard=True)
    add(bool((git_snapshot.get('summary') or {}).get('is_repo')), 'Git entendido', f"git_summary={(git_snapshot.get('summary') or {})}")
    add(all(bool(item.get('reversible', True)) for item in proposals) if proposals else False, 'Proposals reversibles', 'Todas las proposals candidatas deben ser reversibles para auto-apply conservador.', hard=True)

    high_risk = [item for item in proposals if str(item.get('risk_level', 'low')).lower() in {'high', 'critical'}]
    add(not high_risk, 'No hay fix proposals high-risk', f'high_risk={len(high_risk)}')

    dirty_files = int((git_snapshot.get('summary') or {}).get('dirty_file_count') or 0)
    add(dirty_files <= DEFAULT_GIT_DIRTY_FILE_SOFT_LIMIT, 'Git dirty count razonable', f'dirty_file_count={dirty_files}')

    if command_based:
        add(bool(required_verifiers), 'Matriz de verificadores resuelta', f'required_verifiers={required_verifiers}')
    else:
        add(True, 'Matriz de verificadores resuelta', f'required_verifiers={required_verifiers}')

    status = 'pass' if all(item['ok'] for item in checks) else 'caution'
    if blocked_reasons:
        status = 'fail'
    allow_apply = status != 'fail'
    risk_tier = 'safe' if status == 'pass' else 'guarded' if status == 'caution' else 'high-risk'

    payload = {
        'status': status,
        'allow_apply': allow_apply,
        'risk_tier': risk_tier,
        'checks': checks,
        'git_summary': git_snapshot.get('summary') or {},
        'required_verifiers': required_verifiers,
        'blocked_reasons': blocked_reasons,
    }

    telemetry_dir = ensure_dir(base_dir / 'reports' / 'telemetry')
    json_path = telemetry_dir / 'intervention_gates.json'
    md_path = telemetry_dir / 'intervention_gates.md'
    atomic_write_text(json_path, json.dumps(payload, indent=2, ensure_ascii=False) + '\n')

    lines = ['# Intervention gates', '', f"- status: `{status}`", f"- allow_apply: `{allow_apply}`", f"- risk_tier: `{risk_tier}`", '', '## Checks', '']
    for item in checks:
        lines.append(f"- {'PASS' if item['ok'] else 'FAIL'} {item['title']}")
        lines.append(f"  - {item['detail']}")
    lines.append('')
    lines.append('## Required verifiers')
    lines.append('')
    if not required_verifiers:
        lines.append('- No required verifiers.')
    else:
        for verifier_id in required_verifiers:
            lines.append(f'- `{verifier_id}`')
    lines.append('')
    if blocked_reasons:
        lines.append('## Blocked reasons')
        lines.append('')
        for item in blocked_reasons:
            lines.append(f'- {item}')
        lines.append('')
    atomic_write_text(md_path, '\n'.join(lines))
    return payload
