from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from code_atlas.operational import hardened_runner
from code_atlas.operational import (
    breakage,
    client_followup,
    device_claims,
    flow_health,
    gates,
    html_tabs,
    sales_lineage,
)
from code_atlas.operational.capability_contracts import (
    FORMER_PLACEHOLDERS,
    build_capability_specs,
    observe_runtime_bindings,
    validate_capability_specs,
)
from code_atlas.operational.features50 import FEATURE_REGISTRY_VERSION, FEATURE_SPECS


class OperationalHardeningTests(unittest.TestCase):
    def test_registry_preserves_50_legacy_entries_but_adds_hardening_contract(self) -> None:
        self.assertEqual(FEATURE_REGISTRY_VERSION, "2.0.0")
        self.assertEqual(len(FEATURE_SPECS), 50)
        self.assertEqual(sum(row["status"] == "implemented_v1" for row in FEATURE_SPECS), 35)
        self.assertEqual(sum(row["status"] == "placeholder_v1" for row in FEATURE_SPECS), 14)
        self.assertEqual(sum(row["status"] == "placeholder_blocked" for row in FEATURE_SPECS), 1)

        hardened = build_capability_specs(FEATURE_SPECS)
        result = validate_capability_specs(hardened)
        self.assertEqual(result["status"], "PASS_CAPABILITY_CONTRACTS_VALID")
        self.assertEqual(result["formerPlaceholderCount"], 15)
        self.assertTrue(all(row["certifiable"] is False for row in hardened))
        self.assertTrue(all(row["productionCertified"] is False for row in hardened))
        self.assertTrue(all(row["doesNotProve"] for row in hardened))

    def test_historical_trend_foundation_is_not_certified_without_runtime_output(self) -> None:
        specs = build_capability_specs(FEATURE_SPECS)
        observed = observe_runtime_bindings(specs, payload={})
        trend = next(row for row in observed if row["capabilityId"] == "historical_trend_mini_atlas")
        self.assertEqual(trend["implementationState"], "semantic_trend_foundation_v1")
        self.assertEqual(trend["maturity"], "CONTRACT_BACKED")
        self.assertFalse(trend["runtimeOutputObserved"])
        self.assertIn("comparable_snapshot_history_required", trend["hardBlockers"])
        self.assertFalse(trend["certifiable"])

    def test_multi_tenant_contract_requires_negative_isolation_tests(self) -> None:
        spec = next(
            row
            for row in build_capability_specs(FEATURE_SPECS)
            if row["capabilityId"] == "multi_tenant_leakage_guard"
        )
        self.assertTrue(
            {
                "cross_tenant_read",
                "cross_tenant_join",
                "cross_business_projection",
                "wrong_scope_runtime_evidence",
            }.issubset(set(spec["requiredNegativeTests"]))
        )
        self.assertIn("negative_cross_tenant_tests_missing", spec["hardBlockers"])
        self.assertFalse(spec["certifiable"])

    def test_legacy_run_shims_route_through_hardened_runner(self) -> None:
        expected = hardened_runner.run_operational_atlas
        for module in (
            breakage,
            client_followup,
            device_claims,
            flow_health,
            gates,
            html_tabs,
            sales_lineage,
        ):
            self.assertIs(module.run_operational_evidence, expected, module.__name__)

    def test_wrapper_blocks_scope_presence_from_becoming_leakage_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "out"
            out.mkdir()

            base_manifest = {
                "tool": "code_atlas_operational_v3",
                "status": "SOURCE_READY_NOT_PRODUCTION_CERTIFIED",
                "productionGate": "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED",
                "featureCount": 50,
                "detectorsConverted": 15,
                "placeholdersRemaining": 0,
            }
            base_payload = {
                "manifest": dict(base_manifest),
                "multiTenantLeakageGuard": [
                    {
                        "status": "PASS_SCOPE_AUTHORITY_FOUND",
                        "rule": "certify only if real tenant/scope contract exists",
                    }
                ],
                "snapshotDiffEngine": [{"status": "BASELINE"}],
                "surfaceRoleMatrix": [{"status": "PASS"}],
                "operationalTimeline": [{"status": "EMPTY"}],
                "clientRiskScore": [{"status": "PASS"}],
                "orphans": [{"status": "PASS_NO_ORPHANS_IN_SAMPLE"}],
                "stalenessMonitor": [{"status": "PASS_TIMESTAMPS_PRESENT_IN_SAMPLE"}],
                "auditCompleteness": [{"status": "PASS"}],
                "dataLineageGraph": [{"status": "EMPTY_NO_EDGES"}],
                "runtimeEvidenceLinks": [{"status": "BLOCKED_NO_RESULT_ZIPS"}],
                "clientSetupJourneyMap": [{"status": "PASS"}],
                "goldenPathComparator": [{"status": "SOURCE_READY_NOT_PRODUCTION_CERTIFIED"}],
            }

            def fake_base(repo_root: str, output_dir: str, result_root=None):
                destination = Path(output_dir)
                destination.mkdir(parents=True, exist_ok=True)
                (destination / "ATLAS_MANIFEST_PLUS.json").write_text(
                    json.dumps(base_manifest), encoding="utf-8"
                )
                (destination / "operational_evidence_atlas.json").write_text(
                    json.dumps(base_payload), encoding="utf-8"
                )
                (destination / "SMOKE.json").write_text(
                    json.dumps({"status": "PASS", "requiredFiles": []}), encoding="utf-8"
                )
                for name in (
                    "WHY_THIS_IS_RED.md",
                    "HUMAN_OPERATOR_SUMMARY.md",
                    "CONTINUATION_SUPREME.md",
                    "CAN_PATCH_DECISION.md",
                ):
                    (destination / name).write_text(name, encoding="utf-8")
                return dict(base_manifest)

            with mock.patch.object(hardened_runner, "_run_base_operational_atlas", fake_base):
                manifest = hardened_runner.run_operational_atlas(str(root), str(out), None)

            payload = json.loads((out / "operational_evidence_atlas.json").read_text(encoding="utf-8"))
            guard = payload["multiTenantLeakageGuard"][0]
            self.assertTrue(guard["scopeAuthorityObserved"])
            self.assertEqual(guard["status"], "BLOCKED_NEGATIVE_ISOLATION_TESTS_REQUIRED")
            self.assertFalse(guard["certifiable"])
            self.assertFalse(guard["productionCertified"])

            self.assertFalse(manifest["productionCertified"])
            self.assertEqual(manifest["hardeningCertifiableCount"], 0)
            self.assertEqual(manifest["legacyRegistryPlaceholderCount"], len(FORMER_PLACEHOLDERS))
            self.assertTrue((out / "CAPABILITY_HARDENING_LEDGER.json").exists())
            self.assertTrue((out / "CAPABILITY_MATURITY_SUMMARY.json").exists())
            self.assertTrue((out / "FOUNDATION_HARDENING_SUMMARY.json").exists())
            self.assertTrue((out / "SEMANTIC_SNAPSHOT.json").exists())
            self.assertTrue((out / "HARDENING_SUMMARY.md").exists())

            legacy = json.loads((out / "placeholder_ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(len(legacy), 15)
            self.assertTrue(all(row["legacyPlaceholder"] is True for row in legacy))
            self.assertTrue(all(row["certifiable"] is False for row in legacy))

            trend = next(row for row in legacy if row["feature"] == "historical_trend_mini_atlas")
            self.assertTrue(trend["runtimeOutputObserved"])
            self.assertEqual(trend["maturity"], "CONTRACT_BACKED")


if __name__ == "__main__":
    unittest.main()
