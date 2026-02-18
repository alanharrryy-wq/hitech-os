from __future__ import annotations

import unittest

from app.handlers import handle_extract_keywords, handle_summarize_text
from app.models import FeatureFlagsModel, JobRequestModel


class HandlerDeterminismTests(unittest.TestCase):
    def _build_request(self, kind: str, text: str) -> JobRequestModel:
        return JobRequestModel(
            jobId="test-job",
            kind=kind,  # type: ignore[arg-type]
            input={"text": text},
            requestedAtUtc="2026-01-01T00:00:00Z",
            flags=FeatureFlagsModel(),
        )

    def test_summarize_text_is_deterministic(self) -> None:
        request = self._build_request(
            "summarize_text",
            "One. Two! Three?  Extra   spaces should collapse.",
        )
        first = handle_summarize_text(request)
        second = handle_summarize_text(request)

        self.assertEqual(first, second)
        self.assertEqual(first["summary"], "One")
        self.assertEqual(first["sentenceCount"], 4)

    def test_extract_keywords_is_sorted_and_deterministic(self) -> None:
        request = self._build_request(
            "extract_keywords",
            "Data pipeline data quality quality checks checks checks and metrics",
        )
        result = handle_extract_keywords(request)
        expected_keywords = ["checks", "data", "quality", "metrics", "pipeline"]
        self.assertEqual(result["keywords"], expected_keywords)


if __name__ == "__main__":
    unittest.main()
