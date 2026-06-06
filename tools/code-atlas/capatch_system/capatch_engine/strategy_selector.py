from __future__ import annotations

from typing import Any

from capatch_ops.registry import strategy_capabilities, summarize_operation_families
from capatch_policy.confidence import score_patch_strategy
from capatch_policy.strategy_fusion import fuse_strategy_signals

from .planner_runtime import run_planner_runtime

_ALLOWED_STRATEGIES = ('exact', 'structural', 'guarded', 'transactional', 'probe-only')
_TIE_BREAK_ORDER = {name: index for index, name in enumerate(_ALLOWED_STRATEGIES)}


def _planner_hint_from_ctx(ctx: Any) -> Any | None:
    for attr in ('planner_hint', 'ai_strategy_hint', 'strategy_hint'):
        value = getattr(ctx, attr, None)
        if value:
            return value
    return None


def _planner_mode_from_ctx(ctx: Any) -> str:
    return str(getattr(ctx, 'planner_mode', 'off') or 'off').lower()


def _choose_strategy(candidate_scores: dict[str, float]) -> str:
    if not candidate_scores:
        return 'guarded'
    return sorted(candidate_scores.items(), key=lambda item: (-float(item[1]), _TIE_BREAK_ORDER.get(item[0], 99)))[0][0]


def select_patch_strategy(ctx: Any, preflight_report: Any, operations: list[Any], risk_summary: dict[str, Any]) -> dict[str, Any]:
    planner_hint = _planner_hint_from_ctx(ctx)
    planner_mode = _planner_mode_from_ctx(ctx)
    confidence = score_patch_strategy(preflight_report, risk_summary, list(operations or []), planner_hint=planner_hint)
    planner_decision = run_planner_runtime(ctx, preflight_report, risk_summary, list(operations or []))
    fusion = fuse_strategy_signals(dict(confidence.get('candidate_scores') or {}), planner_decision)
    candidate_scores = dict(fusion.get('candidate_scores') or confidence.get('candidate_scores') or {})
    strategy_hints = dict(getattr(preflight_report, 'strategy_hints', {}) or {})
    blockers = list((risk_summary or {}).get('blocked_reasons') or [])
    reasons: list[str] = []

    if blockers or strategy_hints.get('force_probe_only'):
        selected = 'probe-only'
        reasons.append('preflight reported blockers or path violations')
    else:
        selected = _choose_strategy(candidate_scores)

    if selected == 'exact':
        reasons.append('single-file anchor-driven patch remains stable enough for literal execution')
    elif selected == 'structural':
        reasons.append('typescript/javascript surface and anchor fragility suggest structural handling next')
    elif selected == 'guarded':
        reasons.append('risk or anchor fragility suggests guarded execution with review')
    elif selected == 'transactional':
        reasons.append('multi-file or batch-heavy change deserves transactional coordination')
    else:
        reasons.append('inspect only before mutating because confidence is too low or blockers exist')

    if fusion.get('planner_enabled'):
        reasons.append(f"planner foundation advisory nudged strategy toward: {fusion.get('preferred_strategy')}")

    capabilities = strategy_capabilities().get(selected, {'advisory_only': False, 'families': []})
    operation_families = summarize_operation_families(operations)
    ordered_candidates = [
        {'strategy': key, 'score': value}
        for key, value in sorted(candidate_scores.items(), key=lambda item: (-float(item[1]), _TIE_BREAK_ORDER.get(item[0], 99)))
    ]
    return {
        'selected_strategy': selected,
        'selected_score': float(candidate_scores.get(selected, 0.0) or 0.0),
        'candidate_ranking': ordered_candidates,
        'operation_families': operation_families,
        'planner_stub': {'enabled': False, 'hint': None, 'source': None},
        'planner_mode': planner_mode,
        'planner_decision': dict(planner_decision or {}),
        'source_of_decision': str(fusion.get('source_of_decision') or 'confidence-only'),
        'anchor_confidence': float(confidence.get('anchor_confidence', 0.0) or 0.0),
        'syntax_confidence': float(confidence.get('syntax_confidence', 0.0) or 0.0),
        'semantic_confidence': float(confidence.get('semantic_confidence', 0.0) or 0.0),
        'batch_risk': float(confidence.get('batch_risk', 0.0) or 0.0),
        'rollback_readiness': float(confidence.get('rollback_readiness', 0.0) or 0.0),
        'overall_confidence': float(confidence.get('overall_confidence', 0.0) or 0.0),
        'recommended_guardrails': list(confidence.get('recommended_guardrails') or []),
        'requires_future_executor': bool(capabilities.get('advisory_only', False)),
        'executor_capabilities': capabilities,
        'advisory_only': bool(capabilities.get('advisory_only', False)),
        'reasons': reasons,
    }
