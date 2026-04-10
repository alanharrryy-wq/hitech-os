from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PreflightReport:
    ok: bool
    run_id: str
    target_files: list[str]
    operation_count: int
    mutating_operation_count: int
    read_only_operation_count: int
    conflicts: list[dict[str, Any]]
    path_violations: list[dict[str, Any]]
    schema_violations: list[dict[str, Any]]
    syntax_validation_plan: list[dict[str, Any]]
    risk_summary: dict[str, Any]


@dataclass(slots=True)
class OperationResult:
    operation_label: str
    operation_type: str
    target_path: str
    patch_status: str
    message: str
    before_hash: str | None
    after_hash: str | None
    preview_hash: str | None
    bytes_before: int | None
    bytes_after: int | None
    changed_line_count: int
    support_notes: list[str]
