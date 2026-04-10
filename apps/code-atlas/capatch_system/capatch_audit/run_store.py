from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .history import append_history_event
from .manifest import PatchRunRecord, make_patch_run_record, patch_run_record_to_dict, utc_now_iso
from .renderers import ensure_report_tree, read_json, render_patch_run_md, write_json, write_text


def _run_git(root_dir: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root_dir), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    output = completed.stdout.strip()
    return output or None


def _git_dirty(root_dir: Path) -> bool:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root_dir), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return False
    return bool(completed.stdout.strip())


def _build_run_id(ctx: Any) -> str:
    run_id = getattr(ctx, "run_id", None)
    if run_id:
        return str(run_id)
    return f"patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _extract_preflight_list(preflight: Any, field_name: str) -> list[Any]:
    value = getattr(preflight, field_name, None)
    if value is None and isinstance(preflight, dict):
        value = preflight.get(field_name)
    return list(value or [])


def _extract_preflight_value(preflight: Any, field_name: str, default: Any) -> Any:
    value = getattr(preflight, field_name, None)
    if value is None and isinstance(preflight, dict):
        value = preflight.get(field_name, default)
    return default if value is None else value


def _record_path(root_dir: Path, run_id: str) -> Path:
    return Path(root_dir).resolve() / "reports/patch_runs" / f"{run_id}.json"


def _record_md_path(root_dir: Path, run_id: str) -> Path:
    return Path(root_dir).resolve() / "reports/patch_runs" / f"{run_id}.md"


def _checkpoint_meta_path(root_dir: Path, checkpoint_id: str) -> Path:
    return Path(root_dir).resolve() / "reports/checkpoints" / f"{checkpoint_id}.json"


def _compute_patch_status(operation_results: list[dict[str, Any]], current_status: str) -> str:
    if current_status == "rolled_back":
        return current_status
    statuses = [str(item.get("patch_status") or "") for item in operation_results]
    if not statuses:
        return current_status
    if any(status == "failed" for status in statuses):
        return "failed"
    if any(status == "applied" for status in statuses):
        return "applied"
    if statuses and all(status == "noop" for status in statuses):
        return "noop"
    if statuses and all(status == "skipped" for status in statuses):
        return "skipped"
    return current_status


def _compute_system_status(verifier_results: list[dict[str, Any]], current_status: str, patch_status: str) -> str:
    if current_status == "rolled_back" or patch_status == "rolled_back":
        return "rolled_back"
    if current_status == "failed" and not verifier_results:
        return "failed"
    if not verifier_results:
        return current_status if current_status in {"failed", "caution"} else "not_verified"
    oks = [bool(item.get("ok")) for item in verifier_results]
    if all(oks):
        return "verified"
    if any(not ok for ok in oks):
        return "failed"
    return current_status


def start_run(ctx: Any, preflight: Any, risk_summary: dict[str, Any]) -> PatchRunRecord:
    root_dir = Path(getattr(ctx, "root_dir", os.getcwd())).expanduser().resolve()
    ensure_report_tree(root_dir)
    record = make_patch_run_record(
        run_id=_build_run_id(ctx),
        root_dir=root_dir,
        cwd=Path(os.getcwd()).resolve(),
        invocation_mode=str(getattr(ctx, "invocation_mode", "patch-run")),
        execution_mode=str(getattr(ctx, "invocation_mode", "patch-run")),
        target_files=[str(item) for item in _extract_preflight_list(preflight, "target_files")],
        operation_count=int(_extract_preflight_value(preflight, "operation_count", 0)),
        risk_summary=dict(risk_summary or {}),
        rollback_target=str(getattr(ctx, "checkpoint_dir", "")) or None,
        git_branch=_run_git(root_dir, "rev-parse", "--abbrev-ref", "HEAD"),
        git_head=_run_git(root_dir, "rev-parse", "HEAD"),
        git_dirty_before=_git_dirty(root_dir),
    )
    write_json(_record_path(root_dir, record.run_id), patch_run_record_to_dict(record))
    write_text(_record_md_path(root_dir, record.run_id), render_patch_run_md(record))
    checkpoint_target = record.rollback_target
    if checkpoint_target:
        checkpoint_path = Path(checkpoint_target)
        checkpoint_id = checkpoint_path.name
        write_json(
            _checkpoint_meta_path(root_dir, checkpoint_id),
            {
                "checkpoint_id": checkpoint_id,
                "checkpoint_path": str(checkpoint_path),
                "root_dir": str(root_dir),
                "run_id": record.run_id,
                "target_files": list(record.target_files),
                "created_at": record.started_at,
            },
        )
    return record


def finalize_run(record: PatchRunRecord, operation_results: list[Any], verifier_results: list[dict[str, Any]]) -> PatchRunRecord:
    root_dir = Path(record.root_dir).resolve()
    ensure_report_tree(root_dir)
    normalized_results: list[dict[str, Any]] = []
    for item in operation_results:
        if isinstance(item, dict):
            normalized_results.append(dict(item))
        else:
            normalized_results.append({
                "operation_label": getattr(item, "operation_label", "unknown"),
                "operation_type": getattr(item, "operation_type", "unknown"),
                "target_path": getattr(item, "target_path", ""),
                "patch_status": getattr(item, "patch_status", "skipped"),
                "message": getattr(item, "message", ""),
                "before_hash": getattr(item, "before_hash", None),
                "after_hash": getattr(item, "after_hash", None),
                "preview_hash": getattr(item, "preview_hash", None),
                "bytes_before": getattr(item, "bytes_before", None),
                "bytes_after": getattr(item, "bytes_after", None),
                "changed_line_count": getattr(item, "changed_line_count", 0),
                "support_notes": list(getattr(item, "support_notes", [])),
            })
    record.operation_results = normalized_results
    record.verifier_results = [dict(item) for item in verifier_results]
    record.finished_at = utc_now_iso()
    record.patch_status = _compute_patch_status(normalized_results, record.patch_status)
    record.git_dirty_after = _git_dirty(root_dir)
    record.system_status = _compute_system_status(record.verifier_results, record.system_status, record.patch_status)
    write_json(_record_path(root_dir, record.run_id), patch_run_record_to_dict(record))
    write_text(_record_md_path(root_dir, record.run_id), render_patch_run_md(record))
    append_history_event(
        root_dir,
        {
            "timestamp": record.finished_at,
            "event_type": "patch-run",
            "run_id": record.run_id,
            "checkpoint_id": Path(record.rollback_target).name if record.rollback_target else None,
            "status": record.patch_status,
            "detail": record.error or f"system_status={record.system_status}",
        },
    )
    return record


def load_run(run_id: str, *, root_dir: Path | None = None) -> PatchRunRecord | None:
    root_dir = Path(root_dir or os.getcwd()).resolve()
    payload = read_json(_record_path(root_dir, run_id), None)
    if not isinstance(payload, dict):
        return None
    return PatchRunRecord(**payload)


def list_checkpoints(root_dir: Path) -> list[dict[str, Any]]:
    root_dir = Path(root_dir).resolve()
    directory = root_dir / "reports/checkpoints"
    rows: list[dict[str, Any]] = []
    for path_value in sorted(directory.glob("*.json"), reverse=True):
        payload = read_json(path_value, None)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows
