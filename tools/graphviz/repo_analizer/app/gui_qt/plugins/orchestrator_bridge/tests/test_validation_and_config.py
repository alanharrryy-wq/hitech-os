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

plugin = importlib.import_module("orchestrator_bridge.plugin")


class ValidationAndConfigTests(TestCase):
    def test_validate_request_payload_rejects_empty_project_id_in_non_interactive(self):
        errors = plugin.validate_request_payload({
            "mode": "existing_project",
            "policy": "safe-default",
            "project_id": "",
            "intent": "run it",
            "non_interactive": True,
        })
        self.assertIn("Project ID is required when Non-interactive is enabled.", errors)

    def test_validate_request_payload_rejects_bad_project_id(self):
        errors = plugin.validate_request_payload({
            "mode": "existing_project",
            "policy": "resume_latest_round",
            "project_id": "bad id!",
            "intent": "run it",
            "non_interactive": True,
        })
        self.assertTrue(any("Project ID contains invalid characters" in item for item in errors))

    def test_validate_request_payload_requires_new_project_core_fields(self):
        errors = plugin.validate_request_payload({
            "mode": "new_project",
            "policy": "open_new_round",
            "project_name": "",
            "initiative_type": "",
            "project_id": "",
            "intent": "",
            "non_interactive": True,
        })
        self.assertTrue(any("Project name is required" in item for item in errors))
        self.assertTrue(any("Initiative type is required" in item for item in errors))
        self.assertTrue(any("Intent is required" in item for item in errors))

    def test_validate_request_payload_requires_intent_for_open_new_round(self):
        errors = plugin.validate_request_payload({
            "mode": "existing_project",
            "policy": "open_new_round",
            "project_id": "alpha-project",
            "intent": "",
            "non_interactive": True,
        })
        self.assertTrue(any("Intent is required when policy is 'open_new_round'" in item for item in errors))

    def test_derive_project_id_from_name_is_deterministic(self):
        slug = plugin.derive_project_id_from_name("  Smoke_Local  -- Ops  ")
        self.assertEqual(slug, "smoke-local-ops")

    def test_bridge_config_rejects_one_button_outside_approved_root(self):
        config = plugin.BridgeConfig(
            one_button_path=r"C:\temp\one_button.ps1",
            default_handoff_dir=r"F:\OneDrive\Descargas",
            runtime_root=r"F:\repos\hitech-os\tools\_local\orchestrator_bridge",
            startup_timeout_ms=15000,
            run_timeout_ms=1800000,
            kill_after_timeout_ms=3000,
            max_runs=25,
            config_path="",
        )
        problems = config.validate()
        self.assertTrue(any("outside the approved orchestrator root" in item for item in problems))

    def test_bridge_config_rejects_runtime_root_outside_tools_local(self):
        config = plugin.BridgeConfig(
            one_button_path=r"F:\repos\hitech-os\tools\orchestrator_factory\tools\one_button.ps1",
            default_handoff_dir=r"F:\OneDrive\Descargas",
            runtime_root=r"F:\repos\hitech-os\tmp",
            startup_timeout_ms=15000,
            run_timeout_ms=1800000,
            kill_after_timeout_ms=3000,
            max_runs=25,
            config_path="",
        )
        problems = config.validate()
        self.assertTrue(any("must stay under tools\\_local" in item for item in problems))

    def test_load_bridge_config_uses_defaults_when_file_is_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config, problems = plugin._load_bridge_config(temp_dir)
            self.assertEqual(config.one_button_path, plugin.DEFAULT_ONE_BUTTON_PATH)
            self.assertEqual(config.default_handoff_dir, plugin.DEFAULT_HANDOFF_DIR)
            self.assertEqual(problems, [])
