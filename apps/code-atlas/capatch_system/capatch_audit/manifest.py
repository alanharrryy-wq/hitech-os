from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from capatch_contracts.result_status import PATCH_RESULT_STATUS, SYSTEM_RESULT_STATUS
from capatch_contracts.versions import PATCH_RUN_SCHEMA_VERSION


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
    operation_results: list[Any] = field(default_factory=list)
    risk_summary: dict[str, Any] = field(default_factory=dict)
    required_verifiers: list[str] = field(default_factory=list)
    verifier_results: list[dict[str, Any]] = field(default_factory=list)
    rollback_target: str | None = None
    baseline_ref: str | None = None
    error: str | None = None


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


def make_patch_run_record(*, run_id: str, root_dir: Path, cwd: Path, invocation_mode: str, execution_mode: str, target_files: list[str], operation_count: int, risk_summary: dict[str, Any], rollback_target: str | None, git_branch: str | None, git_head: str | None, git_dirty_before: bool) -> PatchRunRecord:
    return PatchRunRecord(
        run_id=run_id,
        schema_version=PATCH_RUN_SCHEMA_VERSION,
        started_at=utc_now_iso(),
        finished_at=None,
        root_dir=str(root_dir),
        cwd=str(cwd),
        invocation_mode=invocation_mode,
        patch_status="skipped",
        system_status="not_verified",
        execution_mode=execution_mode,
        git_branch=git_branch,
        git_head=git_head,
        git_dirty_before=git_dirty_before,
        git_dirty_after=git_dirty_before,
        target_files=list(target_files),
        operation_count=int(operation_count),
        operation_results=[],
        risk_summary=dict(risk_summary or {}),
        required_verifiers=list(risk_summary.get("required_verifiers") or []),
        verifier_results=[],
        rollback_target=rollback_target,
        baseline_ref=None,
        error=None,
    )


def validate_patch_run_record(record: PatchRunRecord) -> None:
    if record.patch_status not in _ALLOWED_PATCH:
        raise ValueError(f"Invalid patch_status: {record.patch_status}")
    if record.system_status not in _ALLOWED_SYSTEM:
        raise ValueError(f"Invalid system_status: {record.system_status}")


def patch_run_record_to_dict(record: PatchRunRecord) -> dict[str, Any]:
    validate_patch_run_record(record)
    return _normalize_jsonable(record)
