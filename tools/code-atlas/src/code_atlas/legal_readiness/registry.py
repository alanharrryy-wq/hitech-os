from __future__ import annotations

import sys
from pathlib import Path

from .contracts import LegalPipelineConfig, LegalStageSpec


def build_legal_stage_registry(config: LegalPipelineConfig) -> list[LegalStageSpec]:
    cfg = config.normalized()
    stages: list[LegalStageSpec] = []
    authority_id = cfg.run_id or "code-atlas-legal"

    if cfg.profile in {"static", "full"}:
        stages.append(
            LegalStageSpec(
                stage_id="ctx-static-baseline",
                label="CTX Legal Static Baseline",
                description="Motor inventory, source/asset metadata and database schema metadata without rows.",
                root=cfg.motors_root,
                program=sys.executable,
                args=(
                    str(Path(cfg.motors_root) / "motor_legal_evidence.py"),
                    "--profile", "static-baseline",
                    "--workers", str(cfg.workers),
                    "--run-id", f"{authority_id}-ctx",
                    "--authority-run-id", authority_id,
                    "--output-root", cfg.output_root,
                    "--repo-root", cfg.repo_root,
                    "--ndc-root", cfg.ndc_root,
                ),
                expected_prefixes=("motlegal ",),
                required=True,
                enabled=True,
                timeout_seconds=7200,
                proves=(
                    "static source and asset metadata was collected",
                    "SQLite schema metadata was collected without rows",
                ),
                does_not_prove=(
                    "IP ownership",
                    "open-source obligations resolved",
                    "runtime behavior",
                    "legal compliance",
                ),
            )
        )

    if cfg.include_runtime or cfg.profile == "runtime-only":
        runtime_args = [
            "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(Path(cfg.mamastrophic_root) / "LEGAL_RUN.ps1"),
            "-Surface", cfg.surface,
            "-Workers", str(cfg.workers),
            "-Shards", str(cfg.shards),
        ]
        if cfg.allow_partial:
            runtime_args.append("-AllowPartial")
        stages.append(
            LegalStageSpec(
                stage_id="mamastrophic-runtime-evidence",
                label="Mamastrophic Legal Runtime Evidence",
                description="Sequential per-surface runtime evidence with redaction and chain of custody.",
                root=cfg.mamastrophic_root,
                program="powershell.exe",
                args=tuple(runtime_args),
                expected_prefixes=("mamlegal ",),
                required=not cfg.allow_partial,
                enabled=True,
                timeout_seconds=14400,
                sensitivity_class="RESTRICTED_REDACTED",
                proves=("fresh runtime observation was captured for responding surfaces",),
                does_not_prove=(
                    "production certification",
                    "IP ownership",
                    "legal compliance",
                    "data privacy compliance",
                ),
            )
        )

    return stages
