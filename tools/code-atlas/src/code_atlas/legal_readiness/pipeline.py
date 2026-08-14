from __future__ import annotations

import json
import os
import subprocess
import traceback
from pathlib import Path
from typing import Any, Callable

from .artifacts import discover_stage_artifact, manifest_status, snapshot_zip_files
from .authority import validate_authority_chain
from .contracts import LegalPipelineConfig, LegalStageResult
from .io_utils import (
    artifact_hash_file,
    git_snapshot,
    local_stamp,
    now_iso,
    package_directory,
    run_token,
    safe_remove_stage,
    write_json,
    write_text,
)
from .registry import build_legal_stage_registry


ProgressCallback = Callable[[dict[str, Any]], None] | None
OutputCallback = Callable[[str, str, str], None] | None


def _emit(callback: ProgressCallback, percent: int, label: str, **details: Any) -> None:
    payload = {"percent": max(0, min(100, int(percent))), "label": label, "details": details}
    print("CODE_ATLAS_LEGAL_PROGRESS " + json.dumps(payload, ensure_ascii=False), flush=True)
    if callback:
        callback(payload)


def _cancel_requested(config: LegalPipelineConfig) -> bool:
    raw = str(config.cancel_file or "").strip()
    if not raw:
        return False
    try:
        return Path(raw).exists()
    except Exception:
        return False


def _stream_process(
    *,
    stage_id: str,
    program: str,
    args: tuple[str, ...],
    root: Path,
    stdout_path: Path,
    stderr_path: Path,
    timeout_seconds: int,
    output_callback: OutputCallback,
) -> int:
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.Popen(
        [program, *args],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        shell=False,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        stderr = (stderr or "") + "\nCODE_ATLAS_LEGAL_STAGE_TIMEOUT"
        exit_code = 124
    else:
        exit_code = int(process.returncode or 0)

    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    if output_callback:
        if stdout:
            output_callback(stage_id, "stdout", stdout)
        if stderr:
            output_callback(stage_id, "stderr", stderr)
    return exit_code


def _artifact_success(artifact: dict[str, Any] | None, *, allow_partial: bool) -> tuple[bool, str]:
    if artifact is None:
        return False, "MISSING_STAGE_ARTIFACT"
    status = manifest_status(artifact).upper()
    if not status:
        return False, "ARTIFACT_MANIFEST_STATUS_MISSING"
    if status.startswith("PASS") or status in {"PARTIAL", "PARTIAL_EVIDENCE_NEEDS_REVIEW"}:
        return True, status
    if allow_partial and "PARTIAL" in status:
        return True, status
    return False, status


def run_pipeline(
    config: LegalPipelineConfig,
    *,
    progress_callback: ProgressCallback = None,
    output_callback: OutputCallback = None,
) -> dict[str, Any]:
    cfg = config.normalized()
    output_root = Path(cfg.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = cfg.run_id or f"catlegal-{run_token()}"
    stage = output_root / f".catlegal-{run_id}-{os.getpid()}"
    result_zip = output_root / f"catlegal {local_stamp()} result.zip"
    fail_zip = output_root / f"catlegal {local_stamp()} fail.zip"
    safe_remove_stage(stage)
    stage.mkdir(parents=True)
    logs = stage / "logs"
    reports = stage / "reports"
    logs.mkdir()
    reports.mkdir()

    started_at = now_iso()
    git_before = git_snapshot(Path(cfg.repo_root))
    authority = validate_authority_chain(output_root)
    write_json(reports / "AUTHORITY_CHAIN.json", authority)
    write_json(reports / "GIT_BEFORE.json", git_before)

    pipeline_manifest: dict[str, Any] = {
        "schema": "CODE_ATLAS_LEGAL_PIPELINE_RUN_V2",
        "version": "catlegal-neutral-v2",
        "run_id": run_id,
        "profile": cfg.profile,
        "status": "RUNNING",
        "started_at": started_at,
        "finished_at": None,
        "config": cfg.to_dict(),
        "external_concurrency": 1,
        "internal_workers": cfg.workers,
        "internal_shards": cfg.shards,
        "cancel_file": cfg.cancel_file or None,
        "authority_status": authority["status"],
        "stage_results": [],
        "artifacts": [],
        "warnings": [],
        "blockers": [],
        "environment_neutral": True,
        "does_not_certify": [
            "legal compliance",
            "IP ownership",
            "open-source obligation resolution",
            "production readiness",
        ],
    }

    try:
        _emit(progress_callback, 3, "authority preflight")
        if authority["status"] != "PASS":
            pipeline_manifest["blockers"].extend(authority["errors"])
            raise RuntimeError("AUTHORITY_CHAIN_FAILED")

        stages = build_legal_stage_registry(LegalPipelineConfig(**{**cfg.to_dict(), "run_id": run_id}))
        write_json(reports / "STAGE_PLAN.json", [item.to_dict() for item in stages])
        if cfg.profile == "plan":
            pipeline_manifest["status"] = "PASS_PLAN_ONLY"
        else:
            total = max(1, len(stages))
            for index, spec in enumerate(stages, 1):
                if _cancel_requested(cfg):
                    pipeline_manifest["status"] = "CANCELLED_AFTER_CURRENT_STAGE"
                    pipeline_manifest["warnings"].append("COOPERATIVE_CANCEL_REQUESTED")
                    _emit(progress_callback, 88, "cancel requested; no new stage started")
                    break

                result = LegalStageResult(
                    stage_id=spec.stage_id,
                    label=spec.label,
                    status="RUNNING",
                    started_at=now_iso(),
                    stdout_log=str(logs / f"{index:02d}_{spec.stage_id}.stdout.log"),
                    stderr_log=str(logs / f"{index:02d}_{spec.stage_id}.stderr.log"),
                )
                _emit(progress_callback, 5 + int((index - 1) * 80 / total), f"stage {index}/{total}: {spec.label}", stage_id=spec.stage_id)

                if not spec.enabled:
                    result.status = "SKIPPED_UNCONFIGURED"
                    result.finished_at = now_iso()
                    pipeline_manifest["stage_results"].append(result.to_dict())
                    marker = f"UNCONFIGURED_STAGE:{spec.stage_id}"
                    if spec.required:
                        pipeline_manifest["blockers"].append(marker)
                        break
                    pipeline_manifest["warnings"].append(marker)
                    continue

                if not spec.root_path.exists():
                    result.status = "FAIL"
                    result.error = f"MISSING_STAGE_ROOT:{spec.root}"
                    result.finished_at = now_iso()
                    pipeline_manifest["stage_results"].append(result.to_dict())
                    if spec.required:
                        pipeline_manifest["blockers"].append(result.error)
                        break
                    pipeline_manifest["warnings"].append(result.error)
                    continue

                before = snapshot_zip_files(output_root)
                exit_code = _stream_process(
                    stage_id=spec.stage_id,
                    program=spec.program,
                    args=spec.args,
                    root=spec.root_path,
                    stdout_path=Path(result.stdout_log),
                    stderr_path=Path(result.stderr_log),
                    timeout_seconds=spec.timeout_seconds,
                    output_callback=output_callback,
                )
                artifact = discover_stage_artifact(output_root=output_root, before=before, expected_prefixes=spec.expected_prefixes)
                ok, artifact_status = _artifact_success(artifact, allow_partial=cfg.allow_partial)
                result.exit_code = exit_code
                result.artifact = artifact
                result.finished_at = now_iso()
                if exit_code == 0 and ok:
                    result.status = artifact_status or "PASS"
                else:
                    result.status = "FAIL"
                    result.error = f"STAGE_FAILED exit={exit_code} artifact_status={artifact_status}"
                pipeline_manifest["stage_results"].append(result.to_dict())
                if artifact:
                    pipeline_manifest["artifacts"].append(artifact)
                if result.status == "FAIL":
                    if spec.required:
                        pipeline_manifest["blockers"].append(f"{spec.stage_id}:{result.error}")
                        break
                    pipeline_manifest["warnings"].append(f"{spec.stage_id}:{result.error}")

        git_after = git_snapshot(Path(cfg.repo_root))
        write_json(reports / "GIT_AFTER.json", git_after)
        repo_unchanged = git_before.get("head") == git_after.get("head") and git_before.get("status_porcelain") == git_after.get("status_porcelain")
        pipeline_manifest["repo_git_unchanged"] = repo_unchanged
        if not repo_unchanged:
            pipeline_manifest["blockers"].append("REPO_GIT_CHANGED_DURING_LEGAL_PIPELINE")

        if pipeline_manifest["blockers"]:
            pipeline_manifest["status"] = "FAIL"
        elif pipeline_manifest["status"] == "CANCELLED_AFTER_CURRENT_STAGE":
            pass
        elif pipeline_manifest["warnings"] or cfg.profile in {"static", "runtime-only"}:
            pipeline_manifest["status"] = "PARTIAL_EVIDENCE_NEEDS_REVIEW"
        elif pipeline_manifest["status"] != "PASS_PLAN_ONLY":
            pipeline_manifest["status"] = "PASS_EVIDENCE_COLLECTION_COMPLETE_NEEDS_REVIEW"

        pipeline_manifest["finished_at"] = now_iso()
        write_json(stage / "LEGAL_PIPELINE_RUN.json", pipeline_manifest)
        write_json(stage / "ARTIFACT_REGISTRY.json", {"schema": "CODE_ATLAS_LEGAL_ARTIFACT_REGISTRY_V2", "run_id": run_id, "artifacts": pipeline_manifest["artifacts"]})
        write_json(stage / "PROVES_DOES_NOT_PROVE.json", {
            "schema": "CODE_ATLAS_LEGAL_PROVES_DOES_NOT_PROVE_V2",
            "run_id": run_id,
            "proves": [
                "configured stages were evaluated sequentially",
                "unconfigured adapters remain explicit instead of receiving platform-specific defaults",
                "stage artifacts were matched by prefix and before/after snapshot when stages executed",
                "artifact hashes and internal manifests were recorded when available",
            ],
            "does_not_prove": pipeline_manifest["does_not_certify"],
            "human_review_required": True,
        })
        write_text(stage / "CONTINUATION.md", f"# Code Atlas legal backend continuation\n\n- Run ID: `{run_id}`\n- Status: `{pipeline_manifest['status']}`\n- External process concurrency: `1`\n- Runtime adapters are caller-configured and optional unless strict mode requires them.\n")
        artifact_hash_file(stage)
        final = package_directory(stage, fail_zip if pipeline_manifest["blockers"] else result_zip)
        _emit(progress_callback, 100, "pipeline packaged", final_zip=str(final), status=pipeline_manifest["status"])
        print(f"FINAL_ZIP={final}", flush=True)
        return {"status": pipeline_manifest["status"], "final_zip": str(final), "manifest": pipeline_manifest}
    except Exception as exc:
        pipeline_manifest["status"] = "FAIL"
        pipeline_manifest["finished_at"] = now_iso()
        pipeline_manifest["blockers"].append(f"{type(exc).__name__}:{exc}")
        write_text(stage / "ERROR.txt", traceback.format_exc())
        write_json(stage / "LEGAL_PIPELINE_RUN.json", pipeline_manifest)
        write_text(stage / "CONTINUATION.md", "# Code Atlas legal backend failure\n\nNo source, database, Git, process or port mutation was intended by the coordinator.\n")
        artifact_hash_file(stage)
        final = package_directory(stage, fail_zip)
        print(f"FINAL_ZIP={final}", flush=True)
        return {"status": "FAIL", "final_zip": str(final), "manifest": pipeline_manifest}
    finally:
        safe_remove_stage(stage)
