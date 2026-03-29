import importlib
import os
from pathlib import Path
from unittest import TestCase

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_ROOT = PACKAGE_ROOT.parent
if str(PLUGINS_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PLUGINS_ROOT))

plugin = importlib.import_module("orchestrator_bridge.plugin")


class ExitMappingTests(TestCase):
    def test_success_exit_maps_to_success(self):
        detail = plugin.map_exit_code_to_contract_detail(0, warnings_present=False)
        status = plugin.normalize_contract_detail_to_ui_status(detail)
        self.assertEqual(detail, "Succeeded")
        self.assertEqual(status, "success")

    def test_success_with_reuse_maps_to_reused(self):
        detail = plugin.map_exit_code_to_contract_detail(0, warnings_present=False)
        status = plugin.normalize_contract_detail_to_ui_status(detail, reused_detected=True)
        self.assertEqual(status, "reused")

    def test_blocked_exit_maps_to_blocked(self):
        detail = plugin.map_exit_code_to_contract_detail(30)
        status = plugin.normalize_contract_detail_to_ui_status(detail)
        self.assertEqual(detail, "Blocked")
        self.assertEqual(status, "blocked")

    def test_unknown_exit_with_failed_hint_maps_to_failed(self):
        detail = plugin.map_exit_code_to_contract_detail(999, status_hint="failed")
        status = plugin.normalize_contract_detail_to_ui_status(detail)
        self.assertEqual(detail, "Failed")
        self.assertEqual(status, "failed")
