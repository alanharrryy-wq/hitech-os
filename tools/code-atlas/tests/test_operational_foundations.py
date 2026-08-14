from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from code_atlas.operational import final_runner, hardened_runner, html_tabs
from code_atlas.operational.assurance_foundation import validate_runtime_artifact
from code_atlas.operational.evidence_foundation import (
    VOLATILE_KEYS,
    assess_freshness,
    canonical_digest,
)
from code_atlas.operational.lineage_foundation import build_lineage_graph
from code_atlas.operational.temporal_foundation import (
    compare_semantic_snapshots,
    historical_trend,
    make_semantic_snapshot,
)


class OperationalFoundationTests(unittest.TestCase):
    def test_canonical_digest_ignores_order_and_declared_volatile_keys(self) -> None:
        left = {"b": 2, "a": 1, "generatedAt": "2026-08-14T01:00:00Z"}
        right = {"generatedAt": "2026-08-14T02:00:00Z", "a": 1, "b": 2}
        self.assertEqual(
            canonical_digest(left, drop_keys=VOLATILE_KEYS),
            canonical_digest(right, drop_keys=VOLATILE_KEYS),
        )

    def test_snapshot_diff_blocks_without_baseline_and_detects_content_change(self) -> None:
        base = make_semantic_snapshot(
            {"clients": [{"id": "c1", "status": "active"}]},
            observed_at="2026-08-14T10:00:00Z",
            source_ref="test",
        )
        current = make_semantic_snapshot(
            {"clients": [{"id": "c1", "status": "suspended"}]},
            observed_at="2026-08-14T11:00:00Z",
            source_ref="test",
        )
        missing = compare_semantic_snapshots(None, current)
        self.assertEqual(missing["status"], "BLOCKED_MISSING_BASELINE")
        self.assertFalse(missing["comparable"])

        changed = compare_semantic_snapshots(base, current)
        self.assertEqual(changed["status"], "CHANGE_DETECTED")
        self.assertEqual(changed["changedSections"], ["clients"])
        self.assertTrue(changed["semanticChange"])
        self.assertFalse(changed["productionCertified"])

    def test_historical_trend_requires_two_comparable_snapshots(self) -> None:
        snapshot = make_semantic_snapshot(
            {"clients": [{"id": "c1"}]},
            observed_at="2026-08-14T11:00:00Z",
            source_ref="test",
        )
        trend = historical_trend([snapshot], "rows.clients")
        self.assertEqual(trend["status"], "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS")
        self.assertFalse(trend["productionCertified"])

    def test_freshness_without_governed_policy_fails_closed(self) -> None:
        result = assess_freshness(
            "2026-08-14T11:00:00Z",
            None,
            now="2026-08-14T11:05:00Z",
        )
        self.assertEqual(result["status"], "BLOCKED_FRESHNESS_POLICY_UNDEFINED")
        self.assertFalse(result["fresh"])

    def test_runtime_artifact_digest_mismatch_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "evidence.zip"
            with zipfile.ZipFile(artifact, "w") as bundle:
                bundle.writestr("REPORT.json", "{}")
            result = validate_runtime_artifact(artifact, expected_sha256="0" * 64)
        self.assertEqual(result["status"], "BLOCKED_ARTIFACT_DIGEST_MISMATCH")
        self.assertFalse(result["verified"])
        self.assertFalse(result["productionCertified"])

    def test_lineage_cross_scope_parent_is_not_resolved_green(self) -> None:
        payload = {
            "clients": [
                {
                    "entityId": "client-1",
                    "sourceDb": "local.db",
                    "sourceTable": "clients",
                    "fields": {"id": "client-1", "tenantId": "tenant-A"},
                }
            ],
            "devices": [
                {
                    "entityId": "device-1",
                    "sourceDb": "local.db",
                    "sourceTable": "devices",
                    "fields": {
                        "id": "device-1",
                        "clientId": "client-1",
                        "tenantId": "tenant-B",
                    },
                }
            ],
            "licenses": [],
            "sales": [],
        }
        graph = build_lineage_graph(payload)
        self.assertTrue(graph["crossScopeEdgeIds"])
        self.assertIn("cross_scope_conflicts", graph["blockers"])
        device = next(row for row in graph["orphans"] if row.get("entityId") == "device-1")
        self.assertEqual(device["status"], "ORPHAN_OR_SCOPE_BLOCKED")
        self.assertIn("CROSS_SCOPE_PARENT_CONFLICT", device["reasons"])
        self.assertFalse(graph["productionCertified"])

    def test_html_tabs_cannot_bypass_final_hardening(self) -> None:
        self.assertIs(html_tabs.run_operational_evidence, final_runner.run_operational_atlas)

    def test_integrated_runner_emits_foundations_but_keeps_certification_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "out"
            out.mkdir()

            base_manifest = {
                "tool": "code_atlas_operational_v3",
                "createdAt": "2026-08-14T11:00:00Z",
                "status": "SOURCE_READY_NOT_PRODUCTION_CERTIFIED",
                "featureCount": 50,
            }
            base_payload = {
                "manifest": dict(base_manifest),
                "clients": [],
                "licenses": [],
                "devices": [],
                "sales": [],
                "deviceClaimCrosscheck": [],
                "salesLineage": [],
                "tenantScopeResolver": {"status": "blocked-by-missing-scope-contract"},
                "schemaDriftGuard": [],
                "surfaceRoleMatrix": [],
                "runtimeEvidenceLinks": [{"status": "BLOCKED_NO_RESULT_ZIPS"}],
                "multiTenantLeakageGuard": [{"status": "blocked-by-missing-scope-contract"}],
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
                manifest = hardened_runner.run_operational_atlas(str(root), str(out), str(root))

            self.assertFalse(manifest["productionCertified"])
            self.assertEqual(manifest["hardeningCertifiableCount"], 0)
            self.assertEqual(
                manifest["foundationHardeningStatus"],
                "SOURCE_FOUNDATIONS_READY_WITH_BLOCKERS",
            )
            for name in (
                "FOUNDATION_HARDENING_SUMMARY.json",
                "EVIDENCE_RECORDS.json",
                "SEMANTIC_SNAPSHOT.json",
                "SNAPSHOT_DIFF_ENGINE.json",
                "HISTORICAL_TREND_MINI_ATLAS.json",
                "DATA_LINEAGE_GRAPH.json",
            ):
                self.assertTrue((out / name).exists(), name)

            diff = json.loads((out / "SNAPSHOT_DIFF_ENGINE.json").read_text(encoding="utf-8"))
            self.assertEqual(diff["status"], "BLOCKED_MISSING_BASELINE")

            trend = json.loads(
                (out / "HISTORICAL_TREND_MINI_ATLAS.json").read_text(encoding="utf-8")
            )
            self.assertTrue(trend)
            self.assertTrue(
                all(row["status"] == "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS" for row in trend)
            )

            ledger = json.loads(
                (out / "CAPABILITY_HARDENING_LEDGER.json").read_text(encoding="utf-8")
            )
            historical = next(
                row for row in ledger if row["capabilityId"] == "historical_trend_mini_atlas"
            )
            self.assertTrue(historical["runtimeOutputObserved"])
            self.assertEqual(historical["maturity"], "CONTRACT_BACKED")
            self.assertFalse(historical["certifiable"])
            self.assertIn(
                "foundation:historical_trend_insufficient_history",
                historical["hardBlockers"],
            )


if __name__ == "__main__":
    unittest.main()
