#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import write_json
from tools.hos._core.stable_text import write_text

from .config import SentinelConfig
from .utils import now_utc_iso


def compute_health_score(
    scan_state: dict[str, Any],
    artifact_result: dict[str, Any],
    cleanup_result: dict[str, Any],
    repair_result: dict[str, Any],
    security_result: dict[str, Any],
    prediction_result: dict[str, Any],
    telemetry_payload: dict[str, Any] | None = None,
) -> tuple[int, list[dict[str, Any]]]:
    telemetry_payload = telemetry_payload or {}
    score = 100
    factors: list[dict[str, Any]] = []

    nested = int(scan_state.get("summary", {}).get("nestedGitMarkers", 0))
    if nested > 0:
        penalty = min(40, nested * 10)
        score -= penalty
        factors.append({"factor": "unmanaged_nested_git", "delta": -penalty, "value": nested})

    artifact_count = int(artifact_result.get("summary", {}).get("artifactCount", 0))
    if artifact_count > 0:
        penalty = min(25, artifact_count // 40 + 1)
        score -= penalty
        factors.append({"factor": "artifact_volume", "delta": -penalty, "value": artifact_count})

    security_findings = int(security_result.get("summary", {}).get("findingCount", 0))
    if security_findings > 0:
        penalty = min(30, security_findings * 2)
        score -= penalty
        factors.append({"factor": "security_findings", "delta": -penalty, "value": security_findings})

    cleanup_deleted = int(cleanup_result.get("summary", {}).get("deletedFiles", 0))
    if cleanup_deleted > 0:
        bonus = min(10, cleanup_deleted // 20 + 1)
        score += bonus
        factors.append({"factor": "cleanup_effect", "delta": bonus, "value": cleanup_deleted})

    repair_failed = int(repair_result.get("summary", {}).get("failedActions", 0))
    if repair_failed > 0:
        penalty = min(20, repair_failed * 4)
        score -= penalty
        factors.append({"factor": "repair_failures", "delta": -penalty, "value": repair_failed})

    high_risk_predictions = int(prediction_result.get("summary", {}).get("highRisk", 0))
    if high_risk_predictions > 0:
        penalty = min(20, high_risk_predictions * 6)
        score -= penalty
        factors.append({"factor": "high_risk_predictions", "delta": -penalty, "value": high_risk_predictions})

    repo_size = int(telemetry_payload.get("repositorySizeBytes", 0))
    if repo_size > 2 * 1024 * 1024 * 1024:
        penalty = 10
        score -= penalty
        factors.append({"factor": "repository_size", "delta": -penalty, "value": repo_size})
    elif repo_size > 1 * 1024 * 1024 * 1024:
        penalty = 5
        score -= penalty
        factors.append({"factor": "repository_size", "delta": -penalty, "value": repo_size})

    stale_branches = int(telemetry_payload.get("staleBranches30d", 0))
    if stale_branches > 0:
        penalty = min(10, stale_branches // 4 + 1)
        score -= penalty
        factors.append({"factor": "branch_hygiene", "delta": -penalty, "value": stale_branches})

    top_modified = telemetry_payload.get("topModifiedFiles90d", [])
    if isinstance(top_modified, list) and top_modified:
        top_pressure = sum(int(row.get("commits", 0)) for row in top_modified[:10])
        if top_pressure > 220:
            penalty = min(8, top_pressure // 90)
            score -= penalty
            factors.append({"factor": "code_stability", "delta": -penalty, "value": top_pressure})

    score = max(0, min(100, score))
    return score, factors


def _status_from_score(score: int) -> str:
    if score >= 85:
        return "healthy"
    if score >= 65:
        return "warning"
    return "critical"


def _markdown_report(payload: dict[str, Any]) -> str:
    health = payload.get("health", {})
    summary = payload.get("summary", {})
    files = payload.get("files", {})
    predictions = payload.get("predictions", {})
    lines = [
        "# Git Sentinel Report",
        "",
        f"- Timestamp: {payload.get('timestamp', '')}",
        f"- Repository: {payload.get('repoRoot', '')}",
        f"- Health score: {health.get('score', 0)} ({health.get('status', 'unknown')})",
        f"- File count: {summary.get('fileCount', 0)}",
        f"- Artifact count: {summary.get('artifactCount', 0)}",
        f"- Nested git markers: {summary.get('nestedGitMarkers', 0)}",
        f"- Security findings: {summary.get('securityFindings', 0)}",
        "",
        "## Predictions",
        "",
    ]
    for row in predictions.get("predictions", []):
        lines.append(
            f"- {row.get('kind')}: risk={row.get('risk')} score={row.get('score')} detail={row.get('detail')}"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Report JSON: {files.get('reportJson', '')}",
            f"- Dashboard data: {files.get('dashboardJson', '')}",
            f"- Telemetry latest: {files.get('telemetryLatest', '')}",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(
    config: SentinelConfig,
    payload: dict[str, Any],
) -> dict[str, str]:
    timestamp_slug = payload.get("timestamp", now_utc_iso()).replace(":", "").replace("-", "")
    report_json_path = (config.report_dir / f"git_sentinel_report_{timestamp_slug}.json").resolve()
    report_md_path = (config.report_dir / f"git_sentinel_report_{timestamp_slug}.md").resolve()
    latest_json_path = (config.report_dir / "git_sentinel_report_latest.json").resolve()
    latest_md_path = (config.report_dir / "git_sentinel_report_latest.md").resolve()
    dashboard_json_path = (config.dashboard_dir / "dashboard_data.json").resolve()

    write_json(report_json_path, payload, indent=2, sort_keys=True)
    write_json(latest_json_path, payload, indent=2, sort_keys=True)
    write_text(report_md_path, _markdown_report(payload), trailing_newline=True)
    write_text(latest_md_path, _markdown_report(payload), trailing_newline=True)
    write_json(dashboard_json_path, payload.get("dashboard", {}), indent=2, sort_keys=True)
    write_json(config.state_path, payload, indent=2, sort_keys=True)

    return {
        "reportJson": report_json_path.as_posix(),
        "reportMarkdown": report_md_path.as_posix(),
        "latestJson": latest_json_path.as_posix(),
        "latestMarkdown": latest_md_path.as_posix(),
        "dashboardJson": dashboard_json_path.as_posix(),
        "stateJson": config.state_path.as_posix(),
    }


def build_report_payload(
    config: SentinelConfig,
    scan_state: dict[str, Any],
    artifact_result: dict[str, Any],
    ignore_result: dict[str, Any],
    cleanup_result: dict[str, Any],
    repair_result: dict[str, Any],
    security_result: dict[str, Any],
    telemetry_payload: dict[str, Any],
    prediction_result: dict[str, Any],
    visualization_result: dict[str, Any],
    errors: list[str],
    telemetry_files: dict[str, str],
) -> dict[str, Any]:
    health_score, health_factors = compute_health_score(
        scan_state=scan_state,
        artifact_result=artifact_result,
        cleanup_result=cleanup_result,
        repair_result=repair_result,
        security_result=security_result,
        prediction_result=prediction_result,
        telemetry_payload=telemetry_payload,
    )

    summary = {
        "fileCount": int(scan_state.get("summary", {}).get("fileCount", 0)),
        "artifactCount": int(artifact_result.get("summary", {}).get("artifactCount", 0)),
        "nestedGitMarkers": int(scan_state.get("summary", {}).get("nestedGitMarkers", 0)),
        "securityFindings": int(security_result.get("summary", {}).get("findingCount", 0)),
        "cleanupDeletedFiles": int(cleanup_result.get("summary", {}).get("deletedFiles", 0)),
        "repairExecutedActions": int(repair_result.get("summary", {}).get("executedActions", 0)),
        "errorCount": len(errors),
    }

    dashboard = {
        "metrics": {
            "healthScore": health_score,
            "repositorySizeBytes": telemetry_payload.get("repositorySizeBytes", 0),
            "artifactCount": telemetry_payload.get("artifactCount", 0),
            "cleanupDeleted": telemetry_payload.get("cleanupDeleted", 0),
            "securityFindingCount": telemetry_payload.get("securityFindingCount", 0),
        },
        "alerts": security_result.get("findings", []),
        "cleanupActions": cleanup_result.get("results", []),
        "healthFactors": health_factors,
        "predictions": prediction_result.get("predictions", []),
    }

    return {
        "timestamp": telemetry_payload.get("timestamp", now_utc_iso()),
        "repoRoot": config.repo_root.as_posix(),
        "health": {
            "score": health_score,
            "status": _status_from_score(health_score),
            "factors": health_factors,
        },
        "summary": summary,
        "scan": scan_state.get("summary", {}),
        "artifacts": artifact_result.get("summary", {}),
        "ignore": ignore_result,
        "cleanup": cleanup_result.get("summary", {}),
        "repair": repair_result.get("summary", {}),
        "security": security_result.get("summary", {}),
        "telemetry": telemetry_payload,
        "predictions": prediction_result,
        "visualization": visualization_result,
        "errors": errors,
        "dashboard": dashboard,
        "files": {
            "telemetryLatest": telemetry_files.get("latest", ""),
            "telemetrySnapshot": telemetry_files.get("snapshot", ""),
        },
    }
