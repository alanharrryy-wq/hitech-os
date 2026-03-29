from __future__ import annotations

import unittest

from tools.hos.git_sentinel.report_generator import compute_health_score


def _base_scan() -> dict:
    return {"summary": {"nestedGitMarkers": 0}}


def _base_cleanup() -> dict:
    return {"summary": {"deletedFiles": 0, "failedActions": 0}}


def _base_repair() -> dict:
    return {"summary": {"failedActions": 0}}


class ReportHealthScoreTests(unittest.TestCase):
    def test_uses_cleanup_candidates_for_artifact_penalty(self) -> None:
        score, factors = compute_health_score(
            scan_state=_base_scan(),
            artifact_result={"summary": {"artifactCount": 9500, "cleanupCandidateCount": 0}},
            cleanup_result=_base_cleanup(),
            repair_result=_base_repair(),
            security_result={"summary": {"findingCount": 0}, "findings": []},
            prediction_result={"summary": {"highRisk": 0}, "predictions": []},
            telemetry_payload={},
        )
        self.assertEqual(100, score)
        self.assertFalse(any(row.get("factor") == "artifact_volume" for row in factors))

    def test_documentation_findings_have_low_penalty(self) -> None:
        findings = [
            {
                "severity": "low",
                "context": "documentation",
                "confidence": 0.35,
            }
            for _ in range(12)
        ]
        findings.extend(
            [
                {
                    "severity": "medium",
                    "context": "documentation",
                    "confidence": 0.55,
                },
                {
                    "severity": "medium",
                    "context": "documentation",
                    "confidence": 1.0,
                },
            ]
        )
        score, _factors = compute_health_score(
            scan_state=_base_scan(),
            artifact_result={"summary": {"artifactCount": 0, "cleanupCandidateCount": 0}},
            cleanup_result=_base_cleanup(),
            repair_result=_base_repair(),
            security_result={"summary": {"findingCount": len(findings)}, "findings": findings},
            prediction_result={"summary": {"highRisk": 0}, "predictions": []},
            telemetry_payload={},
        )
        self.assertGreaterEqual(score, 95)

    def test_runtime_findings_keep_strong_penalty(self) -> None:
        findings = [
            {"severity": "high", "context": "runtime", "confidence": 1.0},
            {"severity": "high", "context": "runtime", "confidence": 1.0},
            {"severity": "critical", "context": "runtime", "confidence": 1.0},
        ]
        score, _factors = compute_health_score(
            scan_state=_base_scan(),
            artifact_result={"summary": {"artifactCount": 0, "cleanupCandidateCount": 0}},
            cleanup_result=_base_cleanup(),
            repair_result=_base_repair(),
            security_result={"summary": {"findingCount": len(findings)}, "findings": findings},
            prediction_result={"summary": {"highRisk": 0}, "predictions": []},
            telemetry_payload={},
        )
        self.assertLessEqual(score, 72)

    def test_merge_conflict_prediction_does_not_penalize_health(self) -> None:
        score, factors = compute_health_score(
            scan_state=_base_scan(),
            artifact_result={"summary": {"artifactCount": 0, "cleanupCandidateCount": 0}},
            cleanup_result=_base_cleanup(),
            repair_result=_base_repair(),
            security_result={"summary": {"findingCount": 0}, "findings": []},
            prediction_result={
                "summary": {"highRisk": 1},
                "predictions": [{"kind": "merge_conflict_risk", "risk": "high"}],
            },
            telemetry_payload={},
        )
        self.assertEqual(100, score)
        self.assertFalse(any(row.get("factor") == "high_risk_predictions" for row in factors))


if __name__ == "__main__":
    unittest.main()
