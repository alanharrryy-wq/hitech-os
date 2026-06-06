#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Legacy audit adapter.

Canonical ownership lives in capatch_audit/capatch_policy/capatch_verify.
This module only preserves a narrow compatibility API used by legacy callers.
"""

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from capatch_audit import apply_rollback, finalize_run, list_checkpoints, load_run, start_run
from capatch_policy import maybe_auto_rollback
from capatch_verify import run_required_verifiers


def _flatten_operations(operations: list[Any]) -> list[Any]:
    rows: list[Any] = []
    for operation in list(operations or []):
        nested = getattr(operation, 'operations', None)
        if nested:
            rows.extend(_flatten_operations(list(nested)))
        else:
            rows.append(operation)
    return rows


def _operation_spec(operation: Any) -> Any:
    return getattr(operation, 'spec', operation)


def _operation_rows(ctx: Any, operations: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    root_dir = Path(getattr(ctx, 'root_dir', Path.cwd())).resolve()
    rows: list[dict[str, Any]] = []
    target_files: list[str] = []
    for index, operation in enumerate(_flatten_operations(operations), start=1):
        spec = _operation_spec(operation)
        relative_path = str(getattr(spec, 'file', '') or '')
        operation_type = str(getattr(spec, 'type', 'unknown') or 'unknown')
        operation_label = str(getattr(spec, 'label', '') or operation_type or f'op-{index}')
        target_path = (root_dir / relative_path).resolve() if relative_path else root_dir
        rows.append(
            {
                'index': index,
                'operation_label': operation_label,
                'operation_type': operation_type,
                'relative_path': relative_path,
                'target_path': str(target_path),
            }
        )
        if relative_path and relative_path not in target_files:
            target_files.append(relative_path)
    return rows, target_files


def _risk_summary(target_files: list[str], operation_count: int) -> dict[str, Any]:
    return {
        'risk_level': 'low' if operation_count <= 1 else 'medium',
        'risk_tier': 'safe' if operation_count <= 1 else 'guarded',
        'target_files': list(target_files),
        'operation_count': int(operation_count),
        'required_verifiers': [],
        'compat_adapter': 'core_patch_audit',
    }


def start_patch_run(ctx: Any, operations: list[Any], preview_content_by_target: dict[Any, str]) -> dict[str, Any]:
    rows, target_files = _operation_rows(ctx, operations)
    preflight = {
        'ok': True,
        'target_files': list(target_files),
        'operation_count': len(rows),
        'mutating_operation_count': len(rows),
        'read_only_operation_count': 0,
        'conflicts': [],
        'path_violations': [],
        'schema_violations': [],
    }
    risk_summary = _risk_summary(target_files, len(rows))
    record = start_run(ctx, preflight, risk_summary)
    return {
        'record': record,
        'rows': rows,
        'preview_content_by_target': dict(preview_content_by_target or {}),
        'risk_summary': risk_summary,
    }


def _build_operation_results(state: dict[str, Any], results: list[str], *, patch_status: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, row in enumerate(list(state.get('rows') or []), start=1):
        output.append(
            {
                'operation_label': row.get('operation_label') or f'op-{index}',
                'operation_type': row.get('operation_type') or 'unknown',
                'target_path': row.get('target_path'),
                'patch_status': patch_status,
                'message': results[index - 1] if index - 1 < len(results) else patch_status,
                'support_notes': ['core_patch_audit compatibility adapter'],
            }
        )
    return output


def _verification_context(ctx: Any) -> dict[str, Any]:
    return {
        'root_dir': str(Path(getattr(ctx, 'root_dir', Path.cwd())).resolve()),
        'build_command': getattr(ctx, 'build_command', None),
        'test_command': getattr(ctx, 'test_command', None),
    }


def _run_policy_verifiers(ctx: Any, record: Any) -> list[dict[str, Any]]:
    required = list(getattr(record, 'required_verifiers', []) or [])
    if not required:
        return []
    target_files = [str(item) for item in list(getattr(record, 'target_files', []) or []) if str(item)]
    return list(run_required_verifiers(target_files, required, _verification_context(ctx)) or [])


def finalize_patch_run_success(ctx: Any, state: dict[str, Any], results: list[str]) -> dict[str, Any]:
    record = state['record']
    operation_results = _build_operation_results(state, list(results or []), patch_status='applied')
    verifier_results = _run_policy_verifiers(ctx, record)
    rollback_decision = maybe_auto_rollback(record, verifier_results)
    rollback_event: dict[str, Any] | None = None

    if rollback_decision.get('should_rollback'):
        try:
            rollback_event = apply_rollback(run_id=str(record.run_id), root_dir=Path(getattr(ctx, 'root_dir')).resolve())
            refreshed = load_run(str(record.run_id), root_dir=Path(getattr(ctx, 'root_dir')).resolve())
            if refreshed is not None:
                record = refreshed
            else:
                record.patch_status = 'rolled_back'
                record.system_status = 'rolled_back'
        except Exception as rollback_exc:
            record.patch_status = 'failed'
            record.system_status = 'failed'
            record.error = f'auto rollback failed: {type(rollback_exc).__name__}: {rollback_exc}'
    elif rollback_decision.get('failed_required_verifiers'):
        record.patch_status = 'failed'
        record.system_status = 'failed'
        record.error = str(rollback_decision.get('rollback_reason') or 'required verifier failed')

    finalized = finalize_run(record, operation_results, verifier_results)
    return {
        'run_id': finalized.run_id,
        'patch_status': finalized.patch_status,
        'system_status': finalized.system_status,
        'rollback_target': finalized.rollback_target,
        'required_verifiers': list(finalized.required_verifiers),
        'verifier_results': list(finalized.verifier_results),
        'failed_required_verifiers': list(rollback_decision.get('failed_required_verifiers') or []),
        'error': finalized.error,
        'rollback_event': rollback_event,
    }


def finalize_patch_run_failure(ctx: Any, state: dict[str, Any], error: str, *, rollback_applied: bool = True) -> dict[str, Any]:
    record = state['record']
    record.error = str(error)
    record.patch_status = 'rolled_back' if rollback_applied else 'failed'
    record.system_status = 'rolled_back' if rollback_applied else 'failed'
    operation_results = _build_operation_results(state, [str(error)], patch_status=record.patch_status)
    finalized = finalize_run(record, operation_results, [])
    return {
        'run_id': finalized.run_id,
        'patch_status': finalized.patch_status,
        'system_status': finalized.system_status,
        'rollback_target': finalized.rollback_target,
        'error': finalized.error,
    }


def list_checkpoint_rows(root_dir: Path) -> list[dict[str, Any]]:
    return list_checkpoints(Path(root_dir).resolve())


def rollback_checkpoint(root_dir: Path, checkpoint_id: str) -> dict[str, Any]:
    return apply_rollback(checkpoint_id=str(checkpoint_id), root_dir=Path(root_dir).resolve())


def rollback_last(root_dir: Path) -> dict[str, Any]:
    rows = list_checkpoints(Path(root_dir).resolve())
    if not rows:
        raise FileNotFoundError('No hay checkpoints para rollback.')
    checkpoint_id = str(rows[0].get('checkpoint_id') or '')
    if not checkpoint_id:
        raise FileNotFoundError('No hay checkpoints para rollback.')
    return apply_rollback(checkpoint_id=checkpoint_id, root_dir=Path(root_dir).resolve())


def _record_to_dict(record: Any) -> dict[str, Any]:
    if isinstance(record, dict):
        return dict(record)
    if is_dataclass(record):
        return asdict(record)
    if hasattr(record, '__dict__'):
        return dict(record.__dict__)
    return {
        'run_id': getattr(record, 'run_id', None),
        'schema_version': getattr(record, 'schema_version', None),
        'started_at': getattr(record, 'started_at', None),
        'finished_at': getattr(record, 'finished_at', None),
        'root_dir': getattr(record, 'root_dir', None),
        'cwd': getattr(record, 'cwd', None),
        'invocation_mode': getattr(record, 'invocation_mode', None),
        'patch_status': getattr(record, 'patch_status', None),
        'system_status': getattr(record, 'system_status', None),
        'execution_mode': getattr(record, 'execution_mode', None),
        'git_branch': getattr(record, 'git_branch', None),
        'git_head': getattr(record, 'git_head', None),
        'git_dirty_before': getattr(record, 'git_dirty_before', None),
        'git_dirty_after': getattr(record, 'git_dirty_after', None),
        'target_files': getattr(record, 'target_files', None),
        'operation_count': getattr(record, 'operation_count', None),
        'operation_results': getattr(record, 'operation_results', None),
        'risk_summary': getattr(record, 'risk_summary', None),
        'required_verifiers': getattr(record, 'required_verifiers', None),
        'verifier_results': getattr(record, 'verifier_results', None),
        'rollback_target': getattr(record, 'rollback_target', None),
        'baseline_ref': getattr(record, 'baseline_ref', None),
        'error': getattr(record, 'error', None),
    }


def load_patch_run(root_dir: Path, run_id: str) -> dict[str, Any]:
    record = load_run(str(run_id), root_dir=Path(root_dir).resolve())
    if record is None:
        raise FileNotFoundError(f'Run no existe: {run_id}')
    payload = _record_to_dict(record)
    rollback_target = str(payload.get('rollback_target') or '')
    checkpoint_id = Path(rollback_target).name if rollback_target else None
    payload['rollback_command'] = (
        f'python capatch.py --root-dir "{payload.get("root_dir")}" --rollback-checkpoint "{checkpoint_id}"'
        if checkpoint_id
        else None
    )
    return payload
