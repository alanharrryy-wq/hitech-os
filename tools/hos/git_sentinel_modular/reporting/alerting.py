from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..shared.contracts import SentinelReport
from ..shared.foundation import write_text


@dataclass(slots=True)
class AlertPayload:
    title: str
    severity: str
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "AlertPayload":
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("AlertPayload.title must be non-empty")
        if self.severity not in {"info", "warn", "error"}:
            raise ValueError("AlertPayload.severity must be one of info/warn/error")
        if not isinstance(self.body, str) or not self.body.strip():
            raise ValueError("AlertPayload.body must be non-empty")
        if not isinstance(self.metadata, dict):
            raise TypeError("AlertPayload.metadata must be dict")
        return self


@dataclass(slots=True)
class AlertFileSink:
    output_path: Path

    def write(self, payload: AlertPayload) -> Path:
        payload = payload.validate()
        text = [
            f"title: {payload.title}",
            f"severity: {payload.severity}",
            f"body: {payload.body}",
            "metadata:",
            json.dumps(payload.metadata, indent=2, ensure_ascii=False),
            "",
        ]
        write_text(self.output_path, "\n".join(text))
        return self.output_path


class AlertDispatcher:
    def build_payload(self, report: SentinelReport) -> AlertPayload:
        report = report.validate()
        severity = "error" if report.repair_plan.has_risky_actions else "warn" if report.scan_result.security_findings else "info"
        body = (
            f"artifacts={len(report.scan_result.artifact_findings)} | "
            f"security={len(report.scan_result.security_findings)} | "
            f"predictions={len(report.predictions)} | "
            f"top={report.summary.get('top_prediction', '')}"
        )
        return AlertPayload(
            title=f"Sentinel report {report.scan_result.scan_id}",
            severity=severity,
            body=body,
            metadata={
                "repo_root": report.repo_root,
                "report_id": report.report_id,
                "warnings_count": len(report.warnings),
            },
        ).validate()

    def dispatch_to_file(self, report: SentinelReport, output_path: str | Path) -> Path:
        sink = AlertFileSink(output_path=Path(output_path).resolve())
        payload = self.build_payload(report)
        return sink.write(payload)
