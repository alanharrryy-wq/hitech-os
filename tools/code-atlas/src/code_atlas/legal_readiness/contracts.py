from __future__ import annotations

import os
import re
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
        return Path(self.root or ".")

    def command_preview(self) -> str:
        values = [self.program, *self.args]
        return " ".join(_quote(value) for value in values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _env(name: str, default: str = "") -> str:
    return str(os.environ.get(name, default))


@dataclass(frozen=True)
class LegalPipelineConfig:
    profile: str = "static"
    workers: int = 6
    shards: int = 1
    surface: str = "all"
    include_runtime: bool = False
    allow_partial: bool = True
    output_root: str = field(default_factory=lambda: _env("CODE_ATLAS_OUTPUT_ROOT", "./code-atlas-out"))
    repo_root: str = field(default_factory=lambda: _env("CODE_ATLAS_PROJECT_ROOT", "."))
    code_atlas_root: str = field(default_factory=lambda: _env("CODE_ATLAS_ROOT", "."))
    motors_root: str = field(default_factory=lambda: _env("CODE_ATLAS_MOTORS_ROOT", ""))
    ndc_root: str = field(default_factory=lambda: _env("CODE_ATLAS_NDC_ROOT", ""))
    runtime_root: str = field(default_factory=lambda: _env("CODE_ATLAS_RUNTIME_ROOT", ""))
    runtime_program: str = field(default_factory=lambda: _env("CODE_ATLAS_RUNTIME_PROGRAM", ""))
    runtime_script: str = field(default_factory=lambda: _env("CODE_ATLAS_RUNTIME_SCRIPT", ""))
    run_id: str = ""
    cancel_file: str = ""

    def normalized(self) -> "LegalPipelineConfig":
        workers = max(1, min(18, int(self.workers)))
        shards = max(1, min(18, int(self.shards)))
        profile = str(self.profile or "static").strip().lower()
        if profile not in {"static", "full", "runtime-only", "plan"}:
            raise ValueError(f"UNKNOWN_LEGAL_PROFILE:{profile}")
        surface = str(self.surface or "all").strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}|all", surface):
            raise ValueError(f"INVALID_SURFACE_ID:{surface}")
        return LegalPipelineConfig(
            profile=profile,
            workers=workers,
            shards=shards,
            surface=surface,
            include_runtime=bool(self.include_runtime or profile in {"full", "runtime-only"}),
            allow_partial=bool(self.allow_partial),
            output_root=str(Path(self.output_root or "./code-atlas-out")),
            repo_root=str(Path(self.repo_root or ".")),
            code_atlas_root=str(Path(self.code_atlas_root or ".")),
            motors_root=str(Path(self.motors_root)) if str(self.motors_root).strip() else "",
            ndc_root=str(Path(self.ndc_root)) if str(self.ndc_root).strip() else "",
            runtime_root=str(Path(self.runtime_root)) if str(self.runtime_root).strip() else "",
            runtime_program=str(self.runtime_program or "").strip(),
            runtime_script=str(self.runtime_script or "").strip(),
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
