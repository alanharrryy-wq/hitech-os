#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Confidence scoring and cross-signal helpers for operator trust layer."""

import json
from pathlib import Path
from typing import Any

from plugin_lib.diagnostic_rules import severity_rank
from plugin_lib.fs_utils import atomic_write_text, ensure_dir

from ._helpers import get_attr_or_key, set_attr_or_key

_TEXT_EXACT_OPS = {
    'ReplaceExactOnce',
    'ReplaceExactMany',
    'EnsureReplaceExactOnce',
    'ReplaceNearestExact',
    'MoveBlockExactOnce',
    'ReplaceBetweenExactAnchors',
    'DeleteBetweenExactAnchors',
    'DeleteExactOnce',
    'EnsureInsertAfterExact',
    'EnsureInsertBeforeExact',
    'InsertAfterExact',
    'InsertBeforeExact',
}
_REGEX_OPS = {'DeleteRegexMany', 'DeleteRegexOnce', 'ReplaceRegexOnce', 'ReplaceRegexMany', 'ReplaceRegexCount', 'EnsureReplaceRegexOnce', 'AssertRegexCount'}
_SEMANTIC_OPS = {'SetJsonValue', 'DeleteJsonKey', 'MergeJsonObject', 'SetYamlValue', 'DeleteYamlKey', 'SetTomlValue', 'EnsurePythonImport', 'DeletePythonImport', 'SetPythonConstant', 'InsertPythonFunctionArg'}
_ALLOWED_STRATEGIES = ('exact', 'structural', 'guarded', 'transactional', 'probe-only')


def _clamp(value: float, low: float = 0.05, high: float = 0.99) -> float:
    return max(low, min(high, round(value, 3)))


def _related_support(findings: list[Any], current: Any) -> list[str]:
    support = []
    current_tags = {str(item) for item in (getattr(current, 'tags', []) or [])}
    for item in findings:
        if item is current:
            continue
        if str(getattr(item, 'category', '')) == str(getattr(current, 'category', '')):
            support.append(str(getattr(item, 'finding_id', '')))
        elif current_tags.intersection({str(token) for token in (getattr(item, 'tags', []) or [])}):
            support.append(str(getattr(item, 'finding_id', '')))
    return sorted({item for item in support if item})[:6]


def _annotate_finding(findings: list[Any], finding: Any) -> None:
    base = float(getattr(finding, 'confidence', 0.0) or 0.0)
    evidence_refs = list(getattr(finding, 'evidence_refs', []) or [])
    contradictions = []
    if severity_rank(getattr(finding, 'severity', 'info')) >= 2 and not evidence_refs:
        contradictions.append('finding severo sin evidence_refs explícitos')
    support = _related_support(findings, finding)
    score = base
    score += min(0.21, len(evidence_refs) * 0.07)
    score += min(0.18, len(support) * 0.06)
    score -= len(contradictions) * 0.10
    confidence_score = _clamp(score or 0.35)
    set_attr_or_key(finding, 'evidence_count', len(evidence_refs))
    set_attr_or_key(finding, 'cross_signal_support', support)
    set_attr_or_key(finding, 'contradictions', contradictions)
    set_attr_or_key(finding, 'confidence_score', confidence_score)
    set_attr_or_key(
        finding,
        'confidence_reason',
        f'base={base:.2f}; evidence={len(evidence_refs)}; cross_signal={len(support)}; contradictions={len(contradictions)}',
    )
    metadata = dict(getattr(finding, 'metadata', {}) or {})
    metadata.update(
        {
            'confidence_score': confidence_score,
            'confidence_reason': getattr(finding, 'confidence_reason', ''),
            'evidence_count': len(evidence_refs),
            'cross_signal_support': support,
            'contradictions': contradictions,
        }
    )
    set_attr_or_key(finding, 'metadata', metadata)


def _annotate_fix(session: Any, proposal: Any) -> None:
    related = []
    family = str((getattr(proposal, 'metadata', {}) or {}).get('family') or getattr(proposal, 'family', '') or '').lower()
    for finding in list(getattr(session, 'findings', []) or []):
        tags = {str(item).lower() for item in (getattr(finding, 'tags', []) or [])}
        compact = ''.join(sorted(tags)).replace('-', '')
        if family and family.replace('-', '') in compact:
            related.append(str(getattr(finding, 'finding_id', '')))
    contradictions = []
    if not bool(getattr(proposal, 'reversible', True)):
        contradictions.append('proposal no reversible')
    risk_level = str(getattr(proposal, 'risk_level', 'low') or 'low').lower()
    risk_tier = 'safe' if risk_level == 'low' and getattr(proposal, 'reversible', True) else 'guarded'
    if risk_level in {'high', 'critical'}:
        risk_tier = 'high-risk'
    base = 0.58 if risk_tier == 'safe' else 0.48 if risk_tier == 'guarded' else 0.31
    verification_steps = list(getattr(proposal, 'verification_steps', []) or [])
    commands = list(getattr(proposal, 'commands', []) or [])
    score = base + min(0.18, len(related) * 0.06) + (0.09 if verification_steps else -0.05) + (0.05 if commands else -0.05) - len(contradictions) * 0.12
    confidence_score = _clamp(score)
    set_attr_or_key(proposal, 'risk_tier', risk_tier)
    set_attr_or_key(proposal, 'evidence_count', len(related))
    set_attr_or_key(proposal, 'cross_signal_support', related[:6])
    set_attr_or_key(proposal, 'contradictions', contradictions)
    set_attr_or_key(proposal, 'confidence_score', confidence_score)
    set_attr_or_key(
        proposal,
        'confidence_reason',
        f'risk_tier={risk_tier}; related_findings={len(related)}; verification_steps={len(verification_steps)}; contradictions={len(contradictions)}',
    )
    metadata = dict(getattr(proposal, 'metadata', {}) or {})
    metadata.update(
        {
            'risk_tier': risk_tier,
            'confidence_score': confidence_score,
            'confidence_reason': getattr(proposal, 'confidence_reason', ''),
            'evidence_count': len(related),
            'cross_signal_support': related[:6],
            'contradictions': contradictions,
        }
    )
    set_attr_or_key(proposal, 'metadata', metadata)


def _normalize_strategy_hint(planner_hint: Any | None) -> dict[str, Any]:
    hint = str(planner_hint or '').strip().lower()
    if hint not in _ALLOWED_STRATEGIES:
        hint = ''
    return {
        'enabled': bool(hint),
        'hint': hint or None,
        'source': 'callsite' if hint else None,
    }


def score_patch_strategy(preflight: Any, risk_summary: dict[str, Any], operations: list[Any], *, planner_hint: Any | None = None) -> dict[str, Any]:
    target_files = list(get_attr_or_key(preflight, 'target_files', []) or [])
    surface_summary = dict(get_attr_or_key(preflight, 'surface_summary', {}) or {})
    anchor_diagnostics = dict(get_attr_or_key(preflight, 'anchor_diagnostics', {}) or {})
    strategy_hints = dict(get_attr_or_key(preflight, 'strategy_hints', {}) or {})
    risk_level = str((risk_summary or {}).get('risk_level') or 'low').lower()
    risk_tier = str((risk_summary or {}).get('risk_tier') or 'safe').lower()
    planner_stub = _normalize_strategy_hint(planner_hint or strategy_hints.get('planner_stub', {}).get('hint'))

    operation_types = [str(get_attr_or_key(item, 'type', '')) for item in list(operations or [])]
    mutating_count = int((risk_summary or {}).get('mutating_operation_count') or len(operation_types))
    exact_ops = sum(1 for item in operation_types if item in _TEXT_EXACT_OPS)
    regex_ops = sum(1 for item in operation_types if item in _REGEX_OPS)
    semantic_ops = sum(1 for item in operation_types if item in _SEMANTIC_OPS)
    structural_candidates = list((risk_summary or {}).get('structural_candidate_files') or surface_summary.get('structural_candidate_files') or [])
    fragile_anchor_count = int((risk_summary or {}).get('fragile_anchor_count') or anchor_diagnostics.get('fragile_anchor_operation_count', 0) or 0)
    exact_anchor_count = int((risk_summary or {}).get('exact_anchor_count') or anchor_diagnostics.get('exact_anchor_operation_count', 0) or 0)
    blockers = list((risk_summary or {}).get('blocked_reasons') or [])

    anchor_confidence = _clamp(0.88 - (0.17 * fragile_anchor_count) + (0.08 if exact_anchor_count else -0.14) - (0.04 * max(0, len(target_files) - 1)))
    syntax_confidence = _clamp(0.64 + min(0.18, len(list(get_attr_or_key(preflight, 'syntax_validation_plan', []) or [])) * 0.05) - (0.12 if blockers else 0.0))
    semantic_confidence = _clamp(0.82 if structural_candidates or semantic_ops else 0.54 + min(0.12, regex_ops * 0.04))
    batch_risk = _clamp(0.26 + min(0.44, max(0, len(target_files) - 1) * 0.12 + max(0, mutating_count - 3) * 0.03) + (0.12 if risk_level in {'high', 'critical'} else 0.0))
    rollback_readiness = _clamp(0.74 - (0.09 if risk_tier == 'blocked' else 0.0) + (0.08 if risk_level in {'medium', 'high'} else 0.0))

    candidate_scores = {
        'exact': _clamp(0.42 + (0.24 if len(target_files) == 1 else -0.10) + (0.18 if exact_ops else -0.08) - (0.16 * fragile_anchor_count) - (0.12 if structural_candidates else 0.0) + (0.06 if planner_stub.get('hint') == 'exact' else 0.0)),
        'structural': _clamp(0.28 + (0.26 if structural_candidates else -0.06) + min(0.12, regex_ops * 0.04) + min(0.16, semantic_ops * 0.06) + min(0.12, fragile_anchor_count * 0.05) + (0.08 if planner_stub.get('hint') == 'structural' else 0.0)),
        'guarded': _clamp(0.30 + (0.18 if risk_level in {'medium', 'high'} else 0.0) + min(0.16, fragile_anchor_count * 0.06) + (0.10 if blockers else 0.0) + (0.06 if planner_stub.get('hint') == 'guarded' else 0.0)),
        'transactional': _clamp(0.22 + min(0.28, max(0, len(target_files) - 1) * 0.12) + min(0.16, max(0, mutating_count - 4) * 0.03) + (0.10 if risk_level in {'high', 'critical'} else 0.0) + (0.08 if planner_stub.get('hint') == 'transactional' else 0.0)),
        'probe-only': _clamp(0.12 + (0.52 if blockers else 0.0) + (0.16 if not operation_types else 0.0) + (0.12 if planner_stub.get('hint') == 'probe-only' else 0.0)),
    }

    overall_confidence = _clamp((anchor_confidence + syntax_confidence + semantic_confidence + (1.0 - batch_risk) + rollback_readiness) / 5.0)
    recommended_guardrails = list((risk_summary or {}).get('recommended_guardrails') or [])
    if batch_risk >= 0.62 and 'dry-run-required' not in recommended_guardrails:
        recommended_guardrails.append('dry-run-required')
    if rollback_readiness < 0.52 and 'checkpoint-required' not in recommended_guardrails:
        recommended_guardrails.append('checkpoint-required')
    if planner_stub.get('enabled') and 'planner-hint-applied' not in recommended_guardrails:
        recommended_guardrails.append('planner-hint-applied')

    return {
        'anchor_confidence': anchor_confidence,
        'syntax_confidence': syntax_confidence,
        'semantic_confidence': semantic_confidence,
        'batch_risk': batch_risk,
        'rollback_readiness': rollback_readiness,
        'overall_confidence': overall_confidence,
        'candidate_scores': candidate_scores,
        'planner_stub': planner_stub,
        'recommended_guardrails': sorted(dict.fromkeys(recommended_guardrails)),
    }


def annotate_session_confidence(session: Any, *, base_dir: Path) -> dict[str, Any]:
    findings = list(getattr(session, 'findings', []) or [])
    proposals = list(getattr(session, 'fix_proposals', []) or [])
    for finding in findings:
        _annotate_finding(findings, finding)
    for proposal in proposals:
        _annotate_fix(session, proposal)
    summary = {
        'session_id': getattr(session, 'session_id', None),
        'finding_confidence': [
            {
                'finding_id': getattr(item, 'finding_id', ''),
                'title': getattr(item, 'title', ''),
                'severity': getattr(item, 'severity', 'info'),
                'confidence_score': getattr(item, 'confidence_score', None),
                'confidence_reason': getattr(item, 'confidence_reason', ''),
                'evidence_count': getattr(item, 'evidence_count', 0),
                'cross_signal_support': list(getattr(item, 'cross_signal_support', []) or []),
                'contradictions': list(getattr(item, 'contradictions', []) or []),
            }
            for item in findings
        ],
        'fix_confidence': [
            {
                'proposal_id': getattr(item, 'proposal_id', ''),
                'title': getattr(item, 'title', ''),
                'risk_tier': getattr(item, 'risk_tier', 'guarded'),
                'confidence_score': getattr(item, 'confidence_score', None),
                'confidence_reason': getattr(item, 'confidence_reason', ''),
                'evidence_count': getattr(item, 'evidence_count', 0),
                'cross_signal_support': list(getattr(item, 'cross_signal_support', []) or []),
                'contradictions': list(getattr(item, 'contradictions', []) or []),
            }
            for item in proposals
        ],
    }
    confidence_dir = ensure_dir(Path(base_dir) / 'reports' / 'confidence')
    json_path = confidence_dir / 'confidence_summary.json'
    md_path = confidence_dir / 'confidence_summary.md'
    atomic_write_text(json_path, json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    lines = ['# Confidence summary', '']
    lines.append('## Findings')
    lines.append('')
    for row in summary['finding_confidence']:
        lines.append(f"- `{row['finding_id']}` score=`{row['confidence_score']}` evidence=`{row['evidence_count']}`")
        lines.append(f"  - {row['confidence_reason']}")
    lines.append('')
    lines.append('## Fix proposals')
    lines.append('')
    for row in summary['fix_confidence']:
        lines.append(f"- `{row['proposal_id']}` score=`{row['confidence_score']}` tier=`{row['risk_tier']}`")
        lines.append(f"  - {row['confidence_reason']}")
    lines.append('')
    atomic_write_text(md_path, '\n'.join(lines))
    try:
        session.options['confidence_summary_path'] = str(json_path)
    except Exception:
        pass
    return summary
