#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Auto rollback decision layer aligned to the Phase 0 master spec."""

from typing import Any


def maybe_auto_rollback(run_record: Any, verifier_results: list[dict[str, Any]]) -> dict[str, Any]:
    record = run_record if isinstance(run_record, dict) else {
        'run_id': getattr(run_record, 'run_id', None),
        'required_verifiers': list(getattr(run_record, 'required_verifiers', []) or []),
        'rollback_target': getattr(run_record, 'rollback_target', None),
        'system_status': getattr(run_record, 'system_status', None),
        'patch_status': getattr(run_record, 'patch_status', None),
    }
    required = [str(item) for item in list(record.get('required_verifiers') or []) if str(item)]
    failures = []
    by_id = {str(item.get('verifier_id') or ''): item for item in list(verifier_results or []) if isinstance(item, dict)}
    for verifier_id in required:
        result = by_id.get(verifier_id)
        if not result or not bool(result.get('ok', False)):
            failures.append(verifier_id)
    should_rollback = bool(failures and record.get('rollback_target'))
    return {
        'run_id': record.get('run_id'),
        'required_verifiers': required,
        'failed_required_verifiers': failures,
        'should_rollback': should_rollback,
        'rollback_target': record.get('rollback_target'),
        'recommended_system_status': 'rolled_back' if should_rollback else 'failed' if failures else 'verified',
    }
