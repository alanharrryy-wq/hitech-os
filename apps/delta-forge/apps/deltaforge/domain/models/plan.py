from dataclasses import dataclass, field

from domain.models.diff import DiffPreview


@dataclass(slots=True)
class PlanStep:
    step_id: str
    title: str
    detail: str


@dataclass(slots=True)
class FilePlan:
    path: str
    summary: str
    operations: list[PlanStep] = field(default_factory=list)


@dataclass(slots=True)
class PlanResult:
    ok: bool
    summary: str
    files: list[FilePlan] = field(default_factory=list)
    diff_preview: DiffPreview = field(default_factory=lambda: DiffPreview(summary=""))
