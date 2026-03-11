#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .config import SentinelConfig
from .learning_engine import compute_health_trend, read_folder_activity, read_telemetry_history, write_prediction_history


@dataclass(frozen=True)
class RiskSignal:
    kind: str
    risk: str
    score: float
    detail: str
    recommendation: str


def _parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _bloat_signal(current: dict[str, Any], history: list[dict[str, Any]]) -> RiskSignal:
    repo_size = int(current.get("repositorySizeBytes", 0))
    file_count = int(current.get("fileCount", 0))
    trend = compute_health_trend(history)
    growth_ratio = 0.0 if repo_size <= 0 else max(0.0, float(trend.size_delta) / float(max(1, repo_size)))
    score = min(1.0, growth_ratio * 4.0 + (0.2 if file_count > 60_000 else 0.0))
    if score >= 0.75:
        risk = "high"
    elif score >= 0.4:
        risk = "medium"
    else:
        risk = "low"
    detail = f"size={repo_size}B delta={trend.size_delta} files={file_count}"
    return RiskSignal(
        kind="repository_bloat",
        risk=risk,
        score=score,
        detail=detail,
        recommendation="Increase cleanup cadence and keep runtime artifacts in tools/_local.",
    )


def _artifact_accumulation_signal(current: dict[str, Any], history: list[dict[str, Any]]) -> RiskSignal:
    artifact_count = int(current.get("artifactCount", 0))
    trend = compute_health_trend(history)
    base = float(max(0, artifact_count)) / 500.0
    delta = max(0, trend.artifact_delta) / 100.0
    score = min(1.0, base + delta)
    if score >= 0.75:
        risk = "high"
    elif score >= 0.35:
        risk = "medium"
    else:
        risk = "low"
    detail = f"artifacts={artifact_count} delta={trend.artifact_delta}"
    return RiskSignal(
        kind="artifact_accumulation",
        risk=risk,
        score=score,
        detail=detail,
        recommendation="Enable guardian mode with apply=true to auto-clean generated files.",
    )


def _merge_conflict_signal(current: dict[str, Any]) -> RiskSignal:
    branches = current.get("branchActivity", [])
    top_modified = current.get("topModifiedFiles90d", [])
    active_branches = len(branches)
    top_pressure = sum(int(row.get("commits", 0)) for row in top_modified[:20])
    score = min(1.0, (active_branches / 20.0) + (top_pressure / 800.0))
    if score >= 0.8:
        risk = "high"
    elif score >= 0.4:
        risk = "medium"
    else:
        risk = "low"
    detail = f"active_branches={active_branches} top_modified_pressure={top_pressure}"
    return RiskSignal(
        kind="merge_conflict_risk",
        risk=risk,
        score=score,
        detail=detail,
        recommendation="Prioritize frequent integration on hot files to reduce divergence risk.",
    )


def _disk_growth_signal(history: list[dict[str, Any]]) -> RiskSignal:
    if len(history) < 2:
        return RiskSignal(
            kind="disk_usage_growth",
            risk="low",
            score=0.0,
            detail="insufficient history",
            recommendation="Collect at least 2 telemetry snapshots for growth prediction.",
        )
    first = history[0]
    last = history[-1]
    first_ts = _parse_ts(str(first.get("timestamp", "")))
    last_ts = _parse_ts(str(last.get("timestamp", "")))
    first_size = int(first.get("repositorySizeBytes", 0))
    last_size = int(last.get("repositorySizeBytes", 0))
    if first_ts is None or last_ts is None or last_ts <= first_ts:
        return RiskSignal(
            kind="disk_usage_growth",
            risk="low",
            score=0.0,
            detail="invalid timestamps",
            recommendation="Keep timestamped telemetry for slope-based prediction.",
        )
    days = max(1e-6, (last_ts - first_ts).total_seconds() / 86400.0)
    growth_per_day = (last_size - first_size) / days
    score = min(1.0, max(0.0, growth_per_day / (150 * 1024 * 1024)))
    if score >= 0.8:
        risk = "high"
    elif score >= 0.35:
        risk = "medium"
    else:
        risk = "low"
    detail = f"growth_per_day={int(growth_per_day)}B/day window_days={days:.2f}"
    return RiskSignal(
        kind="disk_usage_growth",
        risk=risk,
        score=score,
        detail=detail,
        recommendation="Prune old reports/logs and rotate artifacts in runtime zones.",
    )


def _problematic_files_signal(config: SentinelConfig) -> RiskSignal:
    folder_activity = read_folder_activity(config=config, limit=50)
    if not folder_activity:
        return RiskSignal(
            kind="problematic_files",
            risk="low",
            score=0.0,
            detail="no folder activity yet",
            recommendation="Run additional cycles to build folder-level artifact intelligence.",
        )
    hottest = folder_activity[0]
    artifact_count = int(hottest.get("artifactCount", 0))
    source_count = int(hottest.get("sourceCount", 0))
    ratio = artifact_count / max(1, source_count)
    score = min(1.0, ratio / 8.0)
    if score >= 0.8:
        risk = "high"
    elif score >= 0.35:
        risk = "medium"
    else:
        risk = "low"
    detail = f"folder={hottest.get('folder')} artifacts={artifact_count} source={source_count} ratio={ratio:.2f}"
    return RiskSignal(
        kind="problematic_files",
        risk=risk,
        score=score,
        detail=detail,
        recommendation="Inspect top noisy folders and tighten ignore + cleanup policy for them.",
    )


def _unstable_files_signal(current: dict[str, Any]) -> RiskSignal:
    hot = current.get("topModifiedFiles90d", [])
    if not hot:
        return RiskSignal(
            kind="unstable_files",
            risk="low",
            score=0.0,
            detail="no history rows",
            recommendation="Collect commit history to identify unstable files.",
        )
    top20 = hot[:20]
    hotspot_pressure = sum(int(row.get("commits", 0)) for row in top20)
    max_single = max(int(row.get("commits", 0)) for row in top20)
    score = min(1.0, (hotspot_pressure / 500.0) + (max_single / 150.0))
    if score >= 0.8:
        risk = "high"
    elif score >= 0.4:
        risk = "medium"
    else:
        risk = "low"
    detail = f"top20_commits={hotspot_pressure} max_single={max_single}"
    return RiskSignal(
        kind="unstable_files",
        risk=risk,
        score=score,
        detail=detail,
        recommendation="Refactor high-churn files and reduce merge surface in hotspots.",
    )


def generate_predictions(config: SentinelConfig, current_telemetry: dict[str, Any]) -> dict[str, Any]:
    history = read_telemetry_history(config=config, limit=config.prediction_window)
    signals = [
        _bloat_signal(current_telemetry, history),
        _artifact_accumulation_signal(current_telemetry, history),
        _merge_conflict_signal(current_telemetry),
        _disk_growth_signal(history),
        _problematic_files_signal(config),
        _unstable_files_signal(current_telemetry),
    ]
    payload = [
        {
            "kind": signal.kind,
            "risk": signal.risk,
            "score": round(signal.score, 4),
            "detail": signal.detail,
            "recommendation": signal.recommendation,
        }
        for signal in signals
    ]
    write_prediction_history(config=config, predictions=payload)
    return {
        "summary": {
            "count": len(payload),
            "highRisk": len([row for row in payload if row["risk"] == "high"]),
            "mediumRisk": len([row for row in payload if row["risk"] == "medium"]),
        },
        "predictions": payload,
        "historyWindow": len(history),
    }
