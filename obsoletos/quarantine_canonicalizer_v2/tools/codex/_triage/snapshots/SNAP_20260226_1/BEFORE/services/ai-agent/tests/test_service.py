from __future__ import annotations

import unittest

from app.models import FeatureFlagsModel, JobRequestModel
from app.service import get_capabilities, run_job


class ServiceDeterminismTests(unittest.TestCase):
    def test_run_job_same_input_same_output(self) -> None:
        request = JobRequestModel(
            jobId="job-1",
            kind="echo",
            input={"text": "hello"},
            requestedAtUtc="2026-01-01T00:00:00Z",
            flags=FeatureFlagsModel(),
        )

        first = run_job(request).model_dump()
        second = run_job(request).model_dump()
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "completed")
        self.assertEqual(first["finishedAtUtc"], "2026-01-01T00:00:00Z")

    def test_capabilities_declares_required_job_kinds(self) -> None:
        caps = get_capabilities().model_dump()
        self.assertEqual(caps["serviceName"], "ai-agent")
        self.assertEqual(caps["deterministic"], True)
        self.assertEqual(
            caps["supportedJobKinds"],
            ["echo", "extract_keywords", "summarize_text"],
        )


if __name__ == "__main__":
    unittest.main()
