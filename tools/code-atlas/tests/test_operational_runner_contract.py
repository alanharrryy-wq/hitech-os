from __future__ import annotations

import unittest

from code_atlas.change_intelligence import (
    build_authority_pack,
    build_portable_bundle_manifest,
    build_runner_plan,
    validate_runner_egress,
    verify_change,
)
from code_atlas.change_intelligence.contracts import ContractError, sha256_json


class RunnerAndCompatibilityTests(unittest.TestCase):
    def test_authority_digest_drift_blocks_verification(self) -> None:
        old = sha256_json({"authority": 1})
        new = sha256_json({"authority": 2})
        pack = build_authority_pack(
            repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
            normalized_task="task", allowed_scope=["src"], tool_version="1", profile_version="1",
            authority_digest=old,
        )
        report = verify_change(
            authority_pack=pack,
            change_manifest={"changedPaths": ["src/a.py"]},
            current_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t", "authorityDigest": new},
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertTrue(any(row["code"] == "COMPATIBILITY_LOCK_MISMATCH" for row in report["findings"]))

    def test_profile_version_mismatch_blocks_when_current_version_is_supplied(self) -> None:
        pack = build_authority_pack(
            repository_identity="r", commit_identity="c", tree_identity="t", request_digest="d",
            normalized_task="task", allowed_scope=["src"], tool_version="1", profile_version="profile-a",
        )
        report = verify_change(
            authority_pack=pack,
            change_manifest={"changedPaths": ["src/a.py"]},
            current_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t", "profileVersion": "profile-b"},
        )
        self.assertEqual(report["decision"], "BLOCKED")

    def test_runner_rejects_mutation_permissions(self) -> None:
        with self.assertRaises(ContractError):
            build_runner_plan(
                repository_identity="r",
                mode="LOCAL_ONLY",
                requested_outputs=["report"],
                mutation_permissions={"git": True},
            )

    def test_local_only_runner_rejects_egress(self) -> None:
        plan = build_runner_plan(repository_identity="r", mode="LOCAL_ONLY", requested_outputs=["report"])
        bundle = build_portable_bundle_manifest(
            repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
            artifacts=[{"name": "report.json", "kind": "report", "digest": sha256_json({}), "size": 1}],
            purpose="evidence",
        )
        with self.assertRaises(ContractError):
            validate_runner_egress(runner_plan=plan, bundle_manifest=bundle)

    def test_portable_evidence_runner_allows_non_source_bundle(self) -> None:
        plan = build_runner_plan(repository_identity="r", mode="PORTABLE_EVIDENCE", requested_outputs=["report"])
        bundle = build_portable_bundle_manifest(
            repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
            artifacts=[{"name": "report.json", "kind": "report", "digest": sha256_json({}), "size": 1}],
            purpose="evidence",
        )
        result = validate_runner_egress(runner_plan=plan, bundle_manifest=bundle)
        self.assertTrue(result["allowed"])


if __name__ == "__main__":
    unittest.main()
