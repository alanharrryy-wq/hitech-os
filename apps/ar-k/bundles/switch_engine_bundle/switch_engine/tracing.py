"""Trace helpers for resolution outputs."""

from __future__ import annotations

from contracts.artifact_contracts import SwitchSummary


def build_summary(execution_id: str, resolved_count: int, warning_count: int, deterministic_hash: str) -> dict[str, object]:
    summary = SwitchSummary(
        execution_id=execution_id,
        stage="stage_03_switch_resolve",
        resolved_count=resolved_count,
        warning_count=warning_count,
        deterministic_hash=deterministic_hash,
    )
    return {
        "execution_id": summary.execution_id,
        "stage": summary.stage,
        "resolved_count": summary.resolved_count,
        "warning_count": summary.warning_count,
        "deterministic_hash": summary.deterministic_hash,
        "artifact_names": list(summary.artifact_names),
    }
