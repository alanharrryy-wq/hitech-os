"""Python-first contract definitions for switch outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from contracts.shared_canon import REQUIRED_SWITCH_ARTIFACTS


@dataclass(frozen=True)
class SwitchDecisionRecord:
    switch_id: str
    target_type: str
    target_id: str
    default_value: bool
    resolved_value: bool
    decision_source: str
    precedence_path: tuple[str, ...]
    justification: str
    timestamp: str


@dataclass(frozen=True)
class SwitchTraceRecord:
    switch_id: str
    decision_source: str
    resolved_value: bool
    precedence_path: tuple[str, ...]
    evaluated_override_key: str | None
    warning: str | None = None


@dataclass(frozen=True)
class SwitchSummary:
    execution_id: str
    stage: str
    resolved_count: int
    warning_count: int
    deterministic_hash: str
    artifact_names: tuple[str, ...] = field(default_factory=lambda: tuple(REQUIRED_SWITCH_ARTIFACTS))


def validate_artifact_names(names: list[str]) -> bool:
    return sorted(names) == sorted(REQUIRED_SWITCH_ARTIFACTS)


def registry_shape_note() -> dict[str, Any]:
    return {
        "switch_decision_registry.json": [record.__name__ for record in (SwitchDecisionRecord,)],
        "switch_decision_trace.json": [record.__name__ for record in (SwitchTraceRecord,)],
        "switch_resolution_summary.json": [record.__name__ for record in (SwitchSummary,)],
        "invariants": [
            "sorted by switch_id",
            "one record per switch_id",
            "precedence_path is explicit",
            "canonical input files are read-only",
        ],
    }
