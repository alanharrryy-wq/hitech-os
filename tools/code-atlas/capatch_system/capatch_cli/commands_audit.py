#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from capatch_audit import apply_rollback, list_checkpoints, load_run, preview_rollback
from capatch_audit.rollback_preview import rollback_preview_to_dict

def _no_checkpoints_payload(root_dir: Path, *, dry_run: bool, checkpoint_id: str | None = None) -> dict[str, Any]:
    return {
        'status': 'skipped',
        'reason': 'no_checkpoints',
        'dry_run': bool(dry_run),
        'root_dir': str(root_dir),
        'checkpoint_id': checkpoint_id,
    }


def _record_to_dict(record: Any) -> dict[str, Any]:
    if record is None:
        raise FileNotFoundError('Run no existe')
    if isinstance(record, dict):
        return dict(record)
    if is_dataclass(record):
        return asdict(record)
    if hasattr(record, '__dict__'):
        return dict(record.__dict__)
    fields = (
        'run_id', 'schema_version', 'started_at', 'finished_at', 'root_dir', 'cwd', 'invocation_mode',
        'patch_status', 'system_status', 'execution_mode', 'git_branch', 'git_head', 'git_dirty_before',
        'git_dirty_after', 'target_files', 'operation_count', 'operation_results', 'risk_summary',
        'required_verifiers', 'verifier_results', 'rollback_target', 'baseline_ref', 'error'
    )
    return {name: getattr(record, name, None) for name in fields}


def _normalize_status(raw_status: Any) -> str:
    value = str(raw_status or "").strip().lower()
    if value == "skipped":
        return "skipped"
    if value in {"failed", "error", "rollback_failed"}:
        return "failed"
    return "ok"


def _emit_payload(payload: Any, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _audit_json_payload(
    *,
    action: str,
    root_dir: Path,
    dry_run: bool,
    payload: Any,
    checkpoint_id: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    base = payload if isinstance(payload, dict) else {}
    resolved_checkpoint = base.get("checkpoint_id") if isinstance(base, dict) else None
    return {
        "status": _normalize_status(base.get("status") if isinstance(base, dict) else None),
        "reason": str(reason or (base.get("reason") if isinstance(base, dict) else "") or f"{action} completed"),
        "outcome": str(action),
        "dry_run": bool(dry_run),
        "root_dir": str(root_dir),
        "checkpoint_id": str(resolved_checkpoint or checkpoint_id) if (resolved_checkpoint or checkpoint_id) else None,
        "verification_outcome": None,
        "data": payload,
    }


def _load_run_payload(root_dir: Path, run_id: str) -> dict[str, Any]:
    record = load_run(str(run_id), root_dir=root_dir)
    payload = _record_to_dict(record)
    checkpoint_target = payload.get('rollback_target')
    checkpoint_name = Path(checkpoint_target).name if checkpoint_target else None
    payload['rollback_preview_command'] = (
        f'python capatch.py --root-dir "{payload.get("root_dir") or str(root_dir)}" --rollback-checkpoint "{checkpoint_name}" --dry-run'
        if checkpoint_name
        else None
    )
    payload['rollback_apply_command'] = (
        f'python capatch.py --root-dir "{payload.get("root_dir") or str(root_dir)}" --rollback-checkpoint "{checkpoint_name}"'
        if checkpoint_name
        else None
    )
    return payload


def _list_checkpoints_payload(root_dir: Path) -> list[dict[str, Any]]:
    rows = list_checkpoints(root_dir)
    return [dict(item) for item in list(rows or []) if isinstance(item, dict)]


def _preview_checkpoint_payload(root_dir: Path, checkpoint_id: str) -> dict[str, Any]:
    preview = preview_rollback(checkpoint_id=str(checkpoint_id), root_dir=root_dir)
    return rollback_preview_to_dict(preview)


def _rollback_checkpoint_payload(root_dir: Path, checkpoint_id: str) -> dict[str, Any]:
    return apply_rollback(checkpoint_id=str(checkpoint_id), root_dir=root_dir)


def _preview_last_payload(root_dir: Path) -> dict[str, Any]:
    rows = _list_checkpoints_payload(root_dir)
    if not rows:
        return _no_checkpoints_payload(root_dir, dry_run=True)
    checkpoint_id = str(rows[0].get('checkpoint_id') or '')
    if not checkpoint_id:
        return _no_checkpoints_payload(root_dir, dry_run=True)
    return _preview_checkpoint_payload(root_dir, checkpoint_id)


def _rollback_last_payload(root_dir: Path) -> dict[str, Any]:
    rows = _list_checkpoints_payload(root_dir)
    if not rows:
        return _no_checkpoints_payload(root_dir, dry_run=False)
    checkpoint_id = str(rows[0].get('checkpoint_id') or '')
    if not checkpoint_id:
        return _no_checkpoints_payload(root_dir, dry_run=False)
    return _rollback_checkpoint_payload(root_dir, checkpoint_id)


def handle(args: Any) -> int | None:
    root_dir = Path(args.root_dir).expanduser().resolve()
    json_output = bool(getattr(args, "json_output", False))

    if getattr(args, 'list_checkpoints', False):
        payload = _list_checkpoints_payload(root_dir)
        to_emit: Any = payload
        if json_output:
            to_emit = _audit_json_payload(
                action="list-checkpoints",
                root_dir=root_dir,
                dry_run=bool(getattr(args, "dry_run", False)),
                payload=payload,
            )
        _emit_payload(to_emit, json_output=json_output)
        return 0

    if getattr(args, 'rollback_run', None):
        payload = (
            rollback_preview_to_dict(preview_rollback(run_id=str(args.rollback_run), root_dir=root_dir))
            if getattr(args, 'dry_run', False)
            else apply_rollback(run_id=str(args.rollback_run), root_dir=root_dir)
        )
        to_emit: Any = payload
        if json_output:
            to_emit = _audit_json_payload(
                action='rollback-run',
                root_dir=root_dir,
                dry_run=bool(getattr(args, 'dry_run', False)),
                payload=payload,
            )
        _emit_payload(to_emit, json_output=json_output)
        return 0

    if getattr(args, 'rollback_checkpoint', None):
        checkpoint_id = str(args.rollback_checkpoint)
        if getattr(args, 'dry_run', False):
            try:
                payload = _preview_checkpoint_payload(root_dir, checkpoint_id)
            except FileNotFoundError:
                payload = _no_checkpoints_payload(root_dir, dry_run=True, checkpoint_id=checkpoint_id)
        else:
            try:
                payload = _rollback_checkpoint_payload(root_dir, checkpoint_id)
            except FileNotFoundError:
                payload = _no_checkpoints_payload(root_dir, dry_run=False, checkpoint_id=checkpoint_id)
        to_emit: Any = payload
        if json_output:
            to_emit = _audit_json_payload(
                action='rollback-checkpoint',
                root_dir=root_dir,
                dry_run=bool(getattr(args, 'dry_run', False)),
                payload=payload,
                checkpoint_id=checkpoint_id,
            )
        _emit_payload(to_emit, json_output=json_output)
        return 0

    if getattr(args, 'rollback_last', False):
        if getattr(args, 'dry_run', False):
            try:
                payload = _preview_last_payload(root_dir)
            except FileNotFoundError:
                payload = _no_checkpoints_payload(root_dir, dry_run=True)
        else:
            try:
                payload = _rollback_last_payload(root_dir)
            except FileNotFoundError:
                payload = _no_checkpoints_payload(root_dir, dry_run=False)
        to_emit: Any = payload
        if json_output:
            to_emit = _audit_json_payload(
                action='rollback-last',
                root_dir=root_dir,
                dry_run=bool(getattr(args, 'dry_run', False)),
                payload=payload,
            )
        _emit_payload(to_emit, json_output=json_output)
        return 0

    if getattr(args, 'show_run', None):
        run_id = str(args.show_run)
        payload = _load_run_payload(root_dir, run_id)
        to_emit: Any = payload
        if json_output:
            to_emit = _audit_json_payload(
                action='show-run',
                root_dir=root_dir,
                dry_run=bool(getattr(args, 'dry_run', False)),
                payload=payload,
            )
        _emit_payload(to_emit, json_output=json_output)
        return 0

    if getattr(args, 'show_rollback_command', None):
        run_id = str(args.show_rollback_command)
        payload = _load_run_payload(root_dir, run_id)
        if json_output:
            to_emit = _audit_json_payload(
                action='show-rollback-command',
                root_dir=root_dir,
                dry_run=bool(getattr(args, 'dry_run', False)),
                payload={
                    'status': 'ok',
                    'rollback_apply_command': str(payload.get('rollback_apply_command') or ''),
                    'checkpoint_id': Path(str(payload.get('rollback_target') or '')).name if payload.get('rollback_target') else None,
                },
            )
            _emit_payload(to_emit, json_output=True)
        else:
            print(str(payload.get('rollback_apply_command') or ''))
        return 0

    return None
