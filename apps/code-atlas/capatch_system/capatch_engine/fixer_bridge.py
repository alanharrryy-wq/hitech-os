#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Public Autofix Bridge over the patch engine.

Phase 2 hardening goals:
- no success without explicit verification outcome for mutating proposals
- surface lifecycle/rollback data in bridge results
- keep sandbox/live apply results reconstructable
"""

import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from capatch_audit import apply_rollback, finalize_run, start_run
from capatch_contracts.constants import BACKUP_DIR_NAME
from capatch_policy import classify_change, compute_required_verifiers, maybe_auto_rollback
from capatch_verify import run_required_verifiers
from plugin_lib.fixer_utils import command_is_allowlisted, evaluate_applicability_predicates, parse_command, verifier_ctx_defaults

from .context import PatchContext
from .executor import apply
from .parser import parse_operations
from .preflight import preflight
from .preview import preview


def _now_token(prefix: str = 'autofix') -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _proposal_get(proposal: Any, name: str, default: Any = None) -> Any:
    if isinstance(proposal, dict):
        return proposal.get(name, default)
    return getattr(proposal, name, default)


def _proposal_id(proposal: Any) -> str:
    return str(_proposal_get(proposal, 'proposal_id', 'proposal.unknown') or 'proposal.unknown')


def _root_dir(root_dir: Path | str) -> Path:
    return Path(root_dir).expanduser().resolve()


def _checkpoint_dir(root_dir: Path, proposal: Any) -> Path:
    token = _now_token(_proposal_id(proposal).replace('.', '_').replace('/', '_'))
    return root_dir / 'reports' / 'checkpoints' / token


def _patch_context(root_dir: Path, proposal: Any, *, dry_run: bool) -> PatchContext:
    checkpoint_dir = _checkpoint_dir(root_dir, proposal)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    backup_dir = root_dir / BACKUP_DIR_NAME
    backup_dir.mkdir(parents=True, exist_ok=True)
    return PatchContext(
        root_dir=root_dir,
        backup_dir=backup_dir,
        checkpoint_dir=checkpoint_dir,
        dry_run=dry_run,
        auto_support=False,
        requested_by='autofix-bridge',
        invocation_mode='apply-fixes',
        run_id=_now_token('run'),
    )


def evaluate_fix_proposal(root_dir: Path | str, session: Any, proposal: Any) -> dict[str, Any]:
    root = _root_dir(root_dir)
    ok, checks = evaluate_applicability_predicates(root, session, list(_proposal_get(proposal, 'applicability_predicates', []) or []))
    return {
        'proposal_id': _proposal_id(proposal),
        'ok': ok,
        'checks': checks,
        'family': str(_proposal_get(proposal, 'family', 'general') or 'general'),
    }


def _preflight_like(target_files: list[str], operation_count: int) -> dict[str, Any]:
    return {
        'target_files': list(target_files),
        'operation_count': int(operation_count),
        'mutating_operation_count': int(operation_count),
        'read_only_operation_count': 0,
        'conflicts': [],
        'path_violations': [],
        'schema_violations': [],
    }


def _verification_ids_from_recipe(recipe: list[dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    seen = set()
    for item in list(recipe or []):
        verifier_id = str(item.get('verifier_id') or '').strip()
        if verifier_id and verifier_id not in seen:
            seen.add(verifier_id)
            ordered.append(verifier_id)
    return ordered


def _write_command_checkpoint(root_dir: Path, checkpoint_dir: Path, affected_paths: list[str]) -> dict[str, Any]:
    copies_dir = checkpoint_dir / 'command_snapshot'
    copies_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        'checkpoint_dir': str(checkpoint_dir),
        'snapshot_dir': str(copies_dir),
        'copied': [],
        'missing_before': [],
    }
    for relative in list(affected_paths or []):
        source = (root_dir / relative).resolve()
        if not source.exists():
            manifest['missing_before'].append(relative)
            continue
        target = copies_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_file():
            shutil.copy2(source, target)
            manifest['copied'].append(relative)
    return manifest


def _restore_command_checkpoint(root_dir: Path, checkpoint_manifest: dict[str, Any], rollback_recipe: list[dict[str, Any]]) -> dict[str, Any]:
    snapshot_dir = Path(str(checkpoint_manifest.get('snapshot_dir') or '')).resolve()
    restored: list[str] = []
    deleted: list[str] = []
    if snapshot_dir.exists():
        for source in snapshot_dir.rglob('*'):
            if not source.is_file():
                continue
            relative = source.relative_to(snapshot_dir).as_posix()
            target = root_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            restored.append(relative)
    for step in list(rollback_recipe or []):
        if str(step.get('action') or '') != 'delete_paths':
            continue
        for relative in list(step.get('paths') or []):
            target = (root_dir / str(relative)).resolve()
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                deleted.append(str(relative))
            elif target.exists():
                try:
                    target.unlink()
                    deleted.append(str(relative))
                except Exception:
                    pass
    return {'restored_paths': restored, 'deleted_paths': deleted, 'status': 'restored'}


def _run_allowed_commands(root_dir: Path, proposal: Any, *, dry_run: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    family = str(_proposal_get(proposal, 'family', 'general') or 'general')
    for command in list(_proposal_get(proposal, 'commands', []) or []):
        allow_ok, detail = command_is_allowlisted(str(command), family=family)
        row = {
            'command': str(command),
            'allowlisted': allow_ok,
            'detail': detail,
            'returncode': None,
            'stdout': '',
            'stderr': '',
        }
        if not allow_ok:
            rows.append(row)
            continue
        if dry_run:
            row['returncode'] = 0
            row['stdout'] = '[dry-run] command skipped'
            rows.append(row)
            continue
        argv = parse_command(str(command))
        completed = subprocess.run(argv, cwd=str(root_dir), capture_output=True, text=True, timeout=180, check=False)
        row['returncode'] = completed.returncode
        row['stdout'] = (completed.stdout or '')[:4000]
        row['stderr'] = (completed.stderr or '')[:4000]
        rows.append(row)
    return rows


def _target_files_for_proposal(proposal: Any) -> list[str]:
    seen = set()
    ordered: list[str] = []
    for item in list(_proposal_get(proposal, 'affected_paths', []) or []):
        token = str(item or '').strip().replace('\\', '/')
        if token and token not in seen:
            seen.add(token)
            ordered.append(token)
    for op in list(_proposal_get(proposal, 'ops_payload', []) or []):
        token = str((op or {}).get('file') or '').strip().replace('\\', '/')
        if token and token not in seen:
            seen.add(token)
            ordered.append(token)
    for recipe in list(_proposal_get(proposal, 'verification_recipe', []) or []):
        token = str((recipe or {}).get('path') or '').strip().replace('\\', '/')
        if token and token not in seen:
            seen.add(token)
            ordered.append(token)
    return ordered


def _verification_ids(proposal: Any, risk_summary: dict[str, Any], target_files: list[str]) -> list[str]:
    ordered = _verification_ids_from_recipe(list(_proposal_get(proposal, 'verification_recipe', []) or []))
    if ordered:
        return ordered
    return compute_required_verifiers(risk_summary, target_files)


def _operation_results_ok(operation_rows: list[dict[str, Any]]) -> bool:
    rows = list(operation_rows or [])
    return bool(rows) and all(str(row.get('patch_status') or '') in {'applied', 'noop', 'skipped'} for row in rows)


def _command_results_ok(command_rows: list[dict[str, Any]]) -> bool:
    return all(bool(row.get('allowlisted')) and int(row.get('returncode') or 0) == 0 for row in list(command_rows or []))


def _verifier_results_ok(verifier_rows: list[dict[str, Any]]) -> bool:
    return bool(list(verifier_rows or [])) and all(bool(row.get('ok', False)) for row in list(verifier_rows or []))


def _derive_execution_status(*, dry_run: bool, operation_results: list[dict[str, Any]], command_results: list[dict[str, Any]], verifier_results: list[dict[str, Any]], rollback_event: Any) -> str:
    if dry_run:
        return 'preview'
    if rollback_event:
        return 'rolled_back'
    if not _operation_results_ok(operation_results):
        return 'failed-operations'
    if not _command_results_ok(command_results):
        return 'failed-commands'
    if not _verifier_results_ok(verifier_results):
        return 'failed-verification'
    return 'applied'


def _lifecycle_summary(*, dry_run: bool, operation_results: list[dict[str, Any]], verifier_results: list[dict[str, Any]], rollback_event: Any) -> dict[str, Any]:
    verification_steps = [str(row.get('verifier_id') or '') for row in list(verifier_results or []) if str(row.get('verifier_id') or '')]
    verification_ok = _verifier_results_ok(verifier_results)
    rollback_triggered = bool(rollback_event)
    rollback_outcome = None
    if rollback_event is not None:
        rollback_outcome = str(rollback_event.get('status') or 'rolled_back') if isinstance(rollback_event, dict) else 'rolled_back'
    if dry_run:
        final_state = 'preview'
    elif rollback_triggered:
        final_state = 'rolled_back'
    elif verification_ok:
        final_state = 'verification_passed'
    else:
        final_state = 'verification_failed'
    return {
        'preconditions_satisfied': True,
        'applied_changes': bool(list(operation_results or [])),
        'verification_steps': verification_steps,
        'verification_outcome': 'passed' if verification_ok else 'failed',
        'rollback_triggered': rollback_triggered,
        'rollback_outcome': rollback_outcome,
        'final_state': final_state,
    }


def staged_apply(root_dir: Path | str, proposal: Any, *, dry_run: bool = False, verification_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    root = _root_dir(root_dir)
    ctx = _patch_context(root, proposal, dry_run=dry_run)
    ops_payload = list(_proposal_get(proposal, 'ops_payload', []) or [])
    target_files = _target_files_for_proposal(proposal)
    preview_payload: dict[str, Any] = {'messages': [], 'diff_summary': {}, 'executions': []}
    operation_results: list[dict[str, Any]] = []
    run_record = None
    checkpoint_manifest = None
    command_rows: list[dict[str, Any]] = []
    rollback_event = None

    if ops_payload:
        operations = parse_operations(ops_payload)
        preflight_report = preflight(ctx, operations)
        risk_summary = classify_change(preflight_report, operations)
        preview_payload = preview(ctx, operations)
        run_record = start_run(ctx, preflight_report, risk_summary)
        if not dry_run:
            raw_results = apply(ctx, operations)
            operation_results = [
                {
                    'operation_label': item.operation_label,
                    'operation_type': item.operation_type,
                    'target_path': item.target_path,
                    'patch_status': item.patch_status,
                    'message': item.message,
                    'before_hash': item.before_hash,
                    'after_hash': item.after_hash,
                    'preview_hash': item.preview_hash,
                    'bytes_before': item.bytes_before,
                    'bytes_after': item.bytes_after,
                    'changed_line_count': item.changed_line_count,
                    'support_notes': list(item.support_notes),
                }
                for item in raw_results
            ]
        else:
            operation_results = []
    else:
        preflight_report = _preflight_like(target_files, 0)
        risk_summary = {
            'risk_level': str(_proposal_get(proposal, 'risk_level', 'medium') or 'medium'),
            'risk_tier': 'guarded',
            'target_files': list(target_files),
            'operation_count': 0,
            'mutating_operation_count': 0,
            'read_only_operation_count': 0,
            'touches_sensitive': False,
            'touches_packaging': any(Path(item).name.lower() in {'package.json', 'pyproject.toml', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock'} for item in target_files),
            'touches_ui': False,
            'blocked_reasons': [],
            'reasons': ['command based fix proposal'],
        }
        risk_summary['required_verifiers'] = compute_required_verifiers(risk_summary, target_files)
        run_record = start_run(ctx, _preflight_like(target_files, 0), risk_summary)
        checkpoint_manifest = _write_command_checkpoint(root, Path(run_record.rollback_target or ctx.checkpoint_dir), target_files)
        command_rows = _run_allowed_commands(root, proposal, dry_run=dry_run)
        operation_results = [
            {
                'operation_label': f'command::{index + 1}',
                'operation_type': 'Command',
                'target_path': root.as_posix(),
                'patch_status': 'applied' if row.get('returncode') == 0 else 'failed',
                'message': row.get('detail') or row.get('command') or 'command',
                'before_hash': None,
                'after_hash': None,
                'preview_hash': None,
                'bytes_before': None,
                'bytes_after': None,
                'changed_line_count': 0,
                'support_notes': [row.get('command') or ''],
            }
            for index, row in enumerate(command_rows)
        ] if not dry_run else []

    required_verifiers = _verification_ids(proposal, dict(risk_summary or {}), target_files)
    verifier_ctx = verifier_ctx_defaults(root, proposal)
    verifier_ctx.update(
        {
            'command_results': command_rows,
            'operation_results': operation_results,
            'proposal_id': _proposal_id(proposal),
            'family': str(_proposal_get(proposal, 'family', 'general') or 'general'),
            'verification_recipe': list(_proposal_get(proposal, 'verification_recipe', []) or []),
            # CAPATCH_DELTA1_FIXER_CHECKPOINT_CTX: expose command/ops checkpoint to delta-aware verifiers when available.
            'checkpoint_dir': str(Path(getattr(ctx, 'checkpoint_dir', '') or '').expanduser().resolve()) if str(getattr(ctx, 'checkpoint_dir', '') or '').strip() else None,
        }
    )
    verifier_ctx.update(dict(verification_ctx or {}))
    verifier_results = [] if dry_run else run_required_verifiers(target_files, required_verifiers, verifier_ctx)
    finalized_record = finalize_run(run_record, operation_results, verifier_results) if run_record is not None else None
    rollback_decision = maybe_auto_rollback(finalized_record, verifier_results) if finalized_record is not None else {}

    if rollback_decision.get('should_rollback') and not dry_run:
        if ops_payload:
            rollback_event = apply_rollback(run_id=finalized_record.run_id, root_dir=root)
        else:
            rollback_event = _restore_command_checkpoint(root, checkpoint_manifest or {}, list(_proposal_get(proposal, 'rollback_recipe', []) or []))

    operation_ok = _operation_results_ok(operation_results)
    command_ok = _command_results_ok(command_rows)
    verification_ok = _verifier_results_ok(verifier_results)
    execution_status = _derive_execution_status(
        dry_run=dry_run,
        operation_results=operation_results,
        command_results=command_rows,
        verifier_results=verifier_results,
        rollback_event=rollback_event,
    )
    lifecycle = _lifecycle_summary(
        dry_run=dry_run,
        operation_results=operation_results,
        verifier_results=verifier_results,
        rollback_event=rollback_event,
    )
    execution_ok = execution_status in {'preview', 'applied'} and lifecycle['verification_outcome'] == 'passed'

    return {
        'proposal_id': _proposal_id(proposal),
        'family': str(_proposal_get(proposal, 'family', 'general') or 'general'),
        'dry_run': dry_run,
        'target_files': target_files,
        'risk_summary': risk_summary,
        'required_verifiers': required_verifiers,
        'preview': {
            'messages': list(preview_payload.get('messages', []) or []),
            'diff_summary': preview_payload.get('diff_summary', {}),
        },
        'operation_results': operation_results,
        'command_results': command_rows,
        'verifier_results': verifier_results,
        'rollback_decision': rollback_decision,
        'rollback_event': rollback_event,
        'execution_status': execution_status,
        'execution_ok': execution_ok,
        'verification_ok': verification_ok,
        'command_ok': command_ok,
        'operation_ok': operation_ok,
        'rolled_back': bool(rollback_event),
        'summary': f"status={execution_status} verifiers={len(verifier_results)} commands={len(command_rows)} rollback={bool(rollback_event)}",
        'run_id': getattr(finalized_record, 'run_id', None),
        'checkpoint_dir': str(getattr(ctx, 'checkpoint_dir', '')),
        **lifecycle,
    }


def sandbox_apply(root_dir: Path | str, proposal: Any, *, verification_ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    root = _root_dir(root_dir)
    ops_payload = list(_proposal_get(proposal, 'ops_payload', []) or [])
    if not ops_payload:
        return {
            'proposal_id': _proposal_id(proposal),
            'status': 'skipped',
            'reason': 'sandbox only runs for ops-based proposals',
            'verifier_results': [],
        }
    sandbox_root = Path(tempfile.mkdtemp(prefix='capatch_autofix_sandbox_'))
    touched = _target_files_for_proposal(proposal)
    try:
        for relative in touched:
            source = (root / relative).resolve()
            if source.exists() and source.is_file():
                target = sandbox_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        result = staged_apply(sandbox_root, proposal, dry_run=False, verification_ctx=verification_ctx)
        result['status'] = 'ok'
        result['sandbox_root'] = str(sandbox_root)
        shutil.rmtree(sandbox_root, ignore_errors=True)
        result['sandbox_root_cleaned'] = True
        return result
    except Exception as exc:
        shutil.rmtree(sandbox_root, ignore_errors=True)
        return {
            'proposal_id': _proposal_id(proposal),
            'status': 'failed',
            'execution_status': 'sandbox-error',
            'execution_ok': False,
            'reason': f'{type(exc).__name__}: {exc}',
            'verifier_results': [],
            'preconditions_satisfied': False,
            'applied_changes': False,
            'verification_steps': [],
            'verification_outcome': 'failed',
            'rollback_triggered': False,
            'rollback_outcome': None,
            'final_state': 'sandbox_error',
        }
