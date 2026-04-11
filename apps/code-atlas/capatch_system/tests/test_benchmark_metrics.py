from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.qa_testkit import ROOT

from tooling.run_qa_benchmark_suite import compute_metrics, run_suite


class BenchmarkMetricTests(unittest.TestCase):
    def test_metric_formulae_are_stable(self) -> None:
        metrics = compute_metrics(
            [
                {"name": "ok", "kind": "fix", "size_bucket": "small", "success": True, "applied": True, "degraded": False, "false_fix": False, "duration_ms": 10.0},
                {"name": "false-fix", "kind": "fix", "size_bucket": "small", "success": False, "applied": True, "degraded": True, "false_fix": True, "duration_ms": 20.0},
                {"name": "blocked", "kind": "fix", "size_bucket": "medium", "success": False, "applied": False, "degraded": False, "false_fix": False, "duration_ms": 30.0},
                {"name": "diag-a", "kind": "diagnostic", "size_bucket": "small", "hypothesis_ms": 12, "duration_ms": 14.0},
                {"name": "diag-b", "kind": "diagnostic", "size_bucket": "large", "hypothesis_ms": 18, "duration_ms": 40.0},
            ]
        )
        self.assertAlmostEqual(1 / 3, metrics["fix_success_rate"])
        self.assertAlmostEqual(1 / 5, metrics["degraded_rate"])
        self.assertAlmostEqual(1 / 2, metrics["false_fix_rate"])
        self.assertEqual(15.0, metrics["avg_time_to_first_useful_hypothesis_ms"])
        self.assertIn("small", metrics["benchmark_by_size"])
        self.assertIn("large", metrics["benchmark_by_size"])

    def test_quick_suite_writes_reports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_bench_") as tmp_dir:
            payload = run_suite(ROOT, Path(tmp_dir), quick=True)
            self.assertIn("metrics", payload)
            self.assertTrue((Path(tmp_dir) / "qa_benchmark_suite.json").exists())
            self.assertTrue((Path(tmp_dir) / "qa_benchmark_suite.md").exists())
            self.assertIn("benchmark_by_size", payload["metrics"])


if __name__ == "__main__":
    unittest.main()
