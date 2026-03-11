#!/usr/bin/env python3
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import write_json

from .config import SentinelConfig
from .git_utils import git_branch_activity, git_top_modified_files
from .learning_engine import write_telemetry_snapshot
from .utils import now_utc_iso


def build_telemetry_payload(
    config: SentinelConfig,
    scan_state: dict[str, Any],
    artifact_result: dict[str, Any],
    cleanup_result: dict[str, Any],
    repair_result: dict[str, Any],
    security_result: dict[str, Any],
    health_score: int,
    error_count: int,
) -> dict[str, Any]:
    summary = scan_state.get("summary", {})
    cleanup_summary = cleanup_result.get("summary", {})
    repair_summary = repair_result.get("summary", {})
    security_summary = security_result.get("summary", {})
    artifact_summary = artifact_result.get("summary", {})

    branch_activity = git_branch_activity(config.repo_root)
    now_epoch = int(datetime.now(UTC).timestamp())
    stale_30d = len(
        [
            row
            for row in branch_activity
            if int(row.get("lastCommitEpoch", 0)) > 0 and (now_epoch - int(row.get("lastCommitEpoch", 0))) > 30 * 86400
        ]
    )

    return {
        "timestamp": now_utc_iso(),
        "repositorySizeBytes": int(summary.get("totalSizeBytes", 0)),
        "fileCount": int(summary.get("fileCount", 0)),
        "untrackedFileCount": int(summary.get("untrackedFileCount", 0)),
        "artifactCount": int(artifact_summary.get("artifactCount", 0)),
        "artifactClusterCount": int(summary.get("artifactClusters", 0)),
        "artifactFrequency": (
            float(artifact_summary.get("artifactCount", 0)) / max(1, int(summary.get("fileCount", 0)))
        ),
        "largeBinaryFileCount": int(len(scan_state.get("largeBinaryFiles", []))),
        "unexpectedFileTypeCount": int(summary.get("unexpectedFileTypes", 0)),
        "cleanupDeleted": int(cleanup_summary.get("deletedFiles", 0)),
        "cleanupDeletedDirs": int(cleanup_summary.get("deletedDirs", 0)),
        "repairExecuted": int(repair_summary.get("executedActions", 0)),
        "repairFailed": int(repair_summary.get("failedActions", 0)),
        "securityFindingCount": int(security_summary.get("findingCount", 0)),
        "securityAlertLevel": str(security_summary.get("alertLevel", "none")),
        "healthScore": int(health_score),
        "errorCount": int(error_count),
        "branchActivity": branch_activity,
        "branchCount": len(branch_activity),
        "staleBranches30d": stale_30d,
        "topModifiedFiles90d": git_top_modified_files(config.repo_root, days=90, limit=200),
    }


def persist_telemetry_payload(config: SentinelConfig, telemetry_payload: dict[str, Any]) -> None:
    write_telemetry_snapshot(config=config, payload=telemetry_payload)


def write_telemetry_files(config: SentinelConfig, telemetry_payload: dict[str, Any]) -> dict[str, str]:
    config.telemetry_dir.mkdir(parents=True, exist_ok=True)
    latest_path = (config.telemetry_dir / "telemetry_latest.json").resolve()
    timestamp_slug = telemetry_payload.get("timestamp", now_utc_iso()).replace(":", "").replace("-", "")
    snapshot_path = (config.telemetry_dir / f"telemetry_{timestamp_slug}.json").resolve()
    write_json(latest_path, telemetry_payload, indent=2, sort_keys=True)
    write_json(snapshot_path, telemetry_payload, indent=2, sort_keys=True)
    return {
        "latest": latest_path.as_posix(),
        "snapshot": snapshot_path.as_posix(),
    }
