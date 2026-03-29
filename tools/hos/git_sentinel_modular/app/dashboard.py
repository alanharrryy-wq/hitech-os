from __future__ import annotations

from typing import Any

from ..app.visualization import build_dashboard_state, build_marker_summary
from ..shared.contracts import SentinelReport


def build_dashboard_payload(report: SentinelReport) -> dict[str, Any]:
    report = report.validate()
    state = build_dashboard_state(report)
    markers = build_marker_summary(report)
    return {
        "report_id": report.report_id,
        "repo_root": report.repo_root,
        "state": state,
        "markers": markers,
    }


def build_dashboard_snapshot(report: SentinelReport) -> dict[str, Any]:
    payload = build_dashboard_payload(report)
    return {
        "title": "Git Sentinel Modular Dashboard",
        "repo_root": payload["repo_root"],
        "scan_id": payload["state"]["scan_id"],
        "marker_flags": payload["markers"],
        "next_actions": payload["state"]["next_actions"],
        "kpis": payload["state"]["kpis"],
    }
