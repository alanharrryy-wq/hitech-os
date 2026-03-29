import importlib
import os
import sys
from pathlib import Path
from unittest import TestCase

APP_HOST_ROOT = Path(__file__).resolve().parents[5]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

spec_factory = importlib.import_module("app.gui_qt.plugins.cloudflare_guardian.spec_factory")


class SpecFactoryTests(TestCase):
    def test_build_command_specs_respects_dispatcher_and_snapshot(self):
        snapshot = {
            "results_count": 2,
            "nav_can_go_back": True,
            "nav_can_go_forward": False,
            "current_preview_relpath": "app/main.py",
            "bookmarks_count": 1,
        }
        specs = spec_factory.build_command_specs(
            snapshot,
            dispatcher_has=lambda name: name in {"execute_search", "navigate_back", "open_file"},
        )
        by_name = {item["name"]: item for item in specs}
        self.assertTrue(by_name["execute_search"]["enabled"])
        self.assertTrue(by_name["navigate_back"]["enabled"])
        self.assertFalse(by_name["navigate_forward"]["enabled"])
        self.assertTrue(by_name["open_file"]["enabled"])
        self.assertEqual(by_name["open_file"]["payload"]["relpath"], "app/main.py")
        self.assertFalse(by_name["export_results"]["enabled"])

    def test_build_action_specs_respects_first_seen_and_payload(self):
        snapshot = {
            "results_count": 0,
            "nav_can_go_back": False,
            "nav_can_go_forward": False,
            "current_preview_relpath": "",
            "bookmarks_count": 0,
        }
        actions = spec_factory.build_action_specs(
            snapshot,
            dispatcher_has=lambda _name: True,
        )
        action_ids = [item["action_id"] for item in actions]
        self.assertEqual(len(action_ids), len(set(action_ids)))
        open_action = next(item for item in actions if item["action_id"] == "open_file")
        self.assertFalse(open_action["enabled"])
        self.assertEqual(open_action["payload"], {})

