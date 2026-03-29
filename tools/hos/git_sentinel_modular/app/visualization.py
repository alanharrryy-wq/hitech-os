from __future__ import annotations

from typing import Any

from ..shared.contracts import PredictionResult, SentinelReport


def build_kpi_cards(report: SentinelReport) -> list[dict[str, Any]]:
    report = report.validate()
    summary = report.summary
    return [
        {"id": "artifacts", "label": "Artifact Findings", "value": summary.get("artifact_findings", 0)},
        {"id": "security", "label": "Security Findings", "value": summary.get("security_findings", 0)},
        {"id": "predictions", "label": "Predictions", "value": summary.get("prediction_count", 0)},
        {"id": "warnings", "label": "Warnings", "value": summary.get("warnings_count", 0)},
    ]


def build_next_actions(report: SentinelReport) -> list[dict[str, str]]:
    report = report.validate()
    actions: list[dict[str, str]] = []

    if report.repair_plan.has_risky_actions:
        actions.append({
            "id": "gate-risky-repairs",
            "label": "Review risky repairs",
            "reason": "Repair plan contains risky actions that must stay gated.",
        })

    if report.scan_result.security_findings:
        actions.append({
            "id": "review-security-findings",
            "label": "Review security findings",
            "reason": f"Detected {len(report.scan_result.security_findings)} security findings.",
        })

    if report.predictions:
        top = report.predictions[0]
        actions.append({
            "id": "inspect-top-prediction",
            "label": "Inspect top prediction",
            "reason": f"{top.candidate_path} scored {top.risk_score:.2f}.",
        })

    if not actions:
        actions.append({
            "id": "no-op",
            "label": "No immediate action",
            "reason": "Current report has no risky repairs and no actionable findings.",
        })

    return actions


def build_dashboard_state(report: SentinelReport) -> dict[str, Any]:
    report = report.validate()
    return {
        "report_id": report.report_id,
        "repo_root": report.repo_root,
        "scan_id": report.scan_result.scan_id,
        "kpis": build_kpi_cards(report),
        "next_actions": build_next_actions(report),
        "warnings": list(report.warnings),
        "top_predictions": [
            {
                "path": item.candidate_path,
                "risk_score": item.risk_score,
                "confidence": item.confidence,
                "rationale": list(item.rationale),
            }
            for item in report.predictions[:5]
        ],
    }


def build_marker_summary(report: SentinelReport) -> dict[str, Any]:
    report = report.validate()
    return {
        "has_cloud_glass_candidate_data": bool(report.predictions),
        "has_neon_night_candidate_data": bool(report.scan_result.security_findings or report.scan_result.artifact_findings),
        "has_next_best_actions": True,
        "has_what_this_means": True,
    }
