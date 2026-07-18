from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LegalStageSpec:
    stage_id: str
    label: str
    description: str
    root: str
    program: str
    args: tuple[str, ...]
    expected_prefixes: tuple[str, ...]
    required: bool = True
    enabled: bool = True
    timeout_seconds: int = 3600
    mutability: str = "READ_ONLY"
    sensitivity_class: str = "INTERNAL_RESTRICTED"
    proves: tuple[str, ...] = ()
    does_not_prove: tuple[str, ...] = ()

    @property
    def root_path(self) -> Path:
        return Path(self.root)

    def command_preview(self) -> str:
        values = [self.program, *self.args]
        return " ".join(_quote(value) for value in values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LegalPipelineConfig:
    profile: str = "static"
    workers: int = 6
    shards: int = 1
    surface: str = "all"
    include_runtime: bool = False
    allow_partial: bool = True
    output_root: str = r"F:\descargasf"
    repo_root: str = r"F:\repos\hitech-os"
    code_atlas_root: str = r"F:\repos\hitech-os\tools\code-atlas"
    motors_root: str = r"F:\PRISMA_CTX\MOTORES"
    ndc_root: str = r"F:\PRISMA_CTX\NDC"
    mamastrophic_root: str = r"F:\repos\hitech-os\tools\Plawright Mamastrophic"
    run_id: str = ""
    cancel_file: str = ""

    def normalized(self) -> "LegalPipelineConfig":
        workers = max(1, min(18, int(self.workers)))
        shards = max(1, min(18, int(self.shards)))
        profile = str(self.profile or "static").strip().lower()
        if profile not in {"static", "full", "runtime-only", "plan"}:
            raise ValueError(f"UNKNOWN_LEGAL_PROFILE:{profile}")
        surface = str(self.surface or "all").strip().lower()
        if surface not in {"all", "chart-lab", "web", "tablet", "pc", "mobile", "control-center"}:
            raise ValueError(f"UNKNOWN_SURFACE:{surface}")
        return LegalPipelineConfig(
            profile=profile,
            workers=workers,
            shards=shards,
            surface=surface,
            include_runtime=bool(self.include_runtime or profile in {"full", "runtime-only"}),
            allow_partial=bool(self.allow_partial),
            output_root=str(Path(self.output_root)),
            repo_root=str(Path(self.repo_root)),
            code_atlas_root=str(Path(self.code_atlas_root)),
            motors_root=str(Path(self.motors_root)),
            ndc_root=str(Path(self.ndc_root)),
            mamastrophic_root=str(Path(self.mamastrophic_root)),
            run_id=str(self.run_id or ""),
            cancel_file=str(Path(self.cancel_file)) if str(self.cancel_file or "").strip() else "",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.normalized())


@dataclass
class LegalStageResult:
    stage_id: str
    label: str
    status: str
    exit_code: int | None = None
    started_at: str = ""
    finished_at: str = ""
    artifact: dict[str, Any] | None = None
    stdout_log: str = ""
    stderr_log: str = ""
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(ch.isspace() for ch in text) or '"' in text:
        return '"' + text.replace('"', '\\"') + '"'
    return text
