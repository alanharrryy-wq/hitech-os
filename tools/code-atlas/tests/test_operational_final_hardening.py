from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from code_atlas.operational import final_runner
from code_atlas.operational.final_runner import (
    build_client_setup_journey,
    build_investigator_index,
    compare_golden_path,
    entity_detail,
    harden_capability_ledger,
    query_atlas,
)
from code_atlas.operational.risk_scope_foundation import (
    REQUIRED_ISOLATION_TESTS,
    evaluate_client_risk,
    evaluate_tenant_isolation,
)


RISK_POLICY = {
    "maxAgeSeconds": 3600,
    "decayHalfLifeSeconds": 1800,
    "maxFutureSkewSeconds": 30,
    "thresholds": {"LOW": 0, "MEDIUM": 25, "HIGH": 50, "CRITICAL": 75},
}


def isolation_rows(level="source_test", status="PASS"):
    rows = []
    for index, test_id in enumerate(REQUIRED_ISOLATION_TESTS):
        rows.append({
            "testId": test_id,
            "status": status if index == 0 else "PASS",
            "assertion": "ACCESS_DENIED_OR_EMPTY",
            "evidenceLevel": level,
            "sourceRef": f"test:{test_id}",
            "sourceScope": {"tenantId": "tenant-A", "businessId": "biz-A"},
            "targetScope": {"tenantId": "tenant-B", "businessId": "biz-B"},
        })
    return rows


class FinalHardeningTests(unittest.TestCase):
    def test_risk_requires_policy_and_signals_and_is_deterministic(self):
        blocked = evaluate_client_risk([], None, now="2026-08-14T11:00:00Z")
        self.assertEqual(blocked["status"], "BLOCKED_MISSING_OR_INVALID_RISK_POLICY")
        self.assertIsNone(blocked["score"])

        signals = [{
            "signalId": "sig-1",
            "clientId": "client-1",
            "severity": "HIGH",
            "confidence": 0.8,
            "weight": 20,
            "observedAt": "2026-08-14T10:50:00Z",
            "sourceRef": "evidence:risk-1",
            "scope": {"tenantId": "tenant-A", "businessId": "biz-A"},
        }]
        left = evaluate_client_risk(signals, RISK_POLICY, now="2026-08-14T11:00:00Z")
        right = evaluate_client_risk(signals, RISK_POLICY, now="2026-08-14T11:00:00Z")
        self.assertEqual(left, right)
        self.assertEqual(left["status"], "RISK_SCORE_CONTRACT_BACKED")
        self.assertIsNotNone(left["score"])
        self.assertFalse(left["productionCertified"])

    def test_risk_stale_signal_blocks_score(self):
        result = evaluate_client_risk([{
            "signalId": "sig-stale", "clientId": "client-1", "severity": "LOW",
            "confidence": 1, "weight": 1, "observedAt": "2026-08-14T08:00:00Z",
            "sourceRef": "evidence:old",
        }], RISK_POLICY, now="2026-08-14T11:00:00Z")
        self.assertEqual(result["status"], "BLOCKED_RISK_SIGNAL_CONTRACT")
        self.assertIsNone(result["score"])
        self.assertTrue(any("signal_stale" in item for item in result["blockers"]))

    def test_isolation_requires_all_cases_and_scope_authority(self):
        missing = evaluate_tenant_isolation({"status": "PASS_SCOPE_AUTHORITY_FOUND"}, [])
        self.assertEqual(missing["status"], "BLOCKED_NEGATIVE_ISOLATION_TESTS_REQUIRED")

        no_authority = evaluate_tenant_isolation({"status": "blocked"}, isolation_rows())
        self.assertEqual(no_authority["status"], "BLOCKED_SCOPE_AUTHORITY_REQUIRED")
        self.assertTrue(no_authority["negativeTestsPassed"])
        self.assertFalse(no_authority["productionCertified"])

        source = evaluate_tenant_isolation({"status": "PASS_SCOPE_AUTHORITY_FOUND"}, isolation_rows())
        self.assertEqual(source["status"], "NEGATIVE_ISOLATION_CONTRACT_SOURCE_TESTED")
        self.assertTrue(source["negativeTestsPassed"])
        self.assertFalse(source["runtimeBacked"])
        self.assertFalse(source["productionCertified"])

        runtime = evaluate_tenant_isolation({"status": "PASS_SCOPE_AUTHORITY_FOUND"}, isolation_rows("runtime"))
        self.assertTrue(runtime["runtimeBacked"])
        self.assertFalse(runtime["productionCertified"])

    def test_isolation_failure_is_red(self):
        result = evaluate_tenant_isolation({"status": "PASS_SCOPE_AUTHORITY_FOUND"}, isolation_rows(status="FAIL"))
        self.assertEqual(result["status"], "FAIL_CROSS_SCOPE_ISOLATION")
        self.assertFalse(result["negativeTestsPassed"])

    def test_query_and_entity_are_scope_aware_and_fail_closed(self):
        payload = {
            "clients": [{
                "entityId": "client-1",
                "fields": {"id": "client-1", "tenantId": "tenant-A", "businessId": "biz-A"},
                "sourceDb": "local.db",
            }],
            "licenses": [], "devices": [], "sales": [], "evidenceRecords": [], "lineageNodes": [],
        }
        index = build_investigator_index(payload)
        no_scope = query_atlas(index, {"section": "clients", "filters": []})
        self.assertEqual(no_scope["status"], "BLOCKED_QUERY_SCOPE_REQUIRED")

        invalid = query_atlas(index, {
            "section": "clients", "scope": {"tenantId": "tenant-A", "businessId": "biz-A"},
            "filters": [{"field": "data.password", "op": "eq", "value": "x"}],
        })
        self.assertEqual(invalid["status"], "BLOCKED_INVALID_QUERY_FILTER")

        cross = query_atlas(index, {
            "section": "clients", "scope": {"tenantId": "tenant-B", "businessId": "biz-B"}, "filters": [],
        })
        self.assertEqual(cross["status"], "BLOCKED_CROSS_SCOPE_QUERY")

        partial = query_atlas(index, {"section": "clients", "scope": {"tenantId": "tenant-A"}, "filters": []})
        self.assertEqual(partial["status"], "QUERY_CONTRACT_BACKED")
        self.assertEqual(partial["rowCount"], 1)

        detail_block = entity_detail(index, section="clients", entity_id="client-1")
        self.assertEqual(detail_block["status"], "BLOCKED_ENTITY_SCOPE_REQUIRED")
        detail = entity_detail(index, section="clients", entity_id="client-1", scope={"tenantId": "tenant-A", "businessId": "biz-A"})
        self.assertEqual(detail["status"], "ENTITY_DETAIL_CONTRACT_BACKED")

    def test_query_unrelated_partial_scope_is_blocked(self):
        payload = {"clients": [{"entityId": "c1", "fields": {"id": "c1", "businessId": "biz-A"}}]}
        index = build_investigator_index(payload)
        result = query_atlas(index, {"section": "clients", "scope": {"tenantId": "tenant-A"}, "filters": []})
        self.assertEqual(result["status"], "BLOCKED_UNPROVEN_QUERY_SCOPE")

    def test_journey_and_golden_path_contracts_fail_closed(self):
        journey = build_client_setup_journey({
            "clients": [{"entityId": "c1", "fields": {"id": "c1", "tenantId": "t1"}}],
            "licenses": [{"entityId": "l1", "fields": {"id": "l1", "clientId": "c1", "tenantId": "t2"}}],
            "devices": [{"entityId": "d1", "fields": {"id": "d1", "clientId": "c1", "tenantId": "t1"}}],
        })
        self.assertEqual(journey[0]["status"], "BLOCKED_CLIENT_SETUP_JOURNEY")
        self.assertIn("cross_scope_license", journey[0]["blockers"])

        missing = compare_golden_path(None, [])
        self.assertEqual(missing["status"], "BLOCKED_GOLDEN_PATH_POLICY_MISSING")
        good = compare_golden_path(
            {"steps": ["setup", "sale", "sync"]},
            [
                {"stepId": "setup", "status": "PASS", "evidenceRef": "e1"},
                {"stepId": "sale", "status": "PASS", "evidenceRef": "e2"},
                {"stepId": "sync", "status": "PASS", "evidenceRef": "e3"},
            ],
        )
        self.assertEqual(good["status"], "GOLDEN_PATH_CONTRACT_BACKED")
        self.assertFalse(good["productionCertified"])

    def test_closure_requires_and_hardens_exactly_fifty(self):
        rows = [{
            "capabilityId": f"cap_{i}", "maturity": "HEURISTIC", "requiredContracts": [],
            "requiredNegativeTests": [], "doesNotProve": ["production"], "hardBlockers": [],
            "certifiable": False, "productionCertified": False,
        } for i in range(50)]
        ledger, summary = harden_capability_ledger(rows, {})
        self.assertEqual(len(ledger), 50)
        self.assertEqual(summary["sourceHardeningCompleteCount"], 50)
        self.assertTrue(summary["sourceHardeningComplete"])
        self.assertEqual(summary["productionCertifiedCount"], 0)
        self.assertTrue(all(row["sourceOwner"] for row in ledger))
        self.assertTrue(all(row["requiredContracts"] for row in ledger))
        self.assertTrue(all(row["requiredNegativeTests"] for row in ledger))
        self.assertTrue(all(row["certifiable"] is False for row in ledger))

    def test_final_runner_emits_closure_without_fake_production_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "out"
            out.mkdir()
            base_manifest = {
                "tool": "code_atlas_operational_v3",
                "createdAt": "2026-08-14T11:00:00Z",
                "productionCertified": False,
            }
            ledger = [{
                "capabilityId": f"cap_{i}", "maturity": "HEURISTIC", "requiredContracts": [],
                "requiredNegativeTests": [], "doesNotProve": ["production"], "hardBlockers": [],
                "certifiable": False, "productionCertified": False,
            } for i in range(50)]
            payload = {
                "manifest": dict(base_manifest), "clients": [], "licenses": [], "devices": [], "sales": [],
                "evidenceRecords": [], "lineageNodes": [], "capabilityHardeningLedger": ledger,
                "tenantScopeResolver": {"status": "blocked-by-missing-scope-contract"},
            }

            def fake_hardened(repo_root, output_dir, result_root=None):
                destination = Path(output_dir)
                (destination / "operational_evidence_atlas.json").write_text(json.dumps(payload), encoding="utf-8")
                (destination / "ATLAS_MANIFEST_PLUS.json").write_text(json.dumps(base_manifest), encoding="utf-8")
                (destination / "SMOKE.json").write_text(json.dumps({"requiredFiles": []}), encoding="utf-8")
                (destination / "operational_evidence_atlas.html").write_text('<body><input placeholder="Atlas Query Console"><h2>Entity Detail Drawer</h2></body>', encoding="utf-8")
                return dict(base_manifest)

            with mock.patch.object(final_runner, "_run_hardened_operational_atlas", fake_hardened):
                manifest = final_runner.run_operational_atlas(str(root), str(out), str(root))

            self.assertTrue(manifest["sourceHardeningComplete"])
            self.assertFalse(manifest["productionCertified"])
            self.assertEqual(manifest["hardeningCertifiableCount"], 0)
            for name in (
                "SOURCE_HARDENING_CLOSURE.json", "SOURCE_HARDENING_CLOSURE.md",
                "CLIENT_RISK_SCORE_CONTRACT.json", "TENANT_ISOLATION_EVALUATION.json",
                "ATLAS_QUERY_INDEX.json", "ENTITY_DETAIL_INDEX.json", "HARDENED_INVESTIGATOR.html",
            ):
                self.assertTrue((out / name).exists(), name)
            legacy = (out / "operational_evidence_atlas.html").read_text(encoding="utf-8")
            self.assertIn("Legacy payload text filter", legacy)
            self.assertIn("HARDENED_INVESTIGATOR.html", legacy)


if __name__ == "__main__":
    unittest.main()
