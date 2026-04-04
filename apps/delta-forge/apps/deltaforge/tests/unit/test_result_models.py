from __future__ import annotations

from domain.models.process_report import ProcessReport
from domain.models.results import ApplyResult, RefreshResult, RollbackResult, ValidationIssue, ValidationResult


def test_validation_result_exposes_common_backend_fields() -> None:
    result = ValidationResult(
        ok=False,
        status="invalid",
        summary="bad ops",
        warnings=["w1"],
        errors=["e1"],
        touched_files=["a.py"],
        duration_ms=12,
        process=ProcessReport(engine_name="local", mode="validate"),
        issues=[ValidationIssue(severity="error", message="missing")],
        operations_count=3,
    )

    payload = result.as_dict()
    assert payload["ok"] is False
    assert payload["status"] == "invalid"
    assert payload["errors"] == ["e1"]
    assert result.operations_count == 3


def test_apply_and_rollback_results_keep_rollover_metadata() -> None:
    apply_result = ApplyResult(
        ok=True,
        status="applied",
        summary="ok",
        rollback_token="tok-1",
        backups=[{"original_path": "a", "backup_path": "b"}],
    )
    rollback_result = RollbackResult(
        ok=True,
        status="rolled_back",
        summary="restored",
        rollback_token="tok-1",
        restored_paths=["a"],
    )

    assert apply_result.rollback_token == "tok-1"
    assert apply_result.backups[0]["backup_path"] == "b"
    assert rollback_result.restored_paths == ["a"]


def test_refresh_result_accepts_metadata_payload() -> None:
    result = RefreshResult(
        ok=True,
        status="ok",
        summary="refreshed",
        metadata={"operation_count": 2},
    )

    assert result.metadata["operation_count"] == 2
