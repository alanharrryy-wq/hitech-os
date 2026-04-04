from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from forgeos.shared.pyside6_glass.ux_flight_recorder import comparator, runner, specs
from forgeos.shared.pyside6_glass.ux_flight_recorder.recorder import SessionRecorder


class UxFlightRecorderTests(unittest.TestCase):
    def test_golden_sessions_spec_includes_required_sessions(self) -> None:
        payload = specs.load_golden_sessions()
        sessions = payload.get("sessions", [])
        self.assertIsInstance(sessions, list)
        ids = {str(item.get("session_id", "")).strip() for item in sessions if isinstance(item, dict)}
        required = {
            "startup_blank_workspace",
            "picker_search_and_category",
            "add_to_current_tab",
            "open_in_new_tab",
            "drag_panel_cross_slot",
            "resize_panel_and_clamp",
            "clone_reset_isolation",
            "data_runtime_probe_states",
        }
        self.assertTrue(required.issubset(ids))
        for session in sessions:
            if not isinstance(session, dict):
                continue
            self.assertTrue(str(session.get("purpose", "")).strip())
            self.assertTrue(str(session.get("failure_severity", "")).strip())
            self.assertIsInstance(session.get("steps", []), list)
            self.assertIsInstance(session.get("checkpoints", []), list)

    def test_session_recorder_writes_manifest_events_and_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recorder = SessionRecorder(
                session_id="unit_session",
                output_dir=root / "session",
                purpose="unit test session",
                failure_severity="major",
                required_capabilities=[1, 2, 3],
                expected_checkpoints=["cp.one"],
            )
            recorder.log_event("interaction", "clicked")
            recorder.checkpoint(checkpoint_id="cp.one", snapshot={"active_tab_id": "tab-1"})
            manifest = recorder.finalize(passed=True)
            self.assertTrue(bool(manifest.get("passed")))
            self.assertIn("interaction", manifest.get("event_types", []))
            self.assertTrue((root / "session" / "manifest.json").is_file())
            self.assertTrue((root / "session" / "events.json").is_file())
            self.assertTrue((root / "session" / "checkpoints" / "cp.one.json").is_file())

    def test_comparator_detects_missing_session_and_checkpoint(self) -> None:
        baseline = {
            "version": "v1",
            "sessions": {
                "alpha": {
                    "passed": True,
                    "event_count": 2,
                    "event_types": ["interaction", "checkpoint"],
                    "expected_checkpoints": ["cp.a"],
                    "checkpoints": {"cp.a": {"snapshot": {"active_tab_id": "A", "selected_entry_id": ""}}},
                }
            },
            "covered_capabilities": [1, 2],
        }
        run_payload = {
            "version": "v1",
            "sessions": {
                "alpha": {
                    "passed": False,
                    "event_count": 0,
                    "event_types": [],
                    "expected_checkpoints": ["cp.a"],
                    "checkpoints": {},
                }
            },
            "covered_capabilities": [],
        }
        result = comparator.compare_semantic_baseline(
            baseline=baseline,
            run_payload=run_payload,
            required_session_ids=["alpha"],
            required_capabilities=[1, 2],
        )
        self.assertFalse(bool(result.get("passed")))
        self.assertGreater(int(result.get("diff_count", 0)), 0)
        severities = {str(item.get("severity", "")) for item in result.get("diffs", [])}
        self.assertIn("blocker", severities)

    def test_runner_generates_bundle_and_baseline(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            semantic_baseline = root / "baseline" / "semantic_baseline.json"
            visual_baseline = root / "baseline" / "visual_baseline_manifest.json"
            baseline_root = root / "baseline"
            output_root = root / "artifacts"
            command = [
                sys.executable,
                "-m",
                "forgeos.shared.pyside6_glass.ux_flight_recorder.runner",
                "--refresh-baseline",
                "--no-screenshots",
                "--output-root",
                str(output_root),
                "--baseline-root",
                str(baseline_root),
                "--semantic-baseline-path",
                str(semantic_baseline),
                "--visual-baseline-path",
                str(visual_baseline),
                "--extra-evidence-tag",
                "check:test_ux_flight_recorder:pass",
            ]
            proc = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
                env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"runner failed: stdout={proc.stdout}\nstderr={proc.stderr}",
            )
            summary = json.loads(proc.stdout)
            self.assertTrue(bool(summary.get("passed")))
            run_dir = Path(str(summary.get("run_dir", "")))
            self.assertTrue(run_dir.is_dir())
            self.assertTrue((run_dir / "UX_RELEASE_PROOF.md").is_file())
            self.assertTrue((run_dir / "golden_sessions_summary.json").is_file())
            self.assertTrue((run_dir / "comparison_report.json").is_file())
            self.assertTrue((run_dir / "capability_matrix_delta.json").is_file())
            self.assertTrue(semantic_baseline.is_file())
            self.assertTrue(visual_baseline.is_file())
            baseline_payload = json.loads(semantic_baseline.read_text(encoding="utf-8"))
            self.assertEqual(str(baseline_payload.get("version", "")), "v1")


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    unittest.main()
