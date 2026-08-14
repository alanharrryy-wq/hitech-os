from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from code_atlas.operational.assurance_foundation import (
    build_audit_completeness,
    validate_runtime_artifact,
)
from code_atlas.operational.evidence_foundation import (
    FreshnessPolicy,
    assess_freshness,
    canonical_digest,
    make_evidence_record,
)
from code_atlas.operational.foundation_integration import apply_operational_foundations
from code_atlas.operational.lineage_foundation import build_lineage_graph
from code_atlas.operational.temporal_foundation import (
    build_timeline,
    compare_semantic_snapshots,
    historical_trend,
    make_semantic_snapshot,
    validate_snapshot,
)


class OperationalFoundationTests(unittest.TestCase):
    def test_canonical_digest_is_order_stable_and_content_sensitive(self) -> None:
        left = {"b": 2, "a": {"y": 2, "x": 1}, "createdAt": "one"}
        right = {"createdAt": "two", "a": {"x": 1, "y": 2}, "b": 2}
        self.assertEqual(
            canonical_digest(left, drop_keys={"createdAt"}),
            canonical_digest(right, drop_keys={"createdAt"}),
        )
        changed = {"a": {"x": 9, "y": 2}, "b": 2, "createdAt": "two"}
        self.assertNotEqual(
            canonical_digest(left, drop_keys={"createdAt"}),
            canonical_digest(changed, drop_keys={"createdAt"}),
        )

    def test_evidence_record_identity_is_deterministic_and_nonclaims_required(self) -> None:
        kwargs = dict(
            capability_id="sales_lineage_matrix",
            source_kind="operational_row",
            source_ref="sales:s1",
            observed_at="2026-08-14T10:00:00Z",
            trust_level="SOURCE",
            payload={"id": "s1", "businessId": "b1"},
            scope={"businessId": "b1"},
            claims=("sanitized source row observed",),
            does_not_prove=("production correctness",),
        )
        first = make_evidence_record(**kwargs)
        second = make_evidence_record(**kwargs)
        self.assertEqual(first.record_id, second.record_id)
        self.assertEqual(first.payload_digest, second.payload_digest)
        self.assertFalse(first.as_dict()["productionCertified"])
        with self.assertRaises(ValueError):
            make_evidence_record(**{**kwargs, "does_not_prove": ()})

    def test_freshness_fails_closed_without_policy_and_on_future_or_stale_evidence(self) -> None:
        now = "2026-08-14T10:00:00Z"
        missing = assess_freshness("2026-08-14T09:59:30Z", None, now=now)
        self.assertEqual(missing["status"], "BLOCKED_FRESHNESS_POLICY_UNDEFINED")
        policy = FreshnessPolicy("operational-row-60s", ttl_seconds=60, max_future_skew_seconds=5)
        self.assertEqual(assess_freshness("2026-08-14T09:59:30Z", policy, now=now)["status"], "FRESH")
        self.assertEqual(assess_freshness("2026-08-14T09:58:00Z", policy, now=now)["status"], "STALE")
        self.assertEqual(assess_freshness("2026-08-14T10:01:00Z", policy, now=now)["status"], "BLOCKED_FUTURE_TIMESTAMP")

    def test_snapshot_diff_requires_baseline_and_detects_same_section_changed_content(self) -> None:
        base = make_semantic_snapshot(
            {"sales": [{"id": "s1", "total": 100}]},
            observed_at="2026-08-14T09:00:00Z",
            source_ref="operational",
        )
        current = make_semantic_snapshot(
            {"sales": [{"id": "s1", "total": 200}]},
            observed_at="2026-08-14T10:00:00Z",
            source_ref="operational",
        )
        self.assertEqual(compare_semantic_snapshots(None, current)["status"], "BLOCKED_MISSING_BASELINE")
        result = compare_semantic_snapshots(base, current)
        self.assertTrue(result["semanticChange"])
        self.assertEqual(result["changedSections"], ["sales"])
        tampered = dict(current)
        tampered["snapshotDigest"] = "0" * 64
        self.assertEqual(validate_snapshot(tampered)["status"], "BLOCKED_SNAPSHOT_DIGEST_MISMATCH")

    def test_historical_trend_needs_two_comparable_observations(self) -> None:
        first = make_semantic_snapshot(
            {"sales": [{"id": "s1"}]},
            observed_at="2026-08-14T09:00:00Z",
            source_ref="operational",
        )
        second = make_semantic_snapshot(
            {"sales": [{"id": "s1"}, {"id": "s2"}]},
            observed_at="2026-08-14T10:00:00Z",
            source_ref="operational",
        )
        one = historical_trend([first], "rows.sales")
        self.assertEqual(one["status"], "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS")
        two = historical_trend([first, second], "rows.sales")
        self.assertEqual(two["status"], "TREND_AVAILABLE")
        self.assertEqual(two["delta"], 1)
        self.assertFalse(two["productionCertified"])

    def test_timeline_rejects_invalid_identity_and_reports_duplicates(self) -> None:
        record = make_evidence_record(
            capability_id="client_followup_atlas",
            source_kind="operational_row",
            source_ref="clients:c1",
            observed_at="2026-08-14T10:00:00Z",
            trust_level="SOURCE",
            payload={"id": "c1"},
            does_not_prove=("completeness",),
        ).as_dict()
        timeline = build_timeline([record, record, {"observedAt": "2026-08-14T10:00:00Z"}])
        self.assertEqual(timeline["status"], "BLOCKED_INVALID_TIMELINE_EVIDENCE")
        self.assertEqual(timeline["duplicateEvidenceIds"], [record["recordId"]])
        self.assertIn("missing_record_id", timeline["invalidEvidence"])

    def test_lineage_uses_explicit_identity_fields_and_marks_cross_scope_conflicts(self) -> None:
        payload = {
            "clients": [
                {"entityId": "c1", "fields": {"id": "c1", "businessId": "b1"}},
            ],
            "devices": [
                {"entityId": "d1", "fields": {"id": "d1", "deviceId": "d1", "clientId": "c1", "businessId": "b2"}},
                {"entityId": "d2", "fields": {"id": "d2", "businessName": "client c1", "businessId": "b1"}},
            ],
            "sales": [
                {"entityId": "s1", "fields": {"id": "s1", "originDeviceId": "d1", "businessId": "b1"}},
                {"entityId": "s2", "fields": {"id": "s2", "businessId": "b1"}},
            ],
            "licenses": [],
        }
        graph = build_lineage_graph(payload)
        statuses = {(edge["from"], edge["to"]): edge["status"] for edge in graph["edges"]}
        self.assertEqual(statuses[("device:d1", "client:c1")], "CROSS_SCOPE_CONFLICT")
        self.assertEqual(statuses[("sale:s1", "device:d1")], "CROSS_SCOPE_CONFLICT")
        self.assertFalse(any(edge["from"] == "device:d2" and edge["to"] == "client:c1" for edge in graph["edges"]))
        sale2 = next(row for row in graph["orphans"] if row.get("entityId") == "s2")
        self.assertIn("MISSING_ORIGIN_DEVICE", sale2["reasons"])
        self.assertIn("cross_scope_conflicts", graph["blockers"])
        self.assertFalse(graph["productionCertified"])

    def test_runtime_artifact_integrity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / "result.zip"
            with zipfile.ZipFile(good, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                bundle.writestr("MANIFEST.json", "{}")
                bundle.writestr("reports/SMOKE.json", "{}")
            verified = validate_runtime_artifact(good, required_entries=("MANIFEST.json",))
            self.assertEqual(verified["status"], "SOURCE_BACKED_ARTIFACT_VERIFIED")
            self.assertTrue(verified["verified"])
            mismatch = validate_runtime_artifact(good, expected_sha256="0" * 64)
            self.assertEqual(mismatch["status"], "BLOCKED_ARTIFACT_DIGEST_MISMATCH")
            missing = validate_runtime_artifact(good, required_entries=("MISSING.json",))
            self.assertEqual(missing["status"], "BLOCKED_REQUIRED_EVIDENCE_ENTRY_MISSING")
            corrupt = root / "corrupt.zip"
            corrupt.write_bytes(b"not-a-zip")
            self.assertEqual(validate_runtime_artifact(corrupt)["status"], "BLOCKED_CORRUPT_ARTIFACT")

    def test_audit_completeness_requires_authoritative_action_catalog(self) -> None:
        missing_catalog = build_audit_completeness(None, [{"action": "sale.create"}])[0]
        self.assertEqual(missing_catalog["status"], "BLOCKED_AUDIT_ACTION_CATALOG_MISSING")
        missing_event = build_audit_completeness(
            ["sale.create", "sale.refund"],
            [{"action": "sale.create"}],
        )[0]
        self.assertEqual(missing_event["status"], "BLOCKED_MISSING_AUDIT_EVENTS")
        self.assertEqual(missing_event["missingActions"], ["sale.refund"])

    def test_foundation_integration_exposes_dedicated_outputs_without_fake_green(self) -> None:
        payload = {
            "clients": [{"entityId": "c1", "fields": {"id": "c1", "businessId": "b1"}}],
            "licenses": [],
            "devices": [{"entityId": "d1", "fields": {"id": "d1", "deviceId": "d1", "clientId": "c1", "businessId": "b1"}}],
            "sales": [{"entityId": "s1", "fields": {"id": "s1", "originDeviceId": "d1", "businessId": "b1"}}],
            "deviceClaimCrosscheck": [{"deviceId": "d1", "status": "PASS"}],
            "salesLineage": [{"saleId": "s1", "status": "PASS_EXPLICIT_PROVENANCE"}],
            "tenantScopeResolver": {"status": "PASS_SCOPE_AUTHORITY_FOUND"},
            "schemaDriftGuard": [],
            "surfaceRoleMatrix": [],
            "runtimeEvidenceLinks": [],
        }
        result = apply_operational_foundations(
            payload,
            {"tool": "operational-test", "createdAt": "2026-08-14T10:00:00Z"},
            result_root=None,
        )
        hardened = result["payload"]
        self.assertIn("historicalTrendMiniAtlas", hardened)
        self.assertEqual(hardened["snapshotDiffEngine"][0]["status"], "BLOCKED_MISSING_BASELINE")
        self.assertTrue(all(row["status"] == "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS" for row in hardened["historicalTrendMiniAtlas"]))
        self.assertTrue(all(row["status"] == "BLOCKED_FRESHNESS_POLICY_UNDEFINED" for row in hardened["stalenessMonitor"]))
        self.assertEqual(hardened["auditCompleteness"][0]["status"], "BLOCKED_AUDIT_ACTION_CATALOG_MISSING")
        self.assertFalse(result["summary"]["productionCertified"])
        self.assertIn("snapshot_baseline_missing", result["summary"]["blockers"])
        self.assertIn("freshness_policy_or_evidence_missing", result["summary"]["blockers"])
        self.assertIn("audit_catalog_or_events_incomplete", result["summary"]["blockers"])
        for name in (
            "EVIDENCE_RECORDS.json",
            "SEMANTIC_SNAPSHOT.json",
            "HISTORICAL_TREND_MINI_ATLAS.json",
            "DATA_LINEAGE_GRAPH.json",
            "FOUNDATION_HARDENING_SUMMARY.json",
        ):
            self.assertIn(name, result["outputs"])


if __name__ == "__main__":
    unittest.main()
