import importlib
import os
import sys
from pathlib import Path
from unittest import TestCase

APP_HOST_ROOT = Path(__file__).resolve().parents[5]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

snapshot_model = importlib.import_module("app.gui_qt.plugins.cloudflare_guardian.snapshot_model")


class SnapshotModelTests(TestCase):
    def test_normalize_snapshot_coerces_types_and_defaults(self):
        normalized = snapshot_model.normalize_snapshot(
            {
                "repo_root": 123,
                "repo_ready": "true",
                "index_file_count": "18",
                "index_elapsed_sec": "1.75",
                "nodes": ("a", "b"),
                "edges": None,
            }
        )
        self.assertEqual(normalized["repo_root"], "123")
        self.assertTrue(normalized["repo_ready"])
        self.assertEqual(normalized["index_file_count"], 18)
        self.assertAlmostEqual(normalized["index_elapsed_sec"], 1.75)
        self.assertEqual(normalized["nodes"], ["a", "b"])
        self.assertEqual(normalized["edges"], [])
        self.assertEqual(normalized["focus_node_id"], "")

    def test_normalize_snapshot_handles_missing_input(self):
        normalized = snapshot_model.normalize_snapshot(None)
        self.assertEqual(normalized, snapshot_model.empty_snapshot())

    def test_format_elapsed_has_stable_output(self):
        self.assertEqual(snapshot_model.format_elapsed(0), "0.0s")
        self.assertEqual(snapshot_model.format_elapsed(1.234), "1.23s")
        self.assertEqual(snapshot_model.format_elapsed(12.34), "12.3s")

