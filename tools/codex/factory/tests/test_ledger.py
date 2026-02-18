from __future__ import annotations

import json
import sys
import tempfile
import threading
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.ledger import (  # noqa: E402
    CorruptLedgerError,
    append_event,
    append_run,
    query_events,
    query_run_ids,
    query_runs,
    read_events,
    replay_ledger,
    verify_ledger_signature,
)


def _event(run_id: str, *, ts: str, event_type: str, rc: int = 0, status: str = "PASS") -> dict[str, object]:
    return {
        "schema_version": 1,
        "ts_utc": ts,
        "run_id": run_id,
        "event_type": event_type,
        "actor": "Z_integrator",
        "event_id": "",
        "parent_event_id": "",
        "duration_ms": 0,
        "file_counts": {},
        "hashes": {"sample": "abc"},
        "rc": rc,
        "details": {"kind": "factory", "status": status},
    }


class LedgerTests(unittest.TestCase):
    def test_append_event_writes_jsonl_line(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_append_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            payload = _event("factory_20260218_101010_001", ts="2026-02-18T10:10:10+00:00", event_type="RUN_START")
            append_event(payload, path=ledger_path)

            lines = ledger_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(1, len(lines))
            parsed = json.loads(lines[0])
            self.assertEqual(payload["run_id"], parsed["run_id"])
            self.assertEqual(payload["event_type"], parsed["event_type"])
            self.assertEqual(payload["actor"], parsed["actor"])
            self.assertEqual(payload["rc"], parsed["rc"])

    def test_append_only_never_rewrites_previous_lines(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_append_only_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            append_event(_event("factory_20260218_101010_001", ts="2026-02-18T10:10:10+00:00", event_type="RUN_START"), path=ledger_path)
            first_size = ledger_path.stat().st_size

            append_event(_event("factory_20260218_101010_001", ts="2026-02-18T10:10:11+00:00", event_type="WORKTREE_CREATE"), path=ledger_path)
            second_size = ledger_path.stat().st_size
            self.assertGreater(second_size, first_size)

            events = read_events(path=ledger_path)
            self.assertEqual(2, len(events))
            self.assertEqual("RUN_START", events[0]["event_type"])
            self.assertEqual("WORKTREE_CREATE", events[1]["event_type"])

    def test_query_events_sorted_by_ts_then_event_type(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_sort_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            append_event(_event("run_a", ts="2026-02-18T10:10:12+00:00", event_type="WORKTREE_CREATE"), path=ledger_path)
            append_event(_event("run_a", ts="2026-02-18T10:10:11+00:00", event_type="BUNDLE_VALIDATED"), path=ledger_path)
            append_event(_event("run_a", ts="2026-02-18T10:10:11+00:00", event_type="RUN_START"), path=ledger_path)
            append_event(_event("run_a", ts="2026-02-18T10:10:13+00:00", event_type="RUN_END"), path=ledger_path)

            queried = query_events(limit=10, path=ledger_path)
            order = [(entry["ts_utc"], entry["event_type"]) for entry in queried]
            self.assertEqual(
                [
                    ("2026-02-18T10:10:11+00:00", "BUNDLE_VALIDATED"),
                    ("2026-02-18T10:10:11+00:00", "RUN_START"),
                    ("2026-02-18T10:10:12+00:00", "WORKTREE_CREATE"),
                    ("2026-02-18T10:10:13+00:00", "RUN_END"),
                ],
                order,
            )

    def test_query_runs_preserves_ledger_fields(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_runs_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            append_run(
                {
                    "run_id": "factory_20260218_101010_001",
                    "kind": "factory",
                    "status": "PASS",
                    "path": "tools/codex/runs/factory_20260218_101010_001",
                    "report": "tools/codex/runs/factory_20260218_101010_001/Z_integrator/FINAL_REPORT.txt",
                    "workers": ["A_worker", "B_worker", "C_worker", "D_worker"],
                    "started_at": "2026-02-18T10:10:10+00:00",
                    "ended_at": "2026-02-18T10:10:11+00:00",
                },
                path=ledger_path,
            )
            rows = query_runs(limit=5, path=ledger_path)
            self.assertEqual(1, len(rows))
            row = rows[0]
            self.assertEqual("factory_20260218_101010_001", row["run_id"])
            self.assertEqual("RUN_STATE", row["event_type"])
            self.assertEqual("Z_integrator", row["actor"])
            self.assertEqual(0, row["rc"])

    def test_query_run_ids_returns_sorted_unique(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_ids_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            append_event(_event("factory_20260218_101010_002", ts="2026-02-18T10:10:12+00:00", event_type="RUN_START"), path=ledger_path)
            append_event(_event("factory_20260218_101010_001", ts="2026-02-18T10:10:10+00:00", event_type="RUN_START"), path=ledger_path)
            append_event(_event("factory_20260218_101010_001", ts="2026-02-18T10:10:13+00:00", event_type="RUN_END"), path=ledger_path)
            self.assertEqual(
                ["factory_20260218_101010_001", "factory_20260218_101010_002"],
                query_run_ids(path=ledger_path),
            )

    def test_invalid_event_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_invalid_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            with self.assertRaises(ValueError):
                append_event(
                    {
                        "schema_version": 1,
                        "ts_utc": "",
                        "run_id": "",
                        "event_type": "",
                        "actor": "",
                        "event_id": "",
                        "parent_event_id": "",
                        "duration_ms": 0,
                        "file_counts": {},
                        "hashes": {},
                        "rc": 0,
                        "details": {},
                    },
                    path=ledger_path,
                )

    def test_signature_file_written(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_sig_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            sig_path = Path(temp_dir) / "factory_ledger.sha256"
            append_event(
                _event("factory_20260218_101010_001", ts="2026-02-18T10:10:10+00:00", event_type="RUN_START"),
                path=ledger_path,
                signature_path=sig_path,
            )
            self.assertTrue(sig_path.exists())
            verification = verify_ledger_signature(path=ledger_path, signature_path=sig_path)
            self.assertEqual("PASS", verification["status"])

    def test_replay_reconstructs_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_replay_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            append_event(_event("run_1", ts="2026-02-18T10:00:00+00:00", event_type="RUN_START"), path=ledger_path)
            append_event(_event("run_1", ts="2026-02-18T10:00:01+00:00", event_type="RUN_END"), path=ledger_path)
            append_event(_event("run_2", ts="2026-02-18T10:01:00+00:00", event_type="RUN_START"), path=ledger_path)
            replay = replay_ledger(path=ledger_path)
            self.assertEqual("PASS", replay["status"])
            self.assertEqual(2, replay["count"])
            run_ids = [item["run_id"] for item in replay["runs"]]
            self.assertEqual(["run_1", "run_2"], run_ids)

    def test_corrupt_ledger_detected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_corrupt_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            ledger_path.write_text("{bad json}\n", encoding="utf-8")
            with self.assertRaises(CorruptLedgerError):
                read_events(path=ledger_path, strict=True)

    def test_concurrent_appends(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ledger_concurrency_") as temp_dir:
            ledger_path = Path(temp_dir) / "factory_ledger.jsonl"
            sig_path = Path(temp_dir) / "factory_ledger.sha256"
            lock_path = Path(temp_dir) / "factory_ledger.lock"
            errors: list[str] = []

            def _writer(index: int) -> None:
                try:
                    append_event(
                        _event(
                            f"run_{index:03d}",
                            ts=f"2026-02-18T10:10:{index:02d}+00:00",
                            event_type="RUN_STATE",
                        ),
                        path=ledger_path,
                        signature_path=sig_path,
                        lock_path=lock_path,
                    )
                except Exception as exc:  # pragma: no cover
                    errors.append(str(exc))

            threads = [threading.Thread(target=_writer, args=(idx,)) for idx in range(10)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            self.assertEqual([], errors)
            events = read_events(path=ledger_path)
            self.assertEqual(10, len(events))
            self.assertEqual("PASS", verify_ledger_signature(path=ledger_path, signature_path=sig_path)["status"])


if __name__ == "__main__":
    unittest.main()
