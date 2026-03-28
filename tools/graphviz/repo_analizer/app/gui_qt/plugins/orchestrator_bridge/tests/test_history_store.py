import importlib
import json
import os
import tempfile
from pathlib import Path
from unittest import TestCase

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_ROOT = PACKAGE_ROOT.parent
if str(PLUGINS_ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(PLUGINS_ROOT))

bridge_config = importlib.import_module("orchestrator_bridge.bridge_config")
history_module = importlib.import_module("orchestrator_bridge.bridge_history")


def _make_config(runtime_root: str) -> bridge_config.BridgeConfig:
    return bridge_config.BridgeConfig(
        one_button_path=r"F:\repos\hitech-os\tools\orchestrator_factory\tools\one_button.ps1",
        default_handoff_dir=r"F:\OneDrive\Descargas",
        runtime_root=runtime_root,
        startup_timeout_ms=15000,
        run_timeout_ms=1800000,
        kill_after_timeout_ms=3000,
        max_runs=25,
        config_path="",
    )


class BridgeHistoryStoreTests(TestCase):
    def test_append_record_deduplicates_and_prefers_richer_exit_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = history_module.BridgeHistoryStore(_make_config(temp_dir))
            base = {
                "timestamp": "2026-03-28 17:01:08 UTC",
                "status": "failed",
                "mode": "new_project",
                "policy": "open_new_round",
                "project_id": "repo-analizer",
                "session_id": "",
                "zip_path": "",
                "request": {
                    "mode": "new_project",
                    "policy": "open_new_round",
                    "project_id": "repo-analizer",
                },
            }
            left = dict(base)
            left["exit_code"] = "<none>"
            right = dict(base)
            right["exit_code"] = 62097
            right["message"] = "Process launch failed: 62097"

            merged = store.append_record([left], right)

            self.assertEqual(len(merged), 1)
            self.assertEqual(str(merged[0].get("exit_code")), "62097")
            self.assertEqual(merged[0].get("mode"), "new_project")
            self.assertEqual(merged[0].get("policy"), "open_new_round")

    def test_load_records_normalizes_legacy_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg = _make_config(temp_dir)
            os.makedirs(cfg.runtime_root, exist_ok=True)
            payload = [
                {
                    "timestamp": "2026-03-28 14:22:05 UTC",
                    "status": "blocked",
                    "mode": "existing",
                    "policy": "cloudflare_guardian_check",
                    "project_id": "cloudflare-guardian",
                    "exit_code": None,
                    "request": "legacy-bad-shape",
                }
            ]
            with open(cfg.history_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)

            store = history_module.BridgeHistoryStore(cfg)
            rows = store.load_records()

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].get("mode"), "existing_project")
            self.assertEqual(rows[0].get("policy"), "resume_latest_round")
            self.assertEqual(rows[0].get("exit_code"), "<none>")
            request = rows[0].get("request")
            self.assertIsInstance(request, dict)
            self.assertEqual(request.get("mode"), "existing_project")
            self.assertEqual(request.get("policy"), "resume_latest_round")

    def test_load_records_maps_launch_failure_without_exit_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg = _make_config(temp_dir)
            os.makedirs(cfg.runtime_root, exist_ok=True)
            payload = [
                {
                    "timestamp": "2026-03-28 17:08:20 UTC",
                    "status": "failed",
                    "mode": "new_project",
                    "policy": "open_new_round",
                    "project_id": "repo",
                    "contract_detail": "LaunchFailure",
                    "exit_code": "<none>",
                    "request": {"mode": "new_project", "policy": "open_new_round", "project_id": "repo"},
                }
            ]
            with open(cfg.history_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)

            store = history_module.BridgeHistoryStore(cfg)
            rows = store.load_records()

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].get("exit_code"), "process_error")

    def test_load_records_normalizes_request_mode_and_policy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg = _make_config(temp_dir)
            os.makedirs(cfg.runtime_root, exist_ok=True)
            payload = [
                {
                    "timestamp": "2026-03-28 17:20:00 UTC",
                    "status": "blocked",
                    "mode": "existing",
                    "policy": "cloudflare_guardian_check",
                    "project_id": "legacy",
                    "exit_code": "50",
                    "request": {
                        "mode": "existing",
                        "policy": "cloudflare_guardian_check",
                        "project_id": "legacy",
                    },
                }
            ]
            with open(cfg.history_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)

            store = history_module.BridgeHistoryStore(cfg)
            rows = store.load_records()
            req = rows[0].get("request")

            self.assertIsInstance(req, dict)
            self.assertEqual(req.get("mode"), "existing_project")
            self.assertEqual(req.get("policy"), "resume_latest_round")
