from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import attestations, contracts  # noqa: E402
from factory.tests.test_support import isolated_factory_env, make_change, write_worker_bundle  # noqa: E402


class AttestationTests(unittest.TestCase):
    def _seed_run(self, run_id: str) -> None:
        write_worker_bundle(run_id=run_id, worker="A_worker", changes=[make_change("apps/a.ts", sha256="1")])
        write_worker_bundle(run_id=run_id, worker="B_worker", changes=[make_change("apps/b.ts", sha256="2")])
        write_worker_bundle(run_id=run_id, worker="C_worker", changes=[make_change("tools/c.py", sha256="3")])
        write_worker_bundle(run_id=run_id, worker="D_worker", changes=[make_change("docs/d.md", sha256="4")])
        contracts.scaffold_integrator_bundle(run_id)
        report = contracts.bundle_dir(run_id, "Z_integrator") / "FINAL_REPORT.txt"
        report.write_text("# Final Report\n\n- stable\n", encoding="utf-8")

    def test_write_all_attestations(self) -> None:
        run_id = "attest_20260218_000001"
        with isolated_factory_env() as env:
            self._seed_run(run_id)
            ledger = env["runs_dir"] / "factory_ledger.jsonl"
            ledger.write_text('{"a":1}\n', encoding="utf-8")
            payload = attestations.write_all_attestations(run_id)

            self.assertTrue(Path(payload["bundles"]).exists())
            self.assertTrue(Path(payload["ledger"]).exists())
            self.assertTrue(Path(payload["report"]).exists())

    def test_bundle_manifest_sorted_deterministically(self) -> None:
        run_id = "attest_20260218_000002"
        with isolated_factory_env():
            self._seed_run(run_id)
            path_1 = attestations.write_bundle_attestation(run_id)
            content_1 = path_1.read_text(encoding="utf-8")
            path_2 = attestations.write_bundle_attestation(run_id)
            content_2 = path_2.read_text(encoding="utf-8")
            self.assertEqual(content_1, content_2)

            lines = [line for line in content_1.splitlines() if line.strip()]
            sorted_lines = sorted(lines, key=lambda item: item.split("  ", 1)[1])
            self.assertEqual(sorted_lines, lines)

    def test_report_attestation_empty_when_report_missing(self) -> None:
        run_id = "attest_20260218_000003"
        with isolated_factory_env():
            contracts.scaffold_integrator_bundle(run_id)
            report = contracts.bundle_dir(run_id, "Z_integrator") / "FINAL_REPORT.txt"
            report.unlink()
            manifest = attestations.write_report_attestation(run_id)
            self.assertEqual("", manifest.read_text(encoding="utf-8"))

    def test_ledger_attestation_empty_when_missing(self) -> None:
        run_id = "attest_20260218_000004"
        with isolated_factory_env():
            contracts.scaffold_integrator_bundle(run_id)
            manifest = attestations.write_ledger_attestation(run_id)
            self.assertEqual("", manifest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

