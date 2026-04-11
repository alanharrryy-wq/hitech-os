from __future__ import annotations

import json
import tempfile
import types
import unittest
from pathlib import Path

from capatch_audit.run_store import finalize_run, start_run
from capatch_audit.telemetry import enrich_payload, refresh_existing_telemetry, write_telemetry_report


class TelemetryArtifactTests(unittest.TestCase):
    def test_enrich_and_write_report_emits_required_metadata(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_phase4_meta_") as tmp_dir:
            root = Path(tmp_dir)
            payload = enrich_payload(
                {"name": "unit_meta", "status": "passed", "answer": 42},
                root_dir=root,
                artifact_kind="telemetry-report",
                artifact_scope="reports/telemetry/unit_meta",
                run_id="run-1",
            )
            paths = write_telemetry_report(root / "reports" / "telemetry", "unit_meta", payload, ["## body", "", "- ok"])
            data = json.loads((root / "reports" / "telemetry" / "unit_meta.json").read_text(encoding="utf-8"))
            self.assertEqual("passed", data["status"])
            self.assertEqual("run-1", data["run_id"])
            self.assertIn("generated_at_utc", data)
            self.assertIn("environment_fingerprint", data)
            self.assertEqual(str(root / "reports" / "telemetry" / "unit_meta.json"), paths["json"])
            self.assertTrue(Path(paths["md"]).exists())

    def test_refresh_marks_runtime_mismatch_historical(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_phase4_refresh_") as tmp_dir:
            root = Path(tmp_dir)
            output = root / "reports" / "telemetry"
            output.mkdir(parents=True, exist_ok=True)
            stale = {
                "name": "windows_smoke",
                "status": "passed",
                "runtime_version": "5.0.0",
                "artifact_kind": "telemetry-report",
                "artifact_scope": "reports/telemetry/windows_smoke",
                "source_command": "old-command",
                "root_dir": str(root),
                "environment_fingerprint": {"python_version": "3.13"},
                "payload_digest": "abc",
            }
            (output / "windows_smoke.json").write_text(json.dumps(stale, indent=2), encoding="utf-8")
            actions = refresh_existing_telemetry(root)
            self.assertEqual(1, len(actions))
            data = json.loads((output / "windows_smoke.json").read_text(encoding="utf-8"))
            self.assertTrue(data["is_historical"])
            self.assertIn("historical_reason", data)

    def test_start_run_records_trace_report_refs_and_environment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_phase4_run_store_") as tmp_dir:
            root = Path(tmp_dir)
            ctx = types.SimpleNamespace(
                root_dir=root,
                invocation_mode="patch-run",
                checkpoint_dir=root / ".capatch" / "backups" / "patches" / "run-1",
                run_id="run-1",
                trace_id="trace-1",
            )
            preflight = types.SimpleNamespace(target_files=["pkg/service.py"], operation_count=1)
            record = start_run(ctx, preflight, {"required_verifiers": ["python-import-smoke"]})
            self.assertEqual("trace-1", record.trace_id)
            self.assertIn("json", record.report_refs)
            self.assertIn("python_executable", record.environment_fingerprint)
            record = finalize_run(record, [], [])
            self.assertIn("md", record.report_refs)


if __name__ == "__main__":
    unittest.main()
