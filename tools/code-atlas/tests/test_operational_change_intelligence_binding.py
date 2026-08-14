from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from code_atlas.change_intelligence import prepare_change, verify_prepared_change
from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context


class UniversalCustomerWowBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="code-atlas-customer-wow-")
        self.repo = Path(self.tmp.name) / "neutral-repo"
        self.repo.mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "tests").mkdir()
        (self.repo / "src" / "__init__.py").write_text("", encoding="utf-8")
        (self.repo / "src" / "auth.py").write_text(
            "def authenticate(user):\n    return bool(user)\n",
            encoding="utf-8",
        )
        (self.repo / "src" / "consumer.py").write_text(
            "from src.auth import authenticate\n\ndef checkout(user):\n    return authenticate(user)\n",
            encoding="utf-8",
        )
        (self.repo / "src" / "payments.py").write_text(
            "def charge(amount):\n    return amount > 0\n",
            encoding="utf-8",
        )
        (self.repo / "tests" / "test_auth.py").write_text(
            "from src.auth import authenticate\n\ndef test_auth():\n    assert authenticate('u')\n",
            encoding="utf-8",
        )
        (self.repo / "CODEOWNERS").write_text("/src/* @security-team\n", encoding="utf-8")
        self._git("init")
        self._git("config", "user.email", "code-atlas@example.invalid")
        self._git("config", "user.name", "Code Atlas Fixture")
        self._git("add", ".")
        self._git("commit", "-m", "fixture baseline")
        self.policy = {
            "schemaVersion": "code_atlas_customer_policy.v1",
            "policyId": "fixture-policy",
            "version": "1",
            "protectedPaths": ["src/payments.py"],
            "requiredAuthorities": ["CODEOWNERS"],
            "requiredTests": ["test:auth"],
            "requiredReviews": [],
            "forbiddenOperations": ["deploy"],
            "domainEvidenceRequirements": ["evidence:auth"],
            "impactThresholds": {},
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _git(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout.strip()

    def _prepare(self):
        return prepare_change(
            self.repo,
            change_request="harden authentication without changing payments",
            target_paths=["src/auth.py"],
            policy=self.policy,
            domain="security",
        )

    def test_structured_universal_context_is_public_and_non_authoritative_by_projection(self) -> None:
        context = resolve_intelligence_context(
            self.repo,
            request=IntelligenceRequest(
                intent="VERIFY",
                domain="security",
                required_authorities=("CODEOWNERS",),
                changed_paths=("src/auth.py",),
            ),
        )
        self.assertEqual(context["schemaVersion"], "code_atlas_intelligence_context.v1")
        self.assertTrue(context["readOnly"])
        self.assertFalse(context["derivedIndexAuthoritative"])
        self.assertFalse(context["semanticRetrievalIsProof"])
        self.assertIn("src/consumer.py", context["graphs"]["changeImpact"]["impacted"])

    def test_prepare_builds_pack_from_explicit_supported_target_only(self) -> None:
        prepared = self._prepare()
        self.assertEqual(prepared["decision"], "PASS")
        self.assertIsNotNone(prepared["authorityPack"])
        self.assertEqual(prepared["authorityPack"]["allowedScope"], ["src/auth.py"])
        self.assertIn("src/consumer.py", prepared["changeModel"]["impactRadius"]["impacted"])
        self.assertNotIn("src/consumer.py", prepared["authorityPack"]["allowedScope"])
        pending = {row["id"]: row["status"] for row in prepared["changeModel"]["requiredEvidence"]}
        self.assertEqual(pending["test:auth"], "PENDING")
        self.assertEqual(pending["evidence:auth"], "PENDING")

    def test_no_target_fails_closed_without_guessing(self) -> None:
        prepared = prepare_change(
            self.repo,
            change_request="harden authentication",
            target_paths=[],
            policy=self.policy,
            domain="security",
        )
        self.assertEqual(prepared["decision"], "UNKNOWN")
        self.assertIsNone(prepared["authorityPack"])
        self.assertIn("EXPLICIT_EVIDENCE_SUPPORTED_TARGET_REQUIRED", prepared["reasonCodes"])

    def test_verify_passes_for_in_scope_worktree_change_with_required_evidence(self) -> None:
        prepared = self._prepare()
        (self.repo / "src" / "auth.py").write_text(
            "def authenticate(user):\n    return isinstance(user, str) and bool(user.strip())\n",
            encoding="utf-8",
        )
        report = verify_prepared_change(
            prepared,
            self.repo,
            changed_paths=["src/auth.py"],
            produced_evidence=["test:auth", "evidence:auth"],
            policy=self.policy,
        )
        self.assertEqual(report["decision"], "PASS")
        self.assertEqual(report["outOfScopeMutations"], [])
        self.assertEqual(report["protectedBoundaryViolations"], [])

    def test_out_of_scope_and_protected_change_is_blocked(self) -> None:
        prepared = self._prepare()
        report = verify_prepared_change(
            prepared,
            self.repo,
            changed_paths=["src/payments.py"],
            produced_evidence=["test:auth", "evidence:auth"],
            policy=self.policy,
        )
        self.assertEqual(report["decision"], "BLOCKED")
        codes = {row["code"] for row in report["findings"]}
        self.assertIn("OUT_OF_SCOPE_CHANGE", codes)
        self.assertIn("PROTECTED_SCOPE_MUTATION", codes)

    def test_authority_drift_blocks_existing_pack(self) -> None:
        prepared = self._prepare()
        (self.repo / "CODEOWNERS").write_text("/src/* @different-team\n", encoding="utf-8")
        report = verify_prepared_change(
            prepared,
            self.repo,
            changed_paths=["src/auth.py"],
            produced_evidence=["test:auth", "evidence:auth"],
            policy=self.policy,
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertTrue(any(
            row.get("code") == "COMPATIBILITY_LOCK_MISMATCH" and row.get("field") == "authorityDigest"
            for row in report["findings"]
        ))

    def test_new_commit_expires_exact_pack(self) -> None:
        prepared = self._prepare()
        (self.repo / "src" / "auth.py").write_text(
            "def authenticate(user):\n    return user is not None\n",
            encoding="utf-8",
        )
        self._git("add", "src/auth.py")
        self._git("commit", "-m", "change auth")
        report = verify_prepared_change(
            prepared,
            self.repo,
            changed_paths=["src/auth.py"],
            produced_evidence=["test:auth", "evidence:auth"],
            policy=self.policy,
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertTrue(any(row.get("code") == "STALE_SNAPSHOT" for row in report["findings"]))

    def test_missing_required_authority_blocks_verification(self) -> None:
        prepared = self._prepare()
        (self.repo / "CODEOWNERS").unlink()
        self._git("add", "-u")
        self._git("commit", "-m", "remove authority")
        report = verify_prepared_change(
            prepared,
            self.repo,
            changed_paths=["src/auth.py"],
            produced_evidence=["test:auth", "evidence:auth"],
            policy=self.policy,
        )
        self.assertEqual(report["decision"], "BLOCKED")
        self.assertEqual(report["findings"][0]["code"], "REQUIRED_AUTHORITY_MISSING")


if __name__ == "__main__":
    unittest.main()
