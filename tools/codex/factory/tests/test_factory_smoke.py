from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import common, contracts, preflight
from factory.smoke import run_smoke
from factory.tests.test_support import isolated_factory_env


class FactorySmokeTests(unittest.TestCase):
    def test_smoke_passes(self) -> None:
        payload = run_smoke("factory_smoke_test_20260218_000000_001")
        self.assertEqual("PASS", payload["status"])
        self.assertTrue(payload["deterministic"])

    def test_preflight_autorepair_repairs_required_paths(self) -> None:
        with isolated_factory_env() as env:
            run_id = "preflight_autorepair_20260301_000001"
            run_py = env["codex_dir"] / "run.py"
            validation_json = env["codex_dir"] / "validation.json"
            if run_py.exists():
                run_py.unlink()
            if validation_json.exists():
                validation_json.unlink()

            payload = preflight.run_preflight(run_id, auto_repair=True)
            self.assertEqual("PASS", payload["status"])
            self.assertGreaterEqual(payload.get("repairs_applied", 0), 1)
            self.assertTrue(run_py.exists())
            self.assertTrue(validation_json.exists())

    def test_auto_closeout_repairs_missing_codex_output(self) -> None:
        with isolated_factory_env():
            run_id = "autocloseout_20260301_000001"
            worker = "A_worker"
            contracts.scaffold_worker_bundle(run_id, worker)
            root = contracts.bundle_dir(run_id, worker)
            files_changed = {
                "schema_version": 1,
                "run_id": run_id,
                "owner": worker,
                "changes": [
                    {
                        "path": "docs/factory/CONTRACT.md",
                        "change_type": "modified",
                        "reason": "test",
                        "sha256": "abc",
                    }
                ],
                "noop": False,
                "noop_reason": "",
                "noop_ack": "",
            }
            (root / "FILES_CHANGED.json").write_text(
                json.dumps(files_changed, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            (root / "CODEX_OUTPUT.txt").unlink(missing_ok=True)

            payload = contracts.autocloseout_worker_bundle(run_id, worker)
            self.assertEqual("PASS", payload["status"])
            self.assertTrue((root / "CODEX_OUTPUT.txt").exists())

            contracts.scaffold_integrator_bundle(run_id)
            for other in common.WORKERS:
                if other == worker:
                    continue
                contracts.scaffold_worker_bundle(run_id, other)
            validate_payload = contracts.validate_run(run_id, workers=list(common.WORKERS), auto_closeout=True)
            self.assertEqual("PASS", validate_payload["status"])


if __name__ == "__main__":
    unittest.main()
