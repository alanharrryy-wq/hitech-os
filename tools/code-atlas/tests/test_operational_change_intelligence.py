from __future__ import annotations

import unittest

from code_atlas.change_intelligence import (
    build_authority_pack,
    build_connector_envelope,
    build_roi_event,
    derive_financial_estimate,
    normalize_agent_session,
    normalize_evidence_answer,
    validate_authority_pack,
    validate_connector_envelope,
    validate_policy_pack,
    verify_change,
)
from code_atlas.change_intelligence.contracts import CONNECTOR_SCHEMA, POLICY_SCHEMA, ContractError, sha256_json


class ChangeIntelligenceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pack = build_authority_pack(
            repository_identity="repo-123",
            commit_identity="abc123",
            tree_identity="tree123",
            request_digest="req123",
            normalized_task="Change authentication boundary",
            allowed_scope=["src/auth", "tests/auth"],
            protected_scope=["src/payments"],
            required_checks=["auth-tests"],
            required_evidence=["scope-proof"],
            forbidden_operations=["deploy"],
            stop_conditions=["authority drift"],
            tool_version="1.0.0",
            profile_version="generic-v1",
            authority_resolution={"missing": [], "conflicted": []},
            generated_at="2026-08-14T10:00:00Z",
        )

    def test_authority_pack_is_deterministically_checksummed(self) -> None:
        validated = validate_authority_pack(self.pack)
        self.assertEqual(validated["checksum"], self.pack["checksum"])
        self.assertFalse(validated["productionCertified"])

    def test_authority_pack_rejects_stale_checksum(self) -> None:
        mutated = dict(self.pack)
        mutated["normalizedTask"] = "different"
        with self.assertRaises(ContractError):
            validate_authority_pack(mutated)

    def test_authority_pack_rejects_missing_required_authority(self) -> None:
        with self.assertRaises(ContractError):
            build_authority_pack(
                repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
                normalized_task="task", allowed_scope=["src"], tool_version="1", profile_version="1",
                authority_resolution={"missing": ["SECURITY.md"], "conflicted": []},
            )

    def test_paths_with_spaces_unicode_and_long_names_are_valid(self) -> None:
        pack = build_authority_pack(
            repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
            normalized_task="task",
            allowed_scope=["src/área con espacios/" + "x" * 120],
            tool_version="1", profile_version="1",
        )
        self.assertIn("src/área con espacios/" + "x" * 120, pack["allowedScope"])

    def test_path_traversal_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            build_authority_pack(
                repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
                normalized_task="task", allowed_scope=["../outside"], tool_version="1", profile_version="1",
            )

    def test_verify_passes_only_complete_in_scope_change(self) -> None:
        report = verify_change(
            authority_pack=self.pack,
            change_manifest={"changedPaths": ["src/auth/login.py", "tests/auth/test_login.py"]},
            current_snapshot={"repositoryIdentity": "repo-123", "commitIdentity": "abc123", "treeIdentity": "tree123"},
            produced_evidence=[{"id": "auth-tests"}, {"id": "scope-proof"}],
        )
        self.assertEqual(report["decision"], "PASS")

    def test_verify_blocks_stale_snapshot(self) -> None:
        report = verify_change(
            authority_pack=self.pack,
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot={"repositoryIdentity": "repo-123", "commitIdentity": "new", "treeIdentity": "tree123"},
            produced_evidence=["auth-tests", "scope-proof"],
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertTrue(any(row["code"] == "STALE_SNAPSHOT" for row in report["findings"]))

    def test_verify_blocks_out_of_scope_change(self) -> None:
        report = verify_change(
            authority_pack=self.pack,
            change_manifest={"changedPaths": ["src/catalog/item.py"]},
            current_snapshot={"repositoryIdentity": "repo-123", "commitIdentity": "abc123", "treeIdentity": "tree123"},
            produced_evidence=["auth-tests", "scope-proof"],
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("src/catalog/item.py", report["outOfScopeMutations"])

    def test_verify_blocks_protected_mutation_even_if_scope_is_broadened(self) -> None:
        pack = build_authority_pack(
            repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
            normalized_task="task", allowed_scope=["src"], protected_scope=["src/payments"],
            tool_version="1", profile_version="1",
        )
        report = verify_change(
            authority_pack=pack,
            change_manifest={"changedPaths": ["src/payments/charge.py"]},
            current_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertIn("src/payments/charge.py", report["protectedBoundaryViolations"])

    def test_verify_blocks_missing_evidence(self) -> None:
        report = verify_change(
            authority_pack=self.pack,
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot={"repositoryIdentity": "repo-123", "commitIdentity": "abc123", "treeIdentity": "tree123"},
            produced_evidence=["auth-tests"],
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertEqual(report["missingEvidence"], ["scope-proof"])

    def test_verify_unknown_for_contradictory_evidence(self) -> None:
        report = verify_change(
            authority_pack=self.pack,
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot={"repositoryIdentity": "repo-123", "commitIdentity": "abc123", "treeIdentity": "tree123"},
            produced_evidence=["auth-tests", "scope-proof"],
            contradictions=["two ownership sources disagree"],
        )
        self.assertEqual(report["decision"], "UNKNOWN")

    def test_agent_session_pack_mismatch_blocks(self) -> None:
        report = verify_change(
            authority_pack=self.pack,
            change_manifest={"changedPaths": ["src/auth/login.py"]},
            current_snapshot={"repositoryIdentity": "repo-123", "commitIdentity": "abc123", "treeIdentity": "tree123"},
            produced_evidence=["auth-tests", "scope-proof"],
            agent_session={"packId": "other"},
        )
        self.assertEqual(report["decision"], "BLOCKED")

    def test_supported_qa_requires_real_evidence(self) -> None:
        with self.assertRaises(ContractError):
            normalize_evidence_answer({"claim": "team owns auth", "supportLevel": "SUPPORTED", "evidenceReferences": [], "retrievalOnly": True})

    def test_inferred_qa_requires_explicit_inference(self) -> None:
        with self.assertRaises(ContractError):
            normalize_evidence_answer({"claim": "possible owner", "supportLevel": "INFERRED", "evidenceReferences": []})

    def test_policy_is_expectation_not_evidence(self) -> None:
        policy = validate_policy_pack({
            "schemaVersion": POLICY_SCHEMA,
            "policyId": "policy-1",
            "version": "1",
            "protectedPaths": ["infra/prod"],
            "requiredAuthorities": ["SECURITY.md"],
        })
        self.assertFalse(policy["configurationIsEvidence"])

    def test_connector_rejects_cross_repository_contamination(self) -> None:
        env = build_connector_envelope(
            connector_type="junit", repository_identity="repo-a", commit_identity="c1",
            observed_at="2026-08-14T10:00:00Z", source_identity="ci/test", payload={"tests": 4},
        )
        with self.assertRaises(ContractError):
            validate_connector_envelope(env, expected_repository="repo-b")

    def test_connector_rejects_stale_commit(self) -> None:
        env = build_connector_envelope(
            connector_type="sarif", repository_identity="repo-a", commit_identity="c1",
            observed_at="2026-08-14T10:00:00Z", source_identity="scanner", payload={"runs": []},
        )
        with self.assertRaises(ContractError):
            validate_connector_envelope(env, expected_commit="c2")

    def test_connector_rejects_raw_secret_values(self) -> None:
        payload = {"token": "do-not-ingest-this"}
        env = {
            "schemaVersion": CONNECTOR_SCHEMA,
            "connectorType": "generic-command-evidence",
            "repositoryIdentity": "r",
            "commitIdentity": "c",
            "observedAt": "2026-08-14T10:00:00Z",
            "sourceIdentity": "cmd",
            "payload": payload,
            "payloadDigest": sha256_json(payload),
        }
        with self.assertRaises(ContractError):
            validate_connector_envelope(env)

    def test_roi_keeps_financial_value_derived(self) -> None:
        event = build_roi_event(metric="contextDiscoveryTime", value=2.5, unit="hours", repository_identity="r", source="timer")
        estimate = derive_financial_estimate([event], loaded_hourly_cost=100.0, assumption_label="customer-loaded-cost")
        self.assertEqual(estimate["estimatedValue"], 250.0)
        self.assertTrue(estimate["derived"])

    def test_agent_session_records_declared_data_only(self) -> None:
        session = normalize_agent_session({
            "sessionId": "s1", "packId": self.pack["packId"], "agentIdentity": "agent-x",
            "requestedTask": "task", "inspectedPaths": ["src/auth"], "changedPaths": ["src/auth/login.py"],
            "humanInterventions": 1,
        })
        self.assertFalse(session["hiddenReasoningInferred"])


if __name__ == "__main__":
    unittest.main()
