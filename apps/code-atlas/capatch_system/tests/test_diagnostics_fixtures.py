
from __future__ import annotations

import shutil
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from tests.qa_testkit import FIXTURES

from capatch_diagnostics.loader import empty_plugin_state
from capatch_diagnostics.runtime import build_session, run_session, run_session_reports


class DiagnosticsFixtureTests(unittest.TestCase):
    def _run_fixture(self, fixture_name: str):
        tmp = tempfile.TemporaryDirectory(prefix=f"capatch_diag_{fixture_name}_")
        self.addCleanup(tmp.cleanup)
        base_dir = Path(tmp.name)
        source = FIXTURES / fixture_name
        target = base_dir / fixture_name
        shutil.copytree(source, target, dirs_exist_ok=True)
        args = Namespace(
            target_path=fixture_name,
            app_kind="auto",
            collect_only=False,
            verify_only=False,
            support_bundle=True,
            fix_plan=False,
            apply_fixes=False,
            dry_diagnose=True,
            include_logs=True,
            include_processes=False,
            include_ports=False,
            include_git=False,
            include_build=False,
            include_tests=False,
            max_log_lines=40,
            max_log_bytes=65536,
            command_timeout_seconds=15,
            bundle_format="all",
        )
        state = empty_plugin_state()
        session = build_session(args, base_dir, state)
        session = run_session(session, state)
        written = run_session_reports(base_dir, session)
        return base_dir, target, session, written

    def test_python_node_web_db_and_docker_fixtures_run_diagnostics(self) -> None:
        expectations = {
            "sample_python_app": "python",
            "sample_node_app": "node",
            "sample_web_app": "web",
            "sample_db_app": "unknown",
            "sample_docker_app": "unknown",
        }
        for fixture_name, expected_kind in expectations.items():
            with self.subTest(fixture=fixture_name):
                _base_dir, target, session, written = self._run_fixture(fixture_name)
                self.assertEqual(expected_kind, session.app_kind)
                self.assertFalse(session.errors)
                self.assertTrue(session.finished_at)
                self.assertGreaterEqual(len(session.artifacts), 1)
                self.assertIn("session_json", written)
                self.assertIn("bundle_json", written)
                markers = session.environment_summary["workspace_markers"]
                if fixture_name in {"sample_db_app", "sample_docker_app"}:
                    self.assertTrue(markers["has_docker_compose"])
                if fixture_name == "sample_python_app":
                    self.assertTrue((target / "setup.py").exists())
                if fixture_name == "sample_node_app":
                    self.assertTrue((target / "package-lock.json").exists())
                if fixture_name == "sample_web_app":
                    self.assertFalse(markers["has_package_json"])

    def test_support_bundle_writes_human_and_machine_outputs(self) -> None:
        _base_dir, _target, session, written = self._run_fixture("sample_python_app")
        self.assertIn("session_md", written)
        self.assertIn("bundle_md", written)
        self.assertTrue(Path(written["session_json"]).exists())
        self.assertTrue(Path(written["bundle_json"]).exists())
        self.assertGreaterEqual(len(session.recommendations), 1)


if __name__ == "__main__":
    unittest.main()
