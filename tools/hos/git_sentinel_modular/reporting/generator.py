from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..shared.contracts import CleanupPlan, PredictionResult, RepairPlan, ScanResult, SentinelReport
from ..shared.foundation import write_json, write_text
from ..shared.interfaces import ReportGeneratorPort


@dataclass(slots=True)
class ReportSerializationBundle:
    report: SentinelReport
    json_payload: dict[str, Any]
    markdown_text: str


class SentinelReportGenerator(ReportGeneratorPort):
    def build_report(
        self,
        scan_result: ScanResult,
        predictions: list[PredictionResult],
        repair_plan: RepairPlan,
        cleanup_plan: CleanupPlan,
    ) -> SentinelReport:
        scan_result = scan_result.validate()
        predictions = [item.validate() if isinstance(item, PredictionResult) else PredictionResult(**item).validate() for item in predictions]
        repair_plan = repair_plan.validate()
        cleanup_plan = cleanup_plan.validate()

        top_prediction = predictions[0].candidate_path if predictions else ""
        summary = {
            "artifact_findings": len(scan_result.artifact_findings),
            "security_findings": len(scan_result.security_findings),
            "prediction_count": len(predictions),
            "repair_safe_actions": len(repair_plan.safe_actions),
            "repair_risky_actions": len(repair_plan.risky_actions),
            "cleanup_actions": len(cleanup_plan.actions),
            "cleanup_blocked_actions": len(cleanup_plan.blocked_actions),
            "top_prediction": top_prediction,
            "warnings_count": len(scan_result.warnings),
        }

        warnings = list(scan_result.warnings)
        if repair_plan.has_risky_actions:
            warnings.append("repair plan contains risky actions and must remain gated")

        report = SentinelReport(
            report_id=f"report::{Path(scan_result.repo_root).name}::{scan_result.scan_id}",
            repo_root=scan_result.repo_root,
            scan_result=scan_result,
            predictions=predictions,
            repair_plan=repair_plan,
            cleanup_plan=cleanup_plan,
            summary=summary,
            warnings=warnings,
        ).validate()
        return report

    def to_bundle(self, report: SentinelReport) -> ReportSerializationBundle:
        report = report.validate()
        payload = report.to_dict()
        markdown = self.render_markdown(report)
        return ReportSerializationBundle(report=report, json_payload=payload, markdown_text=markdown)

    def write_bundle(
        self,
        report: SentinelReport,
        json_path: str | Path,
        markdown_path: str | Path,
    ) -> ReportSerializationBundle:
        bundle = self.to_bundle(report)
        write_json(Path(json_path), bundle.json_payload)
        write_text(Path(markdown_path), bundle.markdown_text)
        return bundle

    def render_markdown(self, report: SentinelReport) -> str:
        report = report.validate()
        lines = [
            f"# Sentinel report: {report.report_id}",
            "",
            f"- repo_root: `{report.repo_root}`",
            f"- scan_id: `{report.scan_result.scan_id}`",
            f"- artifact_findings: `{len(report.scan_result.artifact_findings)}`",
            f"- security_findings: `{len(report.scan_result.security_findings)}`",
            f"- predictions: `{len(report.predictions)}`",
            f"- risky_repairs: `{len(report.repair_plan.risky_actions)}`",
            "",
            "## Top predictions",
        ]

        if not report.predictions:
            lines.append("- none")
        else:
            for item in report.predictions[:5]:
                lines.append(
                    f"- `{item.candidate_path}` | risk=`{item.risk_score:.2f}` | confidence=`{item.confidence:.2f}`"
                )

        lines.extend(["", "## Warnings"])
        if not report.warnings:
            lines.append("- none")
        else:
            for warning in report.warnings:
                lines.append(f"- {warning}")

        lines.extend(["", "## Summary JSON", "```json", json.dumps(report.summary, indent=2, ensure_ascii=False), "```"])
        return "\n".join(lines) + "\n"
