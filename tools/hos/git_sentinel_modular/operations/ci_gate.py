from __future__ import annotations

from dataclasses import dataclass

from ..shared.contracts import SentinelReport


@dataclass(slots=True)
class CIGateResult:
    ok: bool
    status: str
    reasons: list[str]


class CIGateEvaluator:
    def evaluate(self, report: SentinelReport) -> CIGateResult:
        report = report.validate()
        reasons: list[str] = []

        if report.repair_plan.has_risky_actions:
            reasons.append("repair plan has risky actions")
        if report.scan_result.security_findings:
            reasons.append(f"security findings present: {len(report.scan_result.security_findings)}")

        if reasons:
            return CIGateResult(ok=False, status="blocked", reasons=reasons)

        return CIGateResult(ok=True, status="passed", reasons=["no risky repairs and no security findings"])
