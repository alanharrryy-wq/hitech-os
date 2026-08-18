from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_atlas.change_intelligence import (
    build_customer_lifecycle_policy,
    build_hardened_portable_bundle_manifest,
    build_rental_runner_plan,
    cleanup_customer_workspace,
    create_customer_workspace,
    customer_workspace_expired,
    sanitize_artifact_bytes,
    sanitize_artifacts_for_egress,
    validate_runner_cleanup,
    validate_runner_egress,
)
from code_atlas.change_intelligence.contracts import ContractError
from code_atlas.intelligence.graphs import change_impact, dependency_graph


class RentalArtifactHygieneTests(unittest.TestCase):
    def test_json_artifact_is_content_sanitized_before_egress(self) -> None:
        raw = json.dumps(
            {
                "token": "ghp_abcdefghijklmnopqrstuvwxyz012345",
                "owner": "customer@example.com",
                "nested": {"client_secret": {"value": "not-exportable"}},
            }
        ).encode("utf-8")
        sanitized, attestation = sanitize_artifact_bytes(name="reports/result.json", kind="verification", content=raw)
        text = sanitized.decode("utf-8")
        self.assertNotIn("ghp_abcdefghijklmnopqrstuvwxyz012345", text)
        self.assertNotIn("customer@example.com", text)
        self.assertNotIn("not-exportable", text)
        self.assertIn("<REDACTED_SECRET>", text)
        self.assertIn("<REDACTED_EMAIL>", text)
        self.assertEqual(attestation["decision"], "PASS_SANITIZED")
        self.assertEqual(attestation["contentInspection"], "FULL_UTF8_TEXT")
        self.assertFalse(attestation["sourceCodeIncluded"])

    def test_source_code_and_unknown_binary_formats_fail_closed(self) -> None:
        with self.assertRaises(ContractError):
            sanitize_artifact_bytes(name="src/main.py", kind="report", content=b"print('hello')")
        with self.assertRaises(ContractError):
            sanitize_artifact_bytes(name="query.sqlite", kind="index", content=b"SQLite format 3\x00secret")

    def test_batch_failure_publishes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw"
            out = root / "out"
            raw.mkdir()
            (raw / "good.txt").write_text("email=a@example.com\n", encoding="utf-8")
            (raw / "bad.bin").write_bytes(b"\x00\x01\x02")
            with self.assertRaises(ContractError):
                sanitize_artifacts_for_egress(
                    artifacts=[
                        {"localPath": str(raw / "good.txt"), "name": "reports/good.txt", "kind": "report"},
                        {"localPath": str(raw / "bad.bin"), "name": "reports/bad.bin", "kind": "binary"},
                    ],
                    output_dir=out,
                )
            self.assertTrue(out.is_dir())
            self.assertEqual([path for path in out.rglob("*") if path.is_file()], [])

    def test_rental_v2_requires_sanitized_bundle_and_matching_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            source.write_text(json.dumps({"token": "github_pat_abcdefghijklmnopqrstuvwxyz0123456789"}), encoding="utf-8")
            prepared = sanitize_artifacts_for_egress(
                artifacts=[{"localPath": str(source), "name": "reports/result.json", "kind": "verification"}],
                output_dir=root / "egress",
            )
            plan = build_rental_runner_plan(repository_identity="customer/repo", requested_outputs=["verification"])
            policy = plan["dataLifecyclePolicy"]
            manifest = build_hardened_portable_bundle_manifest(
                repository_snapshot={"repositoryIdentity": "customer/repo", "commitIdentity": "abc", "treeIdentity": "tree"},
                artifacts=prepared["artifacts"],
                sanitization_attestations=prepared["sanitizationAttestations"],
                lifecycle_policy_digest=policy["policyDigest"],
                purpose="rental evidence",
            )
            result = validate_runner_egress(runner_plan=plan, bundle_manifest=manifest)
            self.assertTrue(result["allowed"])
            self.assertTrue(result["postEgressCleanupRequired"])
            self.assertTrue(manifest["artifactContentSanitizationProven"])

    def test_hardened_manifest_rejects_attestation_tampering(self) -> None:
        sanitized, attestation = sanitize_artifact_bytes(name="report.txt", kind="report", content=b"clean report")
        artifact = {"name": "report.txt", "kind": "report", "digest": attestation["sanitizedDigest"], "size": len(sanitized)}
        tampered = dict(attestation)
        tampered["sanitizedSize"] += 1
        with self.assertRaises(ContractError):
            build_hardened_portable_bundle_manifest(
                repository_snapshot={"repositoryIdentity": "customer/repo", "commitIdentity": "abc", "treeIdentity": "tree"},
                artifacts=[artifact],
                sanitization_attestations=[tampered],
                lifecycle_policy_digest=build_customer_lifecycle_policy(repository_identity="customer/repo")["policyDigest"],
                purpose="evidence",
            )


class RentalLifecycleTests(unittest.TestCase):
    def test_ephemeral_workspace_is_expired_and_cleanup_is_verifiable(self) -> None:
        policy = build_customer_lifecycle_policy(repository_identity="customer/repo")
        plan = build_rental_runner_plan(repository_identity="customer/repo", requested_outputs=["report"])
        with tempfile.TemporaryDirectory() as tmp:
            workspace = create_customer_workspace(
                base_root=tmp,
                lifecycle_policy=policy,
                session_id="session-001",
                created_at="2026-08-18T15:00:00Z",
            )
            root = Path(workspace["workspacePath"])
            (root / "private-source-copy.txt").write_text("temporary", encoding="utf-8")
            self.assertTrue(customer_workspace_expired(workspace, now="2026-08-18T15:00:00Z"))
            evidence = cleanup_customer_workspace(
                workspace=workspace,
                lifecycle_policy=policy,
                reason="egress-complete",
                completed_at="2026-08-18T15:00:01Z",
            )
            self.assertFalse(root.exists())
            validation = validate_runner_cleanup(runner_plan=plan, cleanup_evidence=evidence)
            self.assertTrue(validation["cleanupVerified"])
            self.assertEqual(validation["remainingPaths"], 0)
            self.assertFalse(validation["secureEraseGuaranteed"])

    def test_bounded_retention_is_capped(self) -> None:
        with self.assertRaises(ContractError):
            build_customer_lifecycle_policy(
                repository_identity="customer/repo",
                retention_mode="BOUNDED",
                retention_seconds=86_401,
            )


class BoundedGoJavaDependencyTests(unittest.TestCase):
    @staticmethod
    def _inventory(paths: list[str], tests: list[str] | None = None) -> dict:
        return {
            "files": [
                {"path": path, "isText": True, "sensitiveName": False}
                for path in paths
            ],
            "testFiles": tests or [],
        }

    def test_go_local_module_import_and_same_package_test_are_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "go.mod": "module example.com/acme\n\ngo 1.24\n",
                "core/core.go": "package core\n\nfunc Value() int { return 1 }\n",
                "core/core_test.go": "package core\n\nimport \"testing\"\n\nfunc TestValue(t *testing.T) { _ = Value() }\n",
                "consumer/consumer.go": "package consumer\n\nimport \"example.com/acme/core\"\n\nfunc Use() int { return core.Value() }\n",
            }
            for rel, text in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            inventory = self._inventory(list(files), ["core/core_test.go"])
            deps = dependency_graph(root, inventory)
            edges = {(row["from"], row["to"], row["type"]) for row in deps["edges"]}
            self.assertIn(("consumer/consumer.go", "core/core.go", "go-import"), edges)
            self.assertIn(("core/core_test.go", "core/core.go", "go-test-package"), edges)
            impact = change_impact(["core/core.go"], deps, {"edges": []})
            self.assertIn("consumer/consumer.go", impact["impacted"])
            self.assertIn("core/core_test.go", impact["impacted"])
            self.assertEqual(deps, dependency_graph(root, inventory))

    def test_go_external_import_is_not_invented(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "go.mod").write_text("module example.com/acme\n", encoding="utf-8")
            (root / "main.go").write_text("package main\nimport \"github.com/other/pkg\"\nfunc main() {}\n", encoding="utf-8")
            deps = dependency_graph(root, self._inventory(["go.mod", "main.go"]))
            self.assertFalse(any(row["type"] == "go-import" for row in deps["edges"]))

    def test_java_local_import_and_same_package_test_are_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {
                "src/main/java/com/acme/OwnerService.java": "package com.acme;\npublic class OwnerService {}\n",
                "src/main/java/com/acme/OwnerController.java": "package com.acme;\nimport com.acme.OwnerService;\npublic class OwnerController { OwnerService service; }\n",
                "src/test/java/com/acme/OwnerControllerTests.java": "package com.acme;\npublic class OwnerControllerTests { OwnerController subject; }\n",
                "src/test/java/com/acme/WildcardTests.java": "package com.acme.tests;\nimport com.acme.*;\npublic class WildcardTests {}\n",
            }
            for rel, text in files.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            inventory = self._inventory(list(files), [
                "src/test/java/com/acme/OwnerControllerTests.java",
                "src/test/java/com/acme/WildcardTests.java",
            ])
            deps = dependency_graph(root, inventory)
            edges = {(row["from"], row["to"], row["type"]) for row in deps["edges"]}
            self.assertIn((
                "src/main/java/com/acme/OwnerController.java",
                "src/main/java/com/acme/OwnerService.java",
                "java-import",
            ), edges)
            self.assertIn((
                "src/test/java/com/acme/OwnerControllerTests.java",
                "src/main/java/com/acme/OwnerController.java",
                "java-package-type",
            ), edges)
            self.assertTrue(any(
                row.get("reason") == "local-java-wildcard-import-not-expanded"
                for row in deps["unresolved"]
            ))
            impact = change_impact(["src/main/java/com/acme/OwnerController.java"], deps, {"edges": []})
            self.assertIn("src/test/java/com/acme/OwnerControllerTests.java", impact["impacted"])
            self.assertEqual(deps, dependency_graph(root, inventory))


if __name__ == "__main__":
    unittest.main()
