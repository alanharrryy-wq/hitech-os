from __future__ import annotations

import sys
from pathlib import Path

from .contracts import LegalPipelineConfig, LegalStageSpec


def build_legal_stage_registry(config: LegalPipelineConfig) -> list[LegalStageSpec]:
    cfg = config.normalized()
    stages: list[LegalStageSpec] = []
    authority_id = cfg.run_id or "code-atlas-legal"

    if cfg.profile in {"static", "full"}:
        static_root = Path(cfg.motors_root) if cfg.motors_root else Path(cfg.code_atlas_root)
        script = static_root / "motor_legal_evidence.py"
        args = [
            str(script),
            "--profile", "static-baseline",
            "--workers", str(cfg.workers),
            "--run-id", f"{authority_id}-static",
            "--authority-run-id", authority_id,
            "--output-root", cfg.output_root,
            "--repo-root", cfg.repo_root,
        ]
        if cfg.ndc_root:
            args.extend(["--ndc-root", cfg.ndc_root])
        stages.append(
            LegalStageSpec(
                stage_id="configured-static-baseline",
                label="Configured Static Baseline",
                description="Configured source, asset and database-schema metadata collection without database row mutation.",
                root=str(static_root),
                program=sys.executable,
                args=tuple(args),
                expected_prefixes=("legal-static ", "motlegal "),
                required=True,
                enabled=True,
                timeout_seconds=7200,
                proves=(
                    "configured static metadata collection was invoked",
                    "configured database schema metadata collection was invoked without write intent",
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
        runtime_root = Path(cfg.runtime_root) if cfg.runtime_root else Path(cfg.code_atlas_root)
        if not cfg.runtime_program or not cfg.runtime_script:
            stages.append(
                LegalStageSpec(
                    stage_id="configured-runtime-evidence",
                    label="Configured Runtime Evidence",
                    description="Runtime evidence stage is explicit and platform-neutral; a program and script must be configured by the caller.",
                    root=str(runtime_root),
                    program=cfg.runtime_program or "<UNCONFIGURED>",
                    args=(),
                    expected_prefixes=("legal-runtime ",),
                    required=not cfg.allow_partial,
                    enabled=False,
                    sensitivity_class="RESTRICTED_REDACTED",
                    proves=(),
                    does_not_prove=("runtime evidence while the stage is unconfigured", "production certification", "legal compliance"),
                )
            )
        else:
            runtime_script = Path(cfg.runtime_script)
            if not runtime_script.is_absolute():
                runtime_script = runtime_root / runtime_script
            runtime_args = [str(runtime_script), "--surface", cfg.surface, "--workers", str(cfg.workers), "--shards", str(cfg.shards)]
            if cfg.allow_partial:
                runtime_args.append("--allow-partial")
            stages.append(
                LegalStageSpec(
                    stage_id="configured-runtime-evidence",
                    label="Configured Runtime Evidence",
                    description="Caller-configured runtime evidence collection with no platform-specific executable assumed by Code Atlas.",
                    root=str(runtime_root),
                    program=cfg.runtime_program,
                    args=tuple(runtime_args),
                    expected_prefixes=("legal-runtime ",),
                    required=not cfg.allow_partial,
                    enabled=True,
                    timeout_seconds=14400,
                    sensitivity_class="RESTRICTED_REDACTED",
                    proves=("fresh runtime observation was requested from the configured adapter",),
                    does_not_prove=("production certification", "IP ownership", "legal compliance", "data privacy compliance"),
                )
            )

    return stages
