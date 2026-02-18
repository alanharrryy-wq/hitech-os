from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.ledger import append_event  # noqa: E402
from factory.run_id import next_run_identity  # noqa: E402


class RunIdDeterminismTests(unittest.TestCase):
    def test_sequence_starts_at_one_when_ledger_empty(self) -> None:
        with tempfile.TemporaryDirectory(prefix="runid_empty_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            identity = next_run_identity("factory", "20260218_101010", base_ref="HEAD", ledger_path=ledger_path)
            self.assertRegex(identity.run_id, r"^factory_20260218_101010_[a-f0-9]{8}_001$")
            self.assertEqual(1, identity.sequence)

    def test_sequence_increments_from_existing_entries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="runid_seq_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            seed = next_run_identity("factory", "20260218_101010", base_ref="HEAD", ledger_path=ledger_path)
            prefix = seed.run_id.rsplit("_", 1)[0]
            append_event(
                {
                    "schema_version": 1,
                    "ts_utc": "2026-02-18T10:10:10+00:00",
                    "run_id": f"{prefix}_001",
                    "event_type": "RUN_START",
                    "actor": "Z_integrator",
                    "event_id": "",
                    "parent_event_id": "",
                    "duration_ms": 0,
                    "file_counts": {},
                    "hashes": {},
                    "rc": 0,
                    "details": {"status": "PASS"},
                },
                path=ledger_path,
            )
            append_event(
                {
                    "schema_version": 1,
                    "ts_utc": "2026-02-18T10:10:11+00:00",
                    "run_id": f"{prefix}_002",
                    "event_type": "RUN_START",
                    "actor": "Z_integrator",
                    "event_id": "",
                    "parent_event_id": "",
                    "duration_ms": 0,
                    "file_counts": {},
                    "hashes": {},
                    "rc": 0,
                    "details": {"status": "PASS"},
                },
                path=ledger_path,
            )
            identity = next_run_identity("factory", "20260218_101010", base_ref="HEAD", ledger_path=ledger_path)
            self.assertEqual(f"{prefix}_003", identity.run_id)
            self.assertEqual(3, identity.sequence)

    def test_kind_prefix_isolated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="runid_kind_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            seed = next_run_identity("factory", "20260218_101010", base_ref="HEAD", ledger_path=ledger_path)
            append_event(
                {
                    "schema_version": 1,
                    "ts_utc": "2026-02-18T10:10:10+00:00",
                    "run_id": seed.run_id.rsplit("_", 1)[0] + "_004",
                    "event_type": "RUN_START",
                    "actor": "Z_integrator",
                    "event_id": "",
                    "parent_event_id": "",
                    "duration_ms": 0,
                    "file_counts": {},
                    "hashes": {},
                    "rc": 0,
                    "details": {"status": "PASS"},
                },
                path=ledger_path,
            )
            smoke_identity = next_run_identity("factory_smoke", "20260218_101010", base_ref="HEAD", ledger_path=ledger_path)
            self.assertRegex(smoke_identity.run_id, r"^factory_smoke_20260218_101010_[a-f0-9]{8}_001$")

    def test_invalid_stamp_raises(self) -> None:
        with tempfile.TemporaryDirectory(prefix="runid_badstamp_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            with self.assertRaises(ValueError):
                next_run_identity("factory", "2026-02-18T10:10:10", base_ref="HEAD", ledger_path=ledger_path)


if __name__ == "__main__":
    unittest.main()
