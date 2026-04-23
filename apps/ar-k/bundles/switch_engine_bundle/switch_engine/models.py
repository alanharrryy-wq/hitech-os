"""Switch Engine runtime data models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SwitchEntry:
    switch_id: str
    target_type: str
    target_id: str
    default_value: bool


@dataclass(frozen=True)
class ResolutionResult:
    switch_id: str
    target_type: str
    target_id: str
    default_value: bool
    resolved_value: bool
    decision_source: str
    precedence_path: tuple[str, ...]
    justification: str
    override_key: str | None
