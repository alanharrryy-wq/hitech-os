from __future__ import annotations

import copy
import json
import unittest

from code_atlas.change_intelligence import (
    build_customer_lifecycle_policy,
    build_hardened_portable_bundle_manifest,
    sanitize_artifact_bytes,
)
from code_atlas.change_intelligence.contracts import ContractError, sha256_json


class EvidenceBundleSemanticRoleTests(unittest.TestCase):
    @staticmethod
    def _fixture(*, decision: str = "UNKNOWN") -> dict:
        snapshot = {
            "repositoryIdentity": "customer/repo",
            "commitIdentity": "abc123",
            "treeIdentity": "tree456",
        }
        semantic_payload = {
            "decision": decision,
            "classification": "VERIFY / BOUNDED EVIDENCE",
            "gaps": ["MISSING_EXTERNAL_REPLICATION"],
            "unknowns": ["INDEPENDENT_AGENT_RESULT"],
            "replay": {"id": "replay-001"},
            "handoff": {"id": "handoff-001"},
        }
        content = json.dumps(semantic_payload, sort_keys=True).encode("utf-8")
        sanitized, attestation = sanitize_artifact_bytes(
            name="reports/semantic-evidence.json",
            kind="verification",
            content=content,
        )
        artifact = {
            "name": "reports/semantic-evidence.json",
            "kind": "verification",
            "digest": attestation["sanitizedDigest"],
            "size": len(sanitized),
        }
        snapshot_digest = sha256_json(snapshot)
        roles = [
            {
                "role": "decision_classification",
                "artifactName": artifact["name"],
                "snapshotDigest": snapshot_digest,
                "decision": decision,
                "classification": "VERIFY / BOUNDED EVIDENCE",
            },
            {
                "role": "gaps_unknowns",
                "artifactName": artifact["name"],
                "snapshotDigest": snapshot_digest,
                "decision": decision,
                "gaps": ["MISSING_EXTERNAL_REPLICATION"],
                "unknowns": ["INDEPENDENT_AGENT_RESULT"],
            },
            {
                "role": "replay_handoff",
                "artifactName": artifact["name"],
                "snapshotDigest": snapshot_digest,
                "decision": decision,
                "replayId": "replay-001",
                "handoffId": "handoff-001",
                "replayDigest": "sha256:" + "2" * 64,
                "handoffDigest": "sha256:" + "3" * 64,
            },
        ]
        return {
            "snapshot": snapshot,
            "artifact": artifact,
            "attestation": attestation,
            "roles": roles,
            "lifecycleDigest": build_customer_lifecycle_policy(repository_identity="customer/repo")["policyDigest"],
        }

    @staticmethod
    def _build(fixture: dict, roles: list[dict] | None = None) -> dict:
        return build_hardened_portable_bundle_manifest(
            repository_snapshot=fixture["snapshot"],
            artifacts=[fixture["artifact"]],
            sanitization_attestations=[fixture["attestation"]],
            lifecycle_policy_digest=fixture["lifecycleDigest"],
            purpose="semantic evidence bundle",
            semantic_evidence_roles=fixture["roles"] if roles is None else roles,
        )

    def test_valid_semantic_roles_are_complete_canonical_and_replayable(self) -> None:
        fixture = self._fixture()
        manifest = self._build(fixture, list(reversed(fixture["roles"])))
        semantic = manifest["semanticEvidence"]

        self.assertEqual(
            [row["role"] for row in semantic["roles"]],
            ["decision_classification", "gaps_unknowns", "replay_handoff"],
        )
        self.assertTrue(semantic["semanticRoleCoverageComplete"])
        self.assertTrue(semantic["proofBearingSemanticPrerequisitesSatisfied"])
        self.assertFalse(semantic["decisionPromotionAllowedByPackaging"])
        self.assertEqual(semantic["roles"][2]["replayId"], "replay-001")
        self.assertEqual(semantic["roles"][2]["handoffId"], "handoff-001")
        self.assertEqual(semantic["roles"][1]["gaps"], ["MISSING_EXTERNAL_REPLICATION"])
        self.assertEqual(semantic["roles"][1]["unknowns"], ["INDEPENDENT_AGENT_RESULT"])
        self.assertFalse(manifest["sourceCodeIncluded"])
        self.assertTrue(manifest["artifactContentSanitizationProven"])

        repeated = self._build(fixture, fixture["roles"])
        self.assertEqual(manifest["semanticEvidence"], repeated["semanticEvidence"])

    def test_unknown_decision_is_preserved_and_never_promoted_by_packaging(self) -> None:
        manifest = self._build(self._fixture(decision="UNKNOWN"))
        semantic = manifest["semanticEvidence"]
        self.assertEqual(semantic["decision"], "UNKNOWN")
        self.assertTrue(semantic["roles"][1]["unknowns"])
        self.assertFalse(semantic["decisionPromotionAllowedByPackaging"])
        self.assertFalse(manifest["certifiable"])
        self.assertFalse(manifest["productionCertified"])

    def test_each_missing_required_semantic_role_fails_closed(self) -> None:
        fixture = self._fixture()
        for role in ("decision_classification", "gaps_unknowns", "replay_handoff"):
            with self.subTest(role=role):
                incomplete = [row for row in fixture["roles"] if row["role"] != role]
                with self.assertRaises(ContractError):
                    self._build(fixture, incomplete)

    def test_duplicate_or_contradictory_semantic_roles_fail_closed(self) -> None:
        fixture = self._fixture()
        duplicate = fixture["roles"] + [copy.deepcopy(fixture["roles"][0])]
        with self.assertRaises(ContractError):
            self._build(fixture, duplicate)

        contradictory = copy.deepcopy(fixture["roles"])
        contradictory[-1]["decision"] = "PASS"
        with self.assertRaises(ContractError):
            self._build(fixture, contradictory)

    def test_stale_semantic_snapshot_fails_closed(self) -> None:
        fixture = self._fixture()
        stale = copy.deepcopy(fixture["roles"])
        stale[1]["snapshotDigest"] = "sha256:" + "0" * 64
        with self.assertRaises(ContractError):
            self._build(fixture, stale)

    def test_tampered_artifact_descriptor_still_fails_before_semantic_acceptance(self) -> None:
        fixture = self._fixture()
        fixture["artifact"] = dict(fixture["artifact"])
        fixture["artifact"]["digest"] = "sha256:" + "f" * 64
        with self.assertRaises(ContractError):
            self._build(fixture)

    def test_legacy_hardened_v2_shape_remains_compatible_without_semantic_roles(self) -> None:
        fixture = self._fixture()
        manifest = build_hardened_portable_bundle_manifest(
            repository_snapshot=fixture["snapshot"],
            artifacts=[fixture["artifact"]],
            sanitization_attestations=[fixture["attestation"]],
            lifecycle_policy_digest=fixture["lifecycleDigest"],
            purpose="legacy hardened evidence",
        )
        self.assertNotIn("semanticEvidence", manifest)
        self.assertEqual(manifest["schemaVersion"], "code_atlas_portable_evidence_bundle.v2")


if __name__ == "__main__":
    unittest.main()
