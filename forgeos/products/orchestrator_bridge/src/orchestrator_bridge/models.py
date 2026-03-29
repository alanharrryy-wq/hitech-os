from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrchestratorBridgeState(str, Enum):
    REGISTERED = "registered"
    PREPARED = "prepared"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class WorkflowStep:
    step_id: str
    command: tuple[str, ...]
    timeout_seconds: float


@dataclass(frozen=True)
class WorkflowStepResult:
    step_id: str
    status: str
    return_code: int | None
    duration_ms: int


@dataclass(frozen=True)
class WorkflowRunReport:
    workflow_id: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    timed_out_steps: int
    overall_status: str
    total_duration_ms: int
    generated_at_utc: str
