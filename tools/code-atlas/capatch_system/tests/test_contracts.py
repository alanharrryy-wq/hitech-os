
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.qa_testkit import ROOT

from capatch_contracts import (
    EXECUTION_MODES,
    MANDATORY_OUTPUT_FILES,
    PATCH_OPERATION_TYPES,
    REPORT_DIRS,
    RISK_TIERS,
    RUNTIME_PHASES,
    SEMANTIC_OPERATION_TYPES,
)
from capatch_diagnostics.loader import initialize_plugin_runtime


class ContractSmokeTests(unittest.TestCase):
    def test_schema_files_are_present_and_parseable(self) -> None:
        schema_dir = ROOT / "capatch_contracts" / "schemas"
        expected = {
            "operation.schema.json",
            "patch_run.schema.json",
            "plugin_payload.schema.json",
            "verification_result.schema.json",
            "intervention_gate.schema.json",
            "baseline.schema.json",
            "telemetry_artifact.schema.json",
        }
        found = {path.name for path in schema_dir.glob("*.json")}
        self.assertEqual(expected, found)
        for name in sorted(expected):
            payload = json.loads((schema_dir / name).read_text(encoding="utf-8"))
            self.assertEqual("object", payload["type"])

    def test_phase_and_execution_mode_contracts_match_spec(self) -> None:
        self.assertEqual(
            (
                "resolve-target",
                "collect",
                "enrich",
                "analyze",
                "recommend",
                "fix",
                "verify",
                "export",
            ),
            tuple(RUNTIME_PHASES),
        )
        self.assertIn("patch-run", EXECUTION_MODES)
        self.assertIn("apply-fixes", EXECUTION_MODES)
        self.assertIn("rollback-apply", EXECUTION_MODES)
        self.assertEqual(("safe", "guarded", "high-risk", "blocked"), tuple(RISK_TIERS))

    def test_operation_families_include_textual_and_semantic_ops(self) -> None:
        self.assertIn("ReplaceExactOnce", PATCH_OPERATION_TYPES)
        self.assertIn("NormalizeFile", PATCH_OPERATION_TYPES)
        self.assertIn("SetJsonValue", SEMANTIC_OPERATION_TYPES)
        self.assertIn("InsertPythonFunctionArg", SEMANTIC_OPERATION_TYPES)

    def test_report_catalog_has_mandatory_directories_and_outputs(self) -> None:
        self.assertIn("reports/telemetry", REPORT_DIRS)
        self.assertIn("diagnostic_session_json", MANDATORY_OUTPUT_FILES)
        self.assertIn("before_after_verification_md", MANDATORY_OUTPUT_FILES)

    def test_plugin_runtime_contract_smoke_loads_flat_layout(self) -> None:
        state = initialize_plugin_runtime(ROOT)
        self.assertTrue(state["initialized"])
        self.assertGreaterEqual(state["load_summary"]["discovered"], 1)
        self.assertGreaterEqual(len(state["registry"]), 1)
        total_known = state["load_summary"]["active"] + state["load_summary"]["rejected"] + state["load_summary"]["disabled"]
        self.assertGreaterEqual(total_known, 1)
        registry = state["registry"]
        for plugin_id, entry in registry.items():
            self.assertIn(entry["status"], {"active", "disabled", "rejected"})
            self.assertTrue(entry["path"])
            self.assertTrue(entry["hash"])

    def test_qa_tooling_entrypoints_exist(self) -> None:
        for relative in (
            "tooling/run_plugin_contract_smoke.py",
            "tooling/run_windows_smoke.py",
            "tooling/run_rollback_drill.py",
            "tooling/run_qa_benchmark_suite.py",
        ):
            self.assertTrue((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
