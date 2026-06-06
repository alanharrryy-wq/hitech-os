#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Auto rollback decision layer aligned to hardened Phase 1 policy."""

from typing import Any

from .verification_requirements import assess_verification_outcome


def maybe_auto_rollback(run_record: Any, verifier_results: list[dict[str, Any]]) -> dict[str, Any]:
    if isinstance(run_record, dict):
        record = dict(run_record)
    else:
        record = {
            'run_id': getattr(run_record, 'run_id', None),
            'required_verifiers': list(getattr(run_record, 'required_verifiers', []) or []),
            'rollback_target': getattr(run_record, 'rollback_target', None),
            'system_status': getattr(run_record, 'system_status', None),
            'patch_status': getattr(run_record, 'patch_status', None),
            'risk_summary': dict(getattr(run_record, 'risk_summary', {}) or {}),
            'target_files': list(getattr(run_record, 'target_files', []) or []),
        }
    assessment = assess_verification_outcome(
        dict(record.get('risk_summary') or {}),
        list(record.get('target_files') or []),
        verifier_results,
    )
    should_rollback = bool((not assessment.get('passed')) and record.get('rollback_target'))
    failures = list(assessment.get('failed_required_verifiers') or [])
    missing = list(assessment.get('missing_required_verifiers') or [])
    reason_bits = []
    if failures:
        reason_bits.append(f"failed_required_verifiers={','.join(failures)}")
    if missing:
        reason_bits.append(f"missing_required_verifiers={','.join(missing)}")
    if not failures and not missing and not assessment.get('passed'):
        reason_bits.append(f"verification_floor={assessment.get('verification_floor')}")
    return {
        'run_id': record.get('run_id'),
        'required_verifiers': list(assessment.get('required_verifiers') or []),
        'failed_required_verifiers': failures,
        'missing_required_verifiers': missing,
        'should_rollback': should_rollback,
        'rollback_target': record.get('rollback_target'),
        'rollback_reason': ';'.join(reason_bits) if reason_bits else None,
        'recommended_system_status': 'rolled_back' if should_rollback else 'failed' if not assessment.get('passed') else 'verified',
        'verification_assessment': assessment,
    }
