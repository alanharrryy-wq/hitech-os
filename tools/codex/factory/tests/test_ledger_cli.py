from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import cli, ledger  # noqa: E402
from factory.tests.test_support import isolated_factory_env  # noqa: E402


class LedgerCliTests(unittest.TestCase):
    def _seed(self) -> None:
        ledger.append_event(
            {
                "schema_version": 1,
                "ts_utc": "2026-02-18T10:10:10+00:00",
                "run_id": "run_a",
                "event_type": "RUN_START",
                "actor": "Z_integrator",
                "hashes": {},
                "rc": 0,
                "details": {"status": "PASS", "kind": "factory"},
            }
        )
        ledger.append_event(
            {
                "schema_version": 1,
                "ts_utc": "2026-02-18T10:10:11+00:00",
                "run_id": "run_a",
                "event_type": "RUN_END",
                "actor": "Z_integrator",
                "hashes": {},
                "rc": 0,
                "details": {"status": "PASS", "kind": "factory"},
            }
        )
        ledger.append_event(
            {
                "schema_version": 1,
                "ts_utc": "2026-02-18T10:11:11+00:00",
                "run_id": "run_b",
                "event_type": "RUN_START",
                "actor": "A_worker",
                "hashes": {},
                "rc": 2,
                "details": {"status": "BLOCKED", "kind": "factory"},
            }
        )

    def test_ledger_query_filters(self) -> None:
        with isolated_factory_env():
            self._seed()
            stream = io.StringIO()
            with redirect_stdout(stream):
                rc = cli.main(["ledger", "--raw-events", "--actor", "A_worker", "--rc", "2", "--limit", "50"])
            self.assertEqual(0, rc)
            payload = json.loads(stream.getvalue())
            self.assertEqual(1, payload["count"])
            self.assertEqual("run_b", payload["entries"][0]["run_id"])

    def test_ledger_replay_command(self) -> None:
        with isolated_factory_env():
            self._seed()
            stream = io.StringIO()
            with redirect_stdout(stream):
                rc = cli.main(["ledger-replay", "--run-id", "run_a"])
            self.assertEqual(0, rc)
            payload = json.loads(stream.getvalue())
            self.assertEqual("PASS", payload["status"])
            self.assertEqual(1, payload["count"])
            self.assertEqual("run_a", payload["runs"][0]["run_id"])


if __name__ == "__main__":
    unittest.main()

