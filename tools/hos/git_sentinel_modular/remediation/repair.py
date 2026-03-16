from __future__ import annotations

from dataclasses import dataclass

from ..shared.contracts import PredictionResult, RepairAction, RepairPlan, ScanResult


@dataclass(slots=True)
class RepairPolicy:
    allow_rewrite_ignore_block: bool = True
    allow_restore_tracked: bool = False
    max_safe_actions: int = 20


class RepairPlanner:
    def __init__(self, policy: RepairPolicy | None = None):
        self.policy = policy or RepairPolicy()

    def plan_repairs(self, scan_result: ScanResult, predictions: list[PredictionResult]) -> RepairPlan:
        scan_result = scan_result.validate()
        predictions = [
            item.validate() if isinstance(item, PredictionResult) else PredictionResult(**item).validate()
            for item in predictions
        ]
        safe_actions: list[RepairAction] = []
        risky_actions: list[RepairAction] = []

        if self.policy.allow_rewrite_ignore_block and scan_result.artifact_findings:
            safe_actions.append(
                RepairAction(
                    kind="rewrite_ignore_block",
                    target_path=".gitignore",
                    reason="generated artifacts detected and ignore block may need update",
                    safe=True,
                    metadata={"artifact_count": len(scan_result.artifact_findings)},
                ).validate()
            )

        for finding in scan_result.security_findings:
            risky_actions.append(
                RepairAction(
                    kind="notify",
                    target_path=finding.path,
                    reason=f"manual review required for security finding {finding.rule_id}",
                    safe=False,
                    metadata={"rule_id": finding.rule_id, "severity": finding.severity},
                ).validate()
            )

        for prediction in predictions[: self.policy.max_safe_actions]:
            if prediction.risk_score >= 0.80:
                risky_actions.append(
                    RepairAction(
                        kind="notify",
                        target_path=prediction.candidate_path,
                        reason="high-risk prediction requires manual review",
                        safe=False,
                        metadata={"risk_score": prediction.risk_score},
                    ).validate()
                )

        if self.policy.allow_restore_tracked:
            safe_actions.append(
                RepairAction(
                    kind="restore_tracked",
                    target_path=".",
                    reason="policy allows tracked restore operations",
                    safe=False,
                    metadata={"enabled_by_policy": True},
                ).validate()
            )

        return RepairPlan(
            dry_run=True,
            safe_actions=safe_actions,
            risky_actions=risky_actions,
        ).validate()
