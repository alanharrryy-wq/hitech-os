from __future__ import annotations

import unittest

from app.engine import build_health_report, parse_request, run_job


class EngineCompatibilityTests(unittest.TestCase):
    def test_run_job_from_engine_exports(self) -> None:
        request = parse_request(
            {
                "jobId": "engine-job",
                "kind": "echo",
                "input": {"text": "hello"},
                "requestedAtUtc": "2026-01-01T00:00:00Z",
                "flags": {
                    "enableAiExecution": True,
                    "enableCapabilitiesProxy": False,
                    "enableExperimentalUi": False,
                    "enableHealthDashboard": False,
                },
            }
        )
        result = run_job(request).model_dump()
        self.assertEqual(result["jobId"], "engine-job")
        self.assertEqual(result["status"], "completed")

    def test_health_report_ok(self) -> None:
        report = build_health_report().model_dump()
        self.assertEqual(report["status"], "ok")


if __name__ == "__main__":
    unittest.main()
