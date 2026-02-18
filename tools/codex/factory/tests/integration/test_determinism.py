from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import common, contracts  # noqa: E402
from factory.integrator import integrate_run  # noqa: E402
from factory.normalize_artifacts import normalize_file, normalize_report_text  # noqa: E402
from factory.tests.test_support import isolated_factory_env, make_change, write_worker_bundle  # noqa: E402


class DeterminismIntegrationTests(unittest.TestCase):
    def _seed(self, run_id: str) -> None:
        write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change("apps/determinism/a.ts", sha256="a")])
        write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/determinism/b.ts", sha256="b")])
        write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("tools/determinism/c.py", sha256="c")])
        write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("docs/determinism/d.md", sha256="d")])
        contracts.scaffold_integrator_bundle(run_id)

    def test_same_fixture_twice_yields_same_normalized_report(self) -> None:
        run_id = "determinism_20260218_000001"
        with isolated_factory_env():
            self._seed(run_id)
            first = integrate_run(run_id, workers=list(common.WORKERS))
            report_path = Path(first["report"])
            first_text = report_path.read_text(encoding="utf-8")

            second = integrate_run(run_id, workers=list(common.WORKERS))
            self.assertEqual("PASS", first["status"])
            self.assertEqual("PASS", second["status"])
            second_text = report_path.read_text(encoding="utf-8")

            self.assertEqual(normalize_report_text(first_text), normalize_report_text(second_text))

    def test_two_runs_compare_equal_after_normalization(self) -> None:
        with isolated_factory_env():
            run_a = "determinism_20260218_000002"
            run_b = "determinism_20260218_000003"
            self._seed(run_a)
            self._seed(run_b)
            result_a = integrate_run(run_a, workers=list(common.WORKERS))
            result_b = integrate_run(run_b, workers=list(common.WORKERS))
            report_a = normalize_file(Path(result_a["report"]))
            report_b = normalize_file(Path(result_b["report"]))
            self.assertEqual(report_a, report_b)


if __name__ == "__main__":
    unittest.main()

