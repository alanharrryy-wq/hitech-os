#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Confidence scoring and cross-signal helpers for operator trust layer."""

import json
from pathlib import Path
from typing import Any

from plugin_lib.diagnostic_rules import severity_rank
from plugin_lib.fs_utils import atomic_write_text, ensure_dir


def _clamp(value: float, low: float = 0.05, high: float = 0.99) -> float:
    return max(low, min(high, round(value, 3)))


def _related_support(findings: list[Any], current: Any) -> list[str]:
    support = []
    for item in findings:
        if item is current:
            continue
        if str(getattr(item, 'category', '')) == str(getattr(current, 'category', '')):
            support.append(str(getattr(item, 'finding_id', '')))
        elif set(getattr(item, 'tags', []) or []).intersection(set(getattr(current, 'tags', []) or [])):
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
    setattr(finding, 'evidence_count', len(evidence_refs))
    setattr(finding, 'cross_signal_support', support)
    setattr(finding, 'contradictions', contradictions)
    setattr(finding, 'confidence_score', confidence_score)
    setattr(
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
    finding.metadata = metadata


def _annotate_fix(session: Any, proposal: Any) -> None:
    related = []
    family = str((getattr(proposal, 'metadata', {}) or {}).get('family') or '').lower()
    for finding in list(getattr(session, 'findings', []) or []):
        tags = {str(item).lower() for item in (getattr(finding, 'tags', []) or [])}
        if family and family.replace('-', '') in ''.join(sorted(tags)).replace('-', ''):
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
    setattr(proposal, 'risk_tier', risk_tier)
    setattr(proposal, 'evidence_count', len(related))
    setattr(proposal, 'cross_signal_support', related[:6])
    setattr(proposal, 'contradictions', contradictions)
    setattr(proposal, 'confidence_score', confidence_score)
    setattr(
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
    proposal.metadata = metadata


def annotate_session_confidence(session: Any, *, base_dir: Path) -> dict[str, Any]:
    for finding in list(getattr(session, 'findings', []) or []):
        _annotate_finding(list(getattr(session, 'findings', []) or []), finding)
    for proposal in list(getattr(session, 'fix_proposals', []) or []):
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
            for item in list(getattr(session, 'findings', []) or [])
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
            for item in list(getattr(session, 'fix_proposals', []) or [])
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
    session.options['confidence_summary_path'] = str(json_path)
    return summary
