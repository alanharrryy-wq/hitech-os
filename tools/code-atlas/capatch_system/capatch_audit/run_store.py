from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .history import append_history_event
from .manifest import (
    PatchRunRecord,
    make_patch_run_record,
    normalize_operation_result,
    patch_run_record_to_dict,
    utc_now_iso,
)
from .renderers import ensure_report_tree, read_json, render_patch_run_md, write_json, write_text
from .telemetry import build_environment_fingerprint


_CHECKPOINT_META_SCHEMA_VERSION = "1.1.0"


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
    if all(status == "noop" for status in statuses):
        return "noop"
    if all(status in {"noop", "skipped"} for status in statuses):
        return "skipped"
    return current_status


def _compute_system_status(verifier_results: list[dict[str, Any]], current_status: str, patch_status: str) -> str:
    if current_status == "rolled_back":
        return current_status
    if patch_status == "failed":
        return "failed"
    if not verifier_results:
        return current_status
    oks = [bool(item.get("ok")) for item in verifier_results]
    severities = [str(item.get("severity_if_failed") or "").lower() for item in verifier_results if not bool(item.get("ok"))]
    if any(severity in {"high", "critical", "blocker"} for severity in severities):
        return "failed"
    if any(not ok for ok in oks):
        return "caution"
    return "verified"


def start_run(ctx: Any, preflight: Any, risk_summary: dict[str, Any]) -> PatchRunRecord:
    root_dir = Path(getattr(ctx, "root_dir", os.getcwd())).expanduser().resolve()
    ensure_report_tree(root_dir)
    run_id = _build_run_id(ctx)
    record = make_patch_run_record(
        run_id=run_id,
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
        trace_id=str(getattr(ctx, "trace_id", run_id)),
        actor=os.environ.get("USER") or os.environ.get("USERNAME"),
    )
    record.report_refs = {
        "json": str(_record_path(root_dir, record.run_id)),
        "md": str(_record_md_path(root_dir, record.run_id)),
    }
    record.environment_fingerprint = build_environment_fingerprint(root_dir)
    write_json(_record_path(root_dir, record.run_id), patch_run_record_to_dict(record))
    write_text(_record_md_path(root_dir, record.run_id), render_patch_run_md(record))
    checkpoint_target = record.rollback_target
    if checkpoint_target:
        checkpoint_path = Path(checkpoint_target)
        checkpoint_id = checkpoint_path.name
        write_json(
            _checkpoint_meta_path(root_dir, checkpoint_id),
            {
                "schema_version": _CHECKPOINT_META_SCHEMA_VERSION,
                "checkpoint_id": checkpoint_id,
                "checkpoint_path": str(checkpoint_path),
                "root_dir": str(root_dir),
                "run_id": record.run_id,
                "trace_id": record.trace_id,
                "target_files": list(record.target_files),
                "created_at": record.started_at,
                "status": "ready",
                "report_refs": dict(record.report_refs),
            },
        )
    return record


def finalize_run(record: PatchRunRecord, operation_results: list[Any], verifier_results: list[dict[str, Any]]) -> PatchRunRecord:
    root_dir = Path(record.root_dir).resolve()
    ensure_report_tree(root_dir)
    normalized_results = [normalize_operation_result(item, index=index) for index, item in enumerate(operation_results)]
    record.operation_results = normalized_results
    record.verifier_results = [dict(item) for item in list(verifier_results or []) if isinstance(item, dict)]
    record.finished_at = utc_now_iso()
    record.patch_status = _compute_patch_status(normalized_results, record.patch_status)
    record.git_dirty_after = _git_dirty(root_dir)
    record.system_status = _compute_system_status(record.verifier_results, record.system_status, record.patch_status)
    if not record.required_verifiers:
        record.required_verifiers = [str(item.get("verifier_id")) for item in record.verifier_results if item.get("verifier_id")]
    record.report_refs = {
        "json": str(_record_path(root_dir, record.run_id)),
        "md": str(_record_md_path(root_dir, record.run_id)),
    }
    record.environment_fingerprint = build_environment_fingerprint(root_dir)
    write_json(_record_path(root_dir, record.run_id), patch_run_record_to_dict(record))
    write_text(_record_md_path(root_dir, record.run_id), render_patch_run_md(record))
    append_history_event(
        root_dir,
        {
            "timestamp": record.finished_at,
            "event_type": "patch-run",
            "run_id": record.run_id,
            "checkpoint_id": Path(record.rollback_target).name if record.rollback_target else None,
            "trace_id": record.trace_id,
            "status": record.patch_status,
            "system_status": record.system_status,
            "detail": record.error or f"system_status={record.system_status}",
            "source_command": record.invocation_mode,
            "actor": record.actor,
            "report_refs": dict(record.report_refs),
        },
    )
    return record


def load_run(run_id: str, *, root_dir: Path | None = None) -> PatchRunRecord | None:
    root_dir = Path(root_dir or os.getcwd()).resolve()
    payload = read_json(_record_path(root_dir, run_id), None)
    if not isinstance(payload, dict):
        return None
    payload.setdefault("trace_id", run_id)
    payload.setdefault("report_refs", {"json": str(_record_path(root_dir, run_id)), "md": str(_record_md_path(root_dir, run_id))})
    payload.setdefault("environment_fingerprint", build_environment_fingerprint(root_dir))
    payload.setdefault("actor", None)
    return PatchRunRecord(**payload)


def list_checkpoints(root_dir: Path) -> list[dict[str, Any]]:
    root_dir = Path(root_dir).resolve()
    directory = root_dir / "reports/checkpoints"
    rows: list[dict[str, Any]] = []
    for path_value in sorted(directory.glob("*.json"), reverse=True):
        payload = read_json(path_value, None)
        if isinstance(payload, dict):
            rows.append(payload)
    rows.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return rows
