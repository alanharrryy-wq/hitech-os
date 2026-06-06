from __future__ import annotations

from typing import Any

_ALLOWED = ('exact', 'structural', 'guarded', 'transactional', 'probe-only')


def fuse_strategy_signals(candidate_scores: dict[str, float], planner_decision: dict[str, Any] | None) -> dict[str, Any]:
    planner_decision = dict(planner_decision or {})
    fused: dict[str, float] = {}
    base_scores = dict(candidate_scores or {})
    delta = dict(planner_decision.get('confidence_delta') or {})
    for strategy in _ALLOWED:
        base = float(base_scores.get(strategy, 0.0) or 0.0)
        boost = float(delta.get(strategy, 0.0) or 0.0)
        fused[strategy] = round(max(0.01, min(0.99, base + boost)), 3)
    preferred = str(planner_decision.get('preferred_strategy') or '').strip().lower() or None
    source = str(planner_decision.get('source_of_decision') or 'confidence-only')
    return {
        'candidate_scores': fused,
        'preferred_strategy': preferred,
        'source_of_decision': source,
        'planner_mode': str(planner_decision.get('planner_mode') or 'off'),
        'planner_enabled': bool(planner_decision.get('enabled', False)),
        'planner_notes': list(planner_decision.get('notes') or []),
    }
