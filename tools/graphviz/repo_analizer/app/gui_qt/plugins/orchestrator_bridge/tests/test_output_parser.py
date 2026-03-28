import importlib
import os
from pathlib import Path
from unittest import TestCase, mock

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_ROOT = PACKAGE_ROOT.parent
if str(PLUGINS_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PLUGINS_ROOT))

plugin = importlib.import_module("orchestrator_bridge.plugin")
FIXTURES = PACKAGE_ROOT / "tests" / "fixtures"


def _read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _make_config() -> plugin.BridgeConfig:
    return plugin.BridgeConfig(
        one_button_path=r"F:\repos\hitech-os\tools\orchestrator_factory\tools\one_button.ps1",
        default_handoff_dir=r"F:\OneDrive\Descargas",
        runtime_root=r"F:\repos\hitech-os\tools\_local\orchestrator_bridge",
        startup_timeout_ms=15000,
        run_timeout_ms=1800000,
        kill_after_timeout_ms=3000,
        max_runs=25,
        config_path="",
    )


class OutputParserTests(TestCase):
    def _parse(self, fixture_name: str, existing_paths=None, source="stdout", exit_code=0):
        parser = plugin._OutputParser(_make_config())
        existing_paths = set(existing_paths or [])
        with mock.patch.object(plugin.os.path, "exists", side_effect=lambda p: p in existing_paths):
            for line in _read_fixture(fixture_name).splitlines():
                parser.ingest_line(line, source)
            return parser.finalize(exit_code=exit_code)

    def test_success_fixture_parses_structured_status_and_zip(self):
        zip_path = r"F:\OneDrive\Descargas\handoff_success.zip"
        result = self._parse("success_stdout.txt", existing_paths={zip_path}, exit_code=0)
        self.assertEqual(result["normalized_status"], "success")
        self.assertEqual(result["contract_detail"], "SucceededWithWarnings")
        self.assertEqual(result["zip_path"], zip_path)
        self.assertTrue(result["zip_path_publicable"])
        self.assertTrue(result["warnings"])

    def test_reused_fixture_falls_back_by_patterns(self):
        zip_path = r"F:\OneDrive\Descargas\handoff_reused.zip"
        result = self._parse("reused_stdout.txt", existing_paths={zip_path}, exit_code=0)
        self.assertEqual(result["normalized_status"], "reused")
        self.assertEqual(result["zip_path"], zip_path)

    def test_blocked_lock_fixture_maps_to_blocked(self):
        result = self._parse("blocked_lock_stderr.txt", source="stderr", exit_code=30)
        self.assertEqual(result["normalized_status"], "blocked")
        self.assertEqual(result["contract_detail"], "Blocked")
        self.assertTrue(result["errors"])

    def test_contract_fail_fixture_tracks_violations(self):
        result = self._parse("contracts_fail_stdout.txt", exit_code=20)
        self.assertEqual(result["normalized_status"], "blocked")
        self.assertTrue(result["contract_violations"])

    def test_runtime_error_fixture_maps_to_failed(self):
        result = self._parse("runtime_error_stderr.txt", source="stderr", exit_code=20)
        self.assertEqual(result["normalized_status"], "failed")
        self.assertTrue(result["errors"])
