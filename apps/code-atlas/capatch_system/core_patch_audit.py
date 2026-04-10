#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Compat shim for legacy audit calls. Real ownership lives in capatch_audit/."""

from pathlib import Path
from typing import Any

from capatch_audit import apply_rollback, finalize_run, list_checkpoints, load_run, start_run
from capatch_contracts.operations import READ_ONLY_OPERATION_TYPES
from capatch_contracts.result_status import PATCH_RESULT_STATUS


def _flatten_operations(operations: list[Any]) -> list[Any]:
    items: list[Any] = []
    for operation in list(operations or []):
        nested = getattr(operation, "operations", None)
        if nested:
            items.extend(_flatten_operations(list(nested)))
        else:
            items.append(operation)
    return items


def _hash_file(path_value: Path) -> str | None:
    try:
        import hashlib
        return hashlib.sha256(path_value.read_bytes()).hexdigest()
    except Exception:
        return None


def _operation_rows(ctx: Any, operations: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    root_dir = Path(ctx.root_dir).resolve()
    rows: list[dict[str, Any]] = []
    target_files: list[str] = []
    for operation in _flatten_operations(operations):
        spec = getattr(operation, "spec", None)
        if spec is None:
            continue
        relative_path = str(getattr(spec, "file", "") or "")
        target_path = root_dir / relative_path if relative_path else root_dir
        row = {
            "operation_label": str(getattr(spec, "label", "") or getattr(spec, "type", "op")),
            "operation_type": str(getattr(spec, "type", "op")),
            "target_path": str(target_path),
            "before_hash": _hash_file(target_path),
            "bytes_before": target_path.stat().st_size if target_path.exists() else None,
        }
        rows.append(row)
        if relative_path and relative_path not in target_files:
            target_files.append(relative_path)
    return rows, target_files


def _compat_preflight(rows: list[dict[str, Any]], target_files: list[str]) -> dict[str, Any]:
    mutating = [row for row in rows if row["operation_type"] not in READ_ONLY_OPERATION_TYPES]
    return {
        "ok": True,
        "run_id": None,
        "target_files": target_files,
        "operation_count": len(rows),
        "mutating_operation_count": len(mutating),
        "read_only_operation_count": len(rows) - len(mutating),
        "conflicts": [],
        "path_violations": [],
        "schema_violations": [],
        "syntax_validation_plan": [],
        "risk_summary": {
            "risk_level": "low" if len(mutating) <= 1 else "medium",
            "risk_tier": "safe" if len(mutating) <= 1 else "guarded",
            "compat_source": "core_patch_audit",
        },
    }


def start_patch_run(ctx: Any, operations: list[Any], preview_content_by_target: dict[Any, str]) -> dict[str, Any]:
    rows, target_files = _operation_rows(ctx, operations)
    preflight = _compat_preflight(rows, target_files)
    record = start_run(ctx, preflight, dict(preflight["risk_summary"]))
    return {
        "record": record,
        "rows": rows,
        "preview_content_by_target": dict(preview_content_by_target or {}),
    }


def _build_finalize_results(ctx: Any, state: dict[str, Any], results: list[str], *, patch_status: str) -> list[dict[str, Any]]:
    root_dir = Path(ctx.root_dir).resolve()
    rows = list(state.get("rows") or [])
    finalized: list[dict[str, Any]] = []
    allowed = set(PATCH_RESULT_STATUS)
    patch_status_value = patch_status if patch_status in allowed else "failed"
    for index, row in enumerate(rows):
        target_path = Path(row.get("target_path") or "")
        finalized.append(
            {
                "operation_label": row.get("operation_label") or f"op-{index + 1}",
                "operation_type": row.get("operation_type") or "unknown",
                "target_path": str(target_path),
                "patch_status": patch_status_value,
                "message": results[index] if index < len(results) else patch_status_value,
                "before_hash": row.get("before_hash"),
                "after_hash": _hash_file(target_path),
                "preview_hash": None,
                "bytes_before": row.get("bytes_before"),
                "bytes_after": target_path.stat().st_size if target_path.exists() else None,
                "changed_line_count": 0,
                "support_notes": ["legacy core_patch_audit compat shim"],
            }
        )
    if not rows and root_dir.exists():
        return []
    return finalized


def finalize_patch_run_success(ctx: Any, state: dict[str, Any], results: list[str]) -> dict[str, Any]:
    record = state["record"]
    operation_results = _build_finalize_results(ctx, state, list(results or []), patch_status="applied")
    finalized = finalize_run(record, operation_results, [])
    return {
        "run_id": finalized.run_id,
        "patch_status": finalized.patch_status,
        "system_status": finalized.system_status,
        "rollback_target": finalized.rollback_target,
    }


def finalize_patch_run_failure(ctx: Any, state: dict[str, Any], error: str, *, rollback_applied: bool = True) -> dict[str, Any]:
    record = state["record"]
    record.error = str(error)
    record.patch_status = "rolled_back" if rollback_applied else "failed"
    record.system_status = "rolled_back" if rollback_applied else "failed"
    operation_results = _build_finalize_results(ctx, state, [str(error)], patch_status=record.patch_status)
    finalized = finalize_run(record, operation_results, [])
    return {
        "run_id": finalized.run_id,
        "patch_status": finalized.patch_status,
        "system_status": finalized.system_status,
        "rollback_target": finalized.rollback_target,
        "error": finalized.error,
    }


def list_checkpoint_rows(root_dir: Path) -> list[dict[str, Any]]:
    return list_checkpoints(Path(root_dir).resolve())


def rollback_checkpoint(root_dir: Path, checkpoint_id: str) -> dict[str, Any]:
    return apply_rollback(checkpoint_id=str(checkpoint_id), root_dir=Path(root_dir).resolve())


def rollback_last(root_dir: Path) -> dict[str, Any]:
    rows = list_checkpoints(Path(root_dir).resolve())
    if not rows:
        raise FileNotFoundError("No hay checkpoints para rollback.")
    latest = rows[0]
    return apply_rollback(checkpoint_id=str(latest.get("checkpoint_id")), root_dir=Path(root_dir).resolve())


def load_patch_run(root_dir: Path, run_id: str) -> dict[str, Any]:
    record = load_run(str(run_id), root_dir=Path(root_dir).resolve())
    if record is None:
        raise FileNotFoundError(f"Run no existe: {run_id}")
    return {
        "run_id": record.run_id,
        "schema_version": record.schema_version,
        "started_at": record.started_at,
        "finished_at": record.finished_at,
        "root_dir": record.root_dir,
        "cwd": record.cwd,
        "invocation_mode": record.invocation_mode,
        "patch_status": record.patch_status,
        "system_status": record.system_status,
        "execution_mode": record.execution_mode,
        "git_branch": record.git_branch,
        "git_head": record.git_head,
        "git_dirty_before": record.git_dirty_before,
        "git_dirty_after": record.git_dirty_after,
        "target_files": record.target_files,
        "operation_count": record.operation_count,
        "operation_results": record.operation_results,
        "risk_summary": record.risk_summary,
        "required_verifiers": record.required_verifiers,
        "verifier_results": record.verifier_results,
        "rollback_target": record.rollback_target,
        "baseline_ref": record.baseline_ref,
        "error": record.error,
        "rollback_command": f'python capatch.py --root-dir "{record.root_dir}" --rollback-checkpoint "{Path(record.rollback_target).name}"' if record.rollback_target else None,
    }
