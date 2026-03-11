#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import write_json

from .config import SentinelConfig
from .git_utils import run_git
from .scanner import scan_repository
from .security_quality import evaluate_security_dataset, write_security_eval_files
from .security_scanner import scan_security
from .utils import now_utc_iso


def _resolve_base_ref(repo_root: Path, candidate: str) -> str:
    ref = candidate.strip()
    if not ref:
        return "HEAD~1"
    exists = run_git(repo_root, ["rev-parse", "--verify", ref], check=False)
    if exists.returncode == 0:
        return ref
    fallback = "HEAD~1"
    exists_fallback = run_git(repo_root, ["rev-parse", "--verify", fallback], check=False)
    return fallback if exists_fallback.returncode == 0 else "HEAD"


def _changed_paths(repo_root: Path, base_ref: str) -> list[str]:
    commit_scoped: set[str] = set()
    completed = run_git(repo_root, ["diff", "--name-only", f"{base_ref}...HEAD"], check=False)
    if completed.returncode == 0:
        commit_scoped = {line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}

    local_scoped: set[str] = set()
    local = run_git(repo_root, ["status", "--porcelain"], check=False)
    if local.returncode == 0:
        for raw_line in local.stdout.splitlines():
            line = raw_line.strip()
            if len(line) < 4:
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()
            if path:
                local_scoped.add(path.replace("\\", "/"))

    return sorted(commit_scoped | local_scoped)


def run_ci_gate(
    config: SentinelConfig,
    base_ref: str | None = None,
    run_security_eval: bool = True,
) -> dict[str, Any]:
    resolved_base_ref = _resolve_base_ref(config.repo_root, base_ref or config.ci_gate_default_base_ref)
    changed_paths = _changed_paths(config.repo_root, resolved_base_ref)

    scan_state = scan_repository(config)
    include_paths = set(changed_paths) if changed_paths else set()
    security_result = scan_security(config=config, scan_state=scan_state, include_paths=include_paths)

    severity_counts = security_result.get("summary", {}).get("severityCounts", {})
    high_count = int(severity_counts.get("high", 0))
    critical_count = int(severity_counts.get("critical", 0))

    eval_payload: dict[str, Any] = {
        "status": "skipped",
        "passed": True,
        "metrics": {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "tp": 0,
            "fp": 0,
            "fn": 0,
        },
    }
    eval_files: dict[str, str] = {}
    if run_security_eval:
        eval_payload = evaluate_security_dataset(config=config)
        eval_files = write_security_eval_files(config=config, payload=eval_payload)

    failures: list[str] = []
    if bool(config.ci_gate_block_critical) and critical_count > 0:
        failures.append(f"critical_findings={critical_count}")
    if bool(config.ci_gate_block_high) and high_count > 0:
        failures.append(f"high_findings={high_count}")

    if run_security_eval:
        if not bool(eval_payload.get("passed", False)):
            metrics = eval_payload.get("metrics", {})
            failures.append(
                "security_eval_failed: "
                + f"precision={metrics.get('precision', 0)} recall={metrics.get('recall', 0)} f1={metrics.get('f1', 0)}"
            )

    passed = len(failures) == 0
    payload = {
        "timestamp": now_utc_iso(),
        "baseRef": resolved_base_ref,
        "changedPathCount": len(changed_paths),
        "changedPaths": changed_paths,
        "security": {
            "summary": security_result.get("summary", {}),
            "topFindings": security_result.get("findings", [])[:30],
        },
        "securityEval": eval_payload,
        "files": eval_files,
        "passed": passed,
        "failures": failures,
    }

    slug = payload["timestamp"].replace(":", "").replace("-", "")
    latest_path = (config.telemetry_dir / "ci_gate_latest.json").resolve()
    snapshot_path = (config.telemetry_dir / f"ci_gate_{slug}.json").resolve()
    write_json(latest_path, payload, indent=2, sort_keys=True)
    write_json(snapshot_path, payload, indent=2, sort_keys=True)
    payload["files"]["latest"] = latest_path.as_posix()
    payload["files"]["snapshot"] = snapshot_path.as_posix()
    return payload
