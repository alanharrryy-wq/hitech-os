from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from code_atlas.change_intelligence import prepare_change
from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context


class ImpactInspectionV2Tests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        proc = subprocess.run(
            ["git", *args], cwd=repo, check=True, text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return proc.stdout.strip()

    def _init(self, repo: Path) -> None:
        repo.mkdir(parents=True)
        self._git(repo, "init")
        self._git(repo, "config", "user.email", "blast@example.invalid")
        self._git(repo, "config", "user.name", "Impact Fixture")

    def _commit_all(self, repo: Path, message: str) -> None:
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-m", message)

    def _cpp_fixture(self, root: Path) -> Path:
        repo = root / "cpp fixture ü"
        self._init(repo)
        (repo / "include/lib/detail").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "include/lib/detail/function_ref.h").write_text("#pragma once\nstruct function_ref {};\n", encoding="utf-8")
        (repo / "include/lib/core.h").write_text('#pragma once\n#include "detail/function_ref.h"\n', encoding="utf-8")
        (repo / "include/lib/stl.h").write_text('#pragma once\n#include "core.h"\n', encoding="utf-8")
        (repo / "tests/test_copy_move.cpp").write_text('#include <lib/stl.h>\nint main(){return 0;}\n', encoding="utf-8")
        (repo / "tests/test_copy_move.py").write_text("def test_copy_move():\n    assert True\n", encoding="utf-8")
        (repo / "README.md").write_text("# fixture\n", encoding="utf-8")
        self._commit_all(repo, "baseline")
        return repo

    def test_cpp_include_chain_and_cross_language_test_companion_extend_inspection_not_legacy_radius(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._cpp_fixture(Path(td))
            context = resolve_intelligence_context(
                repo,
                request=IntelligenceRequest(changed_paths=("include/lib/detail/function_ref.h",), workers=4),
            )
            impact = context["graphs"]["changeImpact"]
            self.assertEqual(impact["impacted"], ["include/lib/detail/function_ref.h"])
            self.assertEqual(
                impact["inspectionPaths"],
                [
                    "include/lib/core.h",
                    "include/lib/detail/function_ref.h",
                    "include/lib/stl.h",
                    "tests/test_copy_move.cpp",
                    "tests/test_copy_move.py",
                ],
            )
            self.assertFalse(impact["impactRadiusIsAuthorization"])
            relation_types = {row["type"] for row in impact["inspectionV2"]["relations"]}
            self.assertIn("c-family-include", relation_types)
            self.assertIn("typed-test-companion", relation_types)
            why = {row["path"]: row for row in impact["whyIsThisInBlast"]}
            self.assertTrue(any(reason["kind"] == "typed-test-companion" for reason in why["tests/test_copy_move.py"]["reasons"]))
            self.assertTrue(all(row["authorizationGranted"] is False for row in why.values()))

    def test_same_input_is_deterministic_and_backslash_path_normalizes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._cpp_fixture(Path(td))
            request1 = IntelligenceRequest(changed_paths=(r"include\lib\detail\function_ref.h",), workers=2)
            request2 = IntelligenceRequest(changed_paths=("include/lib/detail/function_ref.h",), workers=4)
            first = resolve_intelligence_context(repo, request=request1)["graphs"]["changeImpact"]
            second = resolve_intelligence_context(repo, request=request2)["graphs"]["changeImpact"]
            self.assertEqual(first["blastDigest"], second["blastDigest"])
            self.assertEqual(first["inspectionPaths"], second["inspectionPaths"])
            self.assertEqual(first["whyIsThisInBlast"], second["whyIsThisInBlast"])

    def test_unsupported_language_is_explicit_unknown_not_green(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "unsupported"
            self._init(repo)
            (repo / "src").mkdir()
            (repo / "src/service.cs").write_text("public class Service {}\n", encoding="utf-8")
            self._commit_all(repo, "baseline")
            impact = resolve_intelligence_context(
                repo,
                request=IntelligenceRequest(changed_paths=("src/service.cs",), workers=2),
            )["graphs"]["changeImpact"]
            row = next(item for item in impact["unknownOrUnsupported"] if item.get("path") == "src/service.cs")
            self.assertEqual(row["supportLevel"], "UNKNOWN")
            self.assertEqual(row["disposition"], "UNSUPPORTED")
            self.assertIn("src/service.cs", impact["inspectionPaths"])

    def test_unresolved_local_include_never_invents_nonexistent_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "missing include"
            self._init(repo)
            (repo / "src").mkdir()
            (repo / "src/a.cpp").write_text('#include "does/not/exist.h"\nint a(){return 1;}\n', encoding="utf-8")
            self._commit_all(repo, "baseline")
            impact = resolve_intelligence_context(
                repo,
                request=IntelligenceRequest(changed_paths=("src/a.cpp",), workers=2),
            )["graphs"]["changeImpact"]
            self.assertNotIn("does/not/exist.h", impact["inspectionPaths"])
            self.assertTrue(any(
                row.get("specifier") == "does/not/exist.h" and row.get("supportLevel") == "UNKNOWN"
                for row in impact["unknownOrUnsupported"]
            ))

    def test_historical_cochange_and_ownership_are_inspect_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "history"
            self._init(repo)
            (repo / "src").mkdir()
            (repo / "src/target.py").write_text("VALUE = 0\n", encoding="utf-8")
            (repo / "src/peer.txt").write_text("peer 0\n", encoding="utf-8")
            (repo / "src/owner_peer.py").write_text("OWNER = 0\n", encoding="utf-8")
            (repo / "CODEOWNERS").write_text("/src/* @team\n", encoding="utf-8")
            self._commit_all(repo, "initial")
            for index in range(1, 4):
                (repo / "src/target.py").write_text(f"VALUE = {index}\n", encoding="utf-8")
                (repo / "src/peer.txt").write_text(f"peer {index}\n", encoding="utf-8")
                self._commit_all(repo, f"cochange {index}")

            impact = resolve_intelligence_context(
                repo,
                request=IntelligenceRequest(changed_paths=("src/target.py",), workers=2),
            )["graphs"]["changeImpact"]
            self.assertNotIn("src/peer.txt", impact["inspectionPaths"])
            self.assertIn("src/peer.txt", impact["inspectOnlyCandidates"])
            self.assertNotIn("src/owner_peer.py", impact["inspectionPaths"])
            self.assertIn("src/owner_peer.py", impact["inspectOnlyCandidates"])
            relation_by_type = {}
            for row in impact["inspectionV2"]["relations"]:
                relation_by_type.setdefault(row["type"], []).append(row)
            self.assertTrue(relation_by_type["historical-cochange"])
            self.assertTrue(relation_by_type["shared-codeowner"])
            self.assertTrue(all(row["disposition"] == "INSPECT_ONLY" for row in relation_by_type["historical-cochange"]))
            self.assertTrue(all(row["disposition"] == "INSPECT_ONLY" for row in relation_by_type["shared-codeowner"]))

    def test_non_unknown_relations_always_carry_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._cpp_fixture(Path(td))
            impact = resolve_intelligence_context(
                repo,
                request=IntelligenceRequest(changed_paths=("include/lib/detail/function_ref.h",), workers=2),
            )["graphs"]["changeImpact"]
            for row in impact["inspectionV2"]["relations"]:
                if row.get("supportLevel") != "UNKNOWN":
                    self.assertTrue(row.get("evidence"), row)

    def test_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._cpp_fixture(Path(td))
            with self.assertRaises(ValueError):
                resolve_intelligence_context(
                    repo,
                    request=IntelligenceRequest(changed_paths=("../outside.cpp",), workers=2),
                )

    def test_prepare_never_widens_authority_from_inspection_or_inspect_only_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._cpp_fixture(Path(td))
            prepared = prepare_change(
                repo,
                change_request="change function_ref and inspect bounded companions",
                target_paths=["include/lib/detail/function_ref.h"],
                policy={
                    "schemaVersion": "code_atlas_customer_policy.v1",
                    "policyId": "impact-v2-fixture",
                    "version": "1",
                    "protectedPaths": [],
                    "requiredAuthorities": [],
                    "requiredTests": [],
                    "requiredReviews": [],
                    "forbiddenOperations": [],
                    "domainEvidenceRequirements": [],
                    "impactThresholds": {},
                },
                workers=2,
            )
            self.assertEqual(prepared["decision"], "PASS")
            self.assertEqual(prepared["authorityPack"]["allowedScope"], ["include/lib/detail/function_ref.h"])
            impact = prepared["changeModel"]["impactRadius"]
            self.assertIn("tests/test_copy_move.py", impact["inspectionPaths"])
            self.assertNotIn("tests/test_copy_move.py", prepared["authorityPack"]["allowedScope"])


if __name__ == "__main__":
    unittest.main()
