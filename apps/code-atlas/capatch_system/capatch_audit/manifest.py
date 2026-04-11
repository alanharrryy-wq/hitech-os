from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from capatch_contracts.result_status import PATCH_RESULT_STATUS, SYSTEM_RESULT_STATUS
from capatch_contracts.versions import PATCH_RUN_SCHEMA_VERSION

from .telemetry import build_environment_fingerprint


@dataclass(slots=True)
class PatchRunRecord:
    run_id: str
    schema_version: str
    started_at: str
    finished_at: str | None
    root_dir: str
    cwd: str
    invocation_mode: str
    patch_status: str
    system_status: str
    execution_mode: str
    git_branch: str | None
    git_head: str | None
    git_dirty_before: bool
    git_dirty_after: bool
    target_files: list[str]
    operation_count: int
    operation_results: list[dict[str, Any]] = field(default_factory=list)
    risk_summary: dict[str, Any] = field(default_factory=dict)
    required_verifiers: list[str] = field(default_factory=list)
    verifier_results: list[dict[str, Any]] = field(default_factory=list)
    rollback_target: str | None = None
    baseline_ref: str | None = None
    error: str | None = None
    trace_id: str | None = None
    transaction_id: str | None = None
    transaction_journal: str | None = None
    transaction_phase: str | None = None
    transaction_status: str | None = None
    lifecycle: list[dict[str, Any]] = field(default_factory=list)
    verification_outcome: str | None = None
    final_state: str | None = None
    rollback_triggered: bool = False
    rollback_outcome: str | None = None
    report_refs: dict[str, str] = field(default_factory=dict)
    environment_fingerprint: dict[str, Any] = field(default_factory=dict)
    actor: str | None = None


_ALLOWED_PATCH = set(PATCH_RESULT_STATUS)
_ALLOWED_SYSTEM = set(SYSTEM_RESULT_STATUS)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _normalize_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _normalize_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _normalize_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_jsonable(item) for item in value]
    return value


def normalize_operation_result(item: Any, *, index: int = 0) -> dict[str, Any]:
    if isinstance(item, dict):
        payload = dict(item)
    else:
        payload = {
            "operation_label": getattr(item, "operation_label", None),
            "operation_type": getattr(item, "operation_type", None),
            "target_path": getattr(item, "target_path", None),
            "patch_status": getattr(item, "patch_status", None),
            "message": getattr(item, "message", None),
            "before_hash": getattr(item, "before_hash", None),
            "after_hash": getattr(item, "after_hash", None),
            "preview_hash": getattr(item, "preview_hash", None),
            "bytes_before": getattr(item, "bytes_before", None),
            "bytes_after": getattr(item, "bytes_after", None),
            "changed_line_count": getattr(item, "changed_line_count", 0),
            "support_notes": list(getattr(item, "support_notes", []) or []),
        }
    normalized = {
        "operation_label": str(payload.get("operation_label") or f"op-{index + 1}"),
        "operation_type": str(payload.get("operation_type") or "unknown"),
        "target_path": str(payload.get("target_path") or ""),
        "patch_status": str(payload.get("patch_status") or "skipped"),
        "message": str(payload.get("message") or ""),
        "before_hash": payload.get("before_hash"),
        "after_hash": payload.get("after_hash"),
        "preview_hash": payload.get("preview_hash"),
        "bytes_before": payload.get("bytes_before"),
        "bytes_after": payload.get("bytes_after"),
        "changed_line_count": int(payload.get("changed_line_count") or 0),
        "support_notes": [str(note) for note in list(payload.get("support_notes") or [])],
    }
    if normalized["patch_status"] not in _ALLOWED_PATCH:
        normalized["patch_status"] = "failed"
    return _normalize_jsonable(normalized)


def make_patch_run_record(
    *,
    run_id: str,
    root_dir: Path,
    cwd: Path,
    invocation_mode: str,
    execution_mode: str,
    target_files: list[str],
    operation_count: int,
    risk_summary: dict[str, Any],
    rollback_target: str | None,
    git_branch: str | None,
    git_head: str | None,
    git_dirty_before: bool,
    trace_id: str | None = None,
    actor: str | None = None,
) -> PatchRunRecord:
    normalized_targets = [str(item) for item in list(target_files or [])]
    normalized_verifiers = [str(item) for item in list((risk_summary or {}).get("required_verifiers") or []) if str(item)]
    resolved_root = Path(root_dir).resolve()
    return PatchRunRecord(
        run_id=str(run_id),
        schema_version=PATCH_RUN_SCHEMA_VERSION,
        started_at=utc_now_iso(),
        finished_at=None,
        root_dir=str(resolved_root),
        cwd=str(Path(cwd).resolve()),
        invocation_mode=str(invocation_mode or "patch-run"),
        patch_status="skipped",
        system_status="not_verified",
        execution_mode=str(execution_mode or invocation_mode or "patch-run"),
        git_branch=str(git_branch) if git_branch else None,
        git_head=str(git_head) if git_head else None,
        git_dirty_before=bool(git_dirty_before),
        git_dirty_after=bool(git_dirty_before),
        target_files=normalized_targets,
        operation_count=max(0, int(operation_count)),
        operation_results=[],
        risk_summary=_normalize_jsonable(dict(risk_summary or {})),
        required_verifiers=normalized_verifiers,
        verifier_results=[],
        rollback_target=str(rollback_target) if rollback_target else None,
        baseline_ref=None,
        error=None,
        trace_id=str(trace_id or run_id),
        transaction_id=None,
        transaction_journal=None,
        transaction_phase=None,
        transaction_status=None,
        lifecycle=[],
        verification_outcome=None,
        final_state=None,
        rollback_triggered=False,
        rollback_outcome=None,
        report_refs={},
        environment_fingerprint=build_environment_fingerprint(resolved_root),
        actor=str(actor) if actor else None,
    )


def validate_patch_run_record(record: PatchRunRecord) -> None:
    if record.patch_status not in _ALLOWED_PATCH:
        raise ValueError(f"Invalid patch_status: {record.patch_status}")
    if record.system_status not in _ALLOWED_SYSTEM:
        raise ValueError(f"Invalid system_status: {record.system_status}")


def patch_run_record_to_dict(record: PatchRunRecord) -> dict[str, Any]:
    validate_patch_run_record(record)
    return _normalize_jsonable(record)
