from __future__ import annotations

import hashlib
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
    assess_audit_completeness,
    assess_freshness,
    canonical_digest,
    parse_freshness_policies,
)
from code_atlas.operational.foundation_integration import apply_operational_foundations
from code_atlas.operational.lineage_foundation import build_lineage_graph
from code_atlas.operational.temporal_foundation import (
    build_timeline,
    compare_semantic_snapshots,
    discover_prior_snapshots,
    historical_trend,
    make_semantic_snapshot,
    resolve_repository_identity,
)


def _repo_identity(seed: str) -> str:
    return "repo-sha256:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _init_git_origin(root: Path, url: str = "https://github.com/prismahitech/hitech-os.git") -> None:
    (root / ".git").mkdir(parents=True, exist_ok=True)
    (root / ".git" / "config").write_text(
        f'[remote "origin"]\n\turl = {url}\n',
        encoding="utf-8",
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
        identity = _repo_identity("repo-A")
        base = make_semantic_snapshot(
            {"clients": [{"id": "c1", "status": "active"}]},
            observed_at="2026-08-14T10:00:00Z",
            source_ref="test",
            repository_identity=identity,
        )
        current = make_semantic_snapshot(
            {"clients": [{"id": "c1", "status": "suspended"}]},
            observed_at="2026-08-14T11:00:00Z",
            source_ref="test",
            repository_identity=identity,
        )
        missing = compare_semantic_snapshots(None, current)
        self.assertEqual(missing["status"], "BLOCKED_MISSING_BASELINE")
        self.assertFalse(missing["comparable"])

        changed = compare_semantic_snapshots(base, current)
        self.assertEqual(changed["status"], "CHANGE_DETECTED")
        self.assertEqual(changed["changedSections"], ["clients"])
        self.assertTrue(changed["semanticChange"])
        self.assertFalse(changed["productionCertified"])

    def test_cross_repository_snapshot_and_history_are_never_comparable(self) -> None:
        base = make_semantic_snapshot(
            {"clients": [{"id": "c1"}]},
            observed_at="2026-08-14T10:00:00Z",
            source_ref="test",
            repository_identity=_repo_identity("client-A"),
        )
        current = make_semantic_snapshot(
            {"clients": [{"id": "c1"}]},
            observed_at="2026-08-14T11:00:00Z",
            source_ref="test",
            repository_identity=_repo_identity("client-B"),
        )
        diff = compare_semantic_snapshots(base, current)
        self.assertEqual(diff["status"], "BLOCKED_CROSS_REPOSITORY_SNAPSHOT")
        self.assertFalse(diff["comparable"])
        trend = historical_trend([base, current], "rows.clients")
        self.assertEqual(trend["status"], "BLOCKED_CROSS_REPOSITORY_HISTORY")

    def test_snapshot_discovery_filters_foreign_repository_archives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wanted = _repo_identity("wanted")
            foreign = _repo_identity("foreign")
            for index, identity in enumerate((foreign, wanted)):
                snapshot = make_semantic_snapshot(
                    {"clients": [{"id": index}]},
                    observed_at=f"2026-08-14T1{index}:00:00Z",
                    source_ref="test",
                    repository_identity=identity,
                )
                with zipfile.ZipFile(root / f"atlas {index} result.zip", "w") as bundle:
                    bundle.writestr("SEMANTIC_SNAPSHOT.json", json.dumps(snapshot))
            found = discover_prior_snapshots(root, expected_repository_identity=wanted)
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["repositoryIdentity"], wanted)

    def test_historical_trend_requires_two_comparable_snapshots(self) -> None:
        snapshot = make_semantic_snapshot(
            {"clients": [{"id": "c1"}]},
            observed_at="2026-08-14T11:00:00Z",
            source_ref="test",
            repository_identity=_repo_identity("same"),
        )
        trend = historical_trend([snapshot], "rows.clients")
        self.assertEqual(trend["status"], "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS")
        self.assertFalse(trend["productionCertified"])

    def test_duplicate_timeline_evidence_is_blocking(self) -> None:
        row = {
            "recordId": "e1",
            "observedAt": "2026-08-14T11:00:00Z",
            "capabilityId": "client_followup_atlas",
            "sourceKind": "operational_row",
            "sourceRef": "clients:c1",
            "payloadDigest": "0" * 64,
            "scope": {},
        }
        timeline = build_timeline([row, dict(row)])
        self.assertEqual(timeline["status"], "BLOCKED_DUPLICATE_TIMELINE_EVIDENCE")
        self.assertEqual(timeline["duplicateEvidenceIds"], ["e1"])

    def test_blocked_timeline_propagates_to_capability_hard_blocker(self) -> None:
        reconciled = hardened_runner._reconcile_foundation_capabilities(
            [{
                "capabilityId": "operational_timeline",
                "maturity": "CONTRACT_BACKED",
                "hardBlockers": [],
                "certifiable": False,
                "productionCertified": False,
            }],
            {"operationalTimeline": [{"status": "BLOCKED_DUPLICATE_TIMELINE_EVIDENCE"}]},
            {"blockers": ["operational_timeline_integrity"]},
        )
        timeline = reconciled[0]
        self.assertIn("foundation:operational_timeline_integrity", timeline["hardBlockers"])
        self.assertFalse(timeline["certifiable"])

    def test_freshness_without_governed_policy_fails_closed(self) -> None:
        result = assess_freshness(
            "2026-08-14T11:00:00Z",
            None,
            now="2026-08-14T11:05:00Z",
        )
        self.assertEqual(result["status"], "BLOCKED_FRESHNESS_POLICY_UNDEFINED")
        self.assertFalse(result["fresh"])

    def test_serialized_json_freshness_policy_is_validated_and_promoted(self) -> None:
        policies, rows = parse_freshness_policies({
            "operational_row": {
                "schemaVersion": "code_atlas_freshness_policy.v1",
                "policyId": "row-v1",
                "ttlSeconds": 600,
                "maxFutureSkewSeconds": 30,
            }
        })
        self.assertIn("operational_row", policies)
        self.assertEqual(policies["operational_row"].ttl_seconds, 600)
        self.assertEqual(rows[0]["status"], "PASS_FRESHNESS_POLICY_VALID")
        self.assertEqual(len(rows[0]["policyDigest"]), 64)

        invalid, invalid_rows = parse_freshness_policies({
            "operational_row": {"policyId": "bad", "ttlSeconds": 0}
        })
        self.assertFalse(invalid)
        self.assertEqual(invalid_rows[0]["status"], "BLOCKED_INVALID_FRESHNESS_POLICY")

    def test_audit_completeness_is_scope_and_provenance_aware(self) -> None:
        required = ["license.revoke"]
        no_scope = assess_audit_completeness(required, [])
        self.assertEqual(no_scope["status"], "BLOCKED_AUDIT_SCOPE_CONTRACT_MISSING")

        wrong = assess_audit_completeness(
            required,
            [{"eventId": "e1", "action": "license.revoke", "scope": {"tenantId": "tenant-B"}}],
            required_scope={"tenantId": "tenant-A"},
        )
        self.assertEqual(wrong["status"], "BLOCKED_WRONG_SCOPE_AUDIT_EVENTS")

        no_identity = assess_audit_completeness(
            required,
            [{"action": "license.revoke", "scope": {"tenantId": "tenant-A"}}],
            required_scope={"tenantId": "tenant-A"},
        )
        self.assertEqual(no_identity["status"], "BLOCKED_AUDIT_EVENT_PROVENANCE_INVALID")

        good = assess_audit_completeness(
            required,
            [{"eventId": "e1", "action": "license.revoke", "scope": {"tenantId": "tenant-A"}}],
            required_scope={"tenantId": "tenant-A"},
        )
        self.assertEqual(good["status"], "PASS_AUDIT_COVERAGE")

        duplicate = assess_audit_completeness(
            required,
            [
                {"eventId": "e1", "action": "license.revoke", "scope": {"tenantId": "tenant-A"}},
                {"eventId": "e2", "action": "license.revoke", "scope": {"tenantId": "tenant-A"}},
            ],
            required_scope={"tenantId": "tenant-A"},
        )
        self.assertEqual(duplicate["status"], "BLOCKED_DUPLICATE_AUDIT_EVENTS")

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
            "clients": [{
                "entityId": "client-1",
                "sourceDb": "local.db",
                "sourceTable": "clients",
                "fields": {"id": "client-1", "tenantId": "tenant-A"},
            }],
            "devices": [{
                "entityId": "device-1",
                "sourceDb": "local.db",
                "sourceTable": "devices",
                "fields": {"id": "device-1", "clientId": "client-1", "tenantId": "tenant-B"},
            }],
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

    def test_unresolved_lineage_target_and_orphan_are_global_blockers(self) -> None:
        graph = build_lineage_graph({
            "clients": [],
            "devices": [{
                "entityId": "device-1",
                "fields": {"id": "device-1", "clientId": "missing-client", "businessId": "business-1"},
            }],
            "licenses": [],
            "sales": [],
        })
        self.assertTrue(graph["unresolvedEdgeIds"])
        self.assertIn("unresolved_targets", graph["blockers"])
        self.assertIn("orphan_or_scope_blocked", graph["blockers"])
        self.assertEqual(graph["status"], "GRAPH_CONTRACT_BACKED_WITH_BLOCKERS")

    def test_repository_identity_is_hashed_and_missing_observed_at_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_origin(root, "https://user:secret@example.com/client/private-repo.git")
            identity = resolve_repository_identity(root)
            self.assertEqual(identity["status"], "PASS_REPOSITORY_IDENTITY_RESOLVED")
            self.assertTrue(identity["repositoryIdentity"].startswith("repo-sha256:"))
            self.assertNotIn("private-repo", json.dumps(identity))

            result = apply_operational_foundations(
                {"clients": [], "licenses": [], "devices": [], "sales": []},
                {"tool": "code_atlas_operational_v3"},
                repo_root=root,
                result_root=root,
            )
            self.assertEqual(result["currentSnapshot"]["status"], "BLOCKED_MISSING_OBSERVED_AT")
            self.assertIn("evidence_observed_at_missing_or_invalid", result["summary"]["blockers"])
            self.assertEqual(result["payload"]["evidenceRecords"], [])

    def test_html_tabs_cannot_bypass_final_hardening(self) -> None:
        self.assertIs(html_tabs.run_operational_evidence, final_runner.run_operational_atlas)

    def test_integrated_runner_emits_foundations_but_keeps_certification_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_origin(root)
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
                (destination / "ATLAS_MANIFEST_PLUS.json").write_text(json.dumps(base_manifest), encoding="utf-8")
                (destination / "operational_evidence_atlas.json").write_text(json.dumps(base_payload), encoding="utf-8")
                (destination / "SMOKE.json").write_text(json.dumps({"status": "PASS", "requiredFiles": []}), encoding="utf-8")
                for name in ("WHY_THIS_IS_RED.md", "HUMAN_OPERATOR_SUMMARY.md", "CONTINUATION_SUPREME.md", "CAN_PATCH_DECISION.md"):
                    (destination / name).write_text(name, encoding="utf-8")
                return dict(base_manifest)

            with mock.patch.object(hardened_runner, "_run_base_operational_atlas", fake_base):
                manifest = hardened_runner.run_operational_atlas(str(root), str(out), str(root))

            self.assertFalse(manifest["productionCertified"])
            self.assertEqual(manifest["hardeningCertifiableCount"], 0)
            self.assertEqual(manifest["foundationHardeningStatus"], "SOURCE_FOUNDATIONS_READY_WITH_BLOCKERS")
            for name in (
                "FOUNDATION_HARDENING_SUMMARY.json",
                "REPOSITORY_IDENTITY.json",
                "EVIDENCE_RECORDS.json",
                "SEMANTIC_SNAPSHOT.json",
                "SNAPSHOT_DIFF_ENGINE.json",
                "HISTORICAL_TREND_MINI_ATLAS.json",
                "OPERATIONAL_TIMELINE.json",
                "DATA_LINEAGE_GRAPH.json",
                "FRESHNESS_POLICY_VALIDATION.json",
                "AUDIT_COMPLETENESS_MATRIX.json",
            ):
                self.assertTrue((out / name).exists(), name)

            diff = json.loads((out / "SNAPSHOT_DIFF_ENGINE.json").read_text(encoding="utf-8"))
            self.assertEqual(diff["status"], "BLOCKED_MISSING_BASELINE")

            trend = json.loads((out / "HISTORICAL_TREND_MINI_ATLAS.json").read_text(encoding="utf-8"))
            self.assertTrue(trend)
            self.assertTrue(all(row["status"] == "BLOCKED_INSUFFICIENT_COMPARABLE_RUNS" for row in trend))

            ledger = json.loads((out / "CAPABILITY_HARDENING_LEDGER.json").read_text(encoding="utf-8"))
            historical = next(row for row in ledger if row["capabilityId"] == "historical_trend_mini_atlas")
            self.assertTrue(historical["runtimeOutputObserved"])
            self.assertEqual(historical["maturity"], "CONTRACT_BACKED")
            self.assertFalse(historical["certifiable"])
            self.assertIn("foundation:historical_trend_insufficient_history", historical["hardBlockers"])


if __name__ == "__main__":
    unittest.main()
