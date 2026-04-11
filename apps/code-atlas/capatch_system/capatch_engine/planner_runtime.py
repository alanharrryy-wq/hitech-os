from __future__ import annotations

from typing import Any

from .planner_input import build_planner_input

_ALLOWED = ('exact', 'structural', 'guarded', 'transactional', 'probe-only')


def run_planner_runtime(ctx: Any, preflight_report: Any, risk_summary: dict[str, Any], operations: list[Any]) -> dict[str, Any]:
    planner_mode = str(getattr(ctx, 'planner_mode', 'off') or 'off').lower()
    planner_input = build_planner_input(preflight_report, risk_summary, operations)
    blocked_reasons = list(planner_input.get('blocked_reasons') or [])
    if planner_mode not in {'off', 'advisory'}:
        planner_mode = 'off'
    if planner_mode == 'off':
        return {
            'planner_mode': 'off',
            'enabled': False,
            'preferred_strategy': None,
            'confidence_delta': {},
            'source_of_decision': 'planner:off',
            'planner_input': planner_input,
            'notes': ['planner disabled'],
        }

    target_file_count = int(planner_input.get('target_file_count', 0) or 0)
    fragile_anchor_count = int(planner_input.get('fragile_anchor_count', 0) or 0)
    exact_anchor_count = int(planner_input.get('exact_anchor_count', 0) or 0)
    structural_candidate_files = list(planner_input.get('structural_candidate_files') or [])
    risk_level = str(planner_input.get('risk_level') or 'low').lower()

    preferred = 'guarded'
    notes: list[str] = []
    if blocked_reasons:
        preferred = 'probe-only'
        notes.append('planner saw blockers and suggested probe-only')
    elif target_file_count > 1:
        preferred = 'transactional'
        notes.append('planner prefers transactional for multi-file change sets')
    elif structural_candidate_files:
        preferred = 'structural'
        notes.append('planner detected structural surface candidates')
    elif exact_anchor_count > 0 and fragile_anchor_count == 0:
        preferred = 'exact'
        notes.append('planner saw exact anchors with low fragility')
    elif fragile_anchor_count > 0 or risk_level in {'medium', 'high', 'critical'}:
        preferred = 'guarded'
        notes.append('planner prefers guarded mode for fragile anchors or elevated risk')

    confidence_delta = {key: 0.0 for key in _ALLOWED}
    if preferred in confidence_delta:
        confidence_delta[preferred] = 0.07
    return {
        'planner_mode': 'advisory',
        'enabled': True,
        'preferred_strategy': preferred,
        'confidence_delta': confidence_delta,
        'source_of_decision': 'planner:advisory',
        'planner_input': planner_input,
        'notes': notes,
    }
