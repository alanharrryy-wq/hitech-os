from __future__ import annotations

from dataclasses import dataclass, field

from domain.models.diff import DiffPreview
from domain.models.process_report import ProcessReport


@dataclass(slots=True)
class PlanStep:
    step_id: str
    title: str
    detail: str
    preview: str = ""
    risk: str = "low"
    file_path: str = ""
    operation_type: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FilePlan:
    path: str
    summary: str
    operations: list[PlanStep] = field(default_factory=list)
    risk: str = "low"
    warnings: list[str] = field(default_factory=list)
    diff_summary: str = ""


@dataclass(slots=True)
class PlanResult:
    ok: bool
    summary: str
    files: list[FilePlan] = field(default_factory=list)
    diff_preview: DiffPreview = field(default_factory=lambda: DiffPreview(summary=""))
    status: str = "ok"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    touched_files: list[str] = field(default_factory=list)
    duration_ms: int = 0
    process: ProcessReport | None = None

    @property
    def steps(self) -> list[PlanStep]:
        flattened: list[PlanStep] = []
        for item in self.files:
            flattened.extend(item.operations)
        return flattened
