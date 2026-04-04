from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PlanStepPreview:
    step_id: str
    label: str
    operation_type: str
    file_path: str
    preview: str
    risk: str = "low"
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PlanFilePreview:
    file_path: str
    operations_count: int
    summary: str
    steps: list[PlanStepPreview] = field(default_factory=list)
