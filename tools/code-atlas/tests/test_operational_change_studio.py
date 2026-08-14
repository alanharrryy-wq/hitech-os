from __future__ import annotations

import unittest

from code_atlas.change_intelligence import (
    compose_change_model,
    normalize_architecture_delta,
    normalize_ci_result,
    parse_codeowners,
    parse_coverage_summary,
    parse_junit_xml,
    parse_sarif,
)
from code_atlas.change_intelligence.contracts import ContractError


class ChangeStudioContractTests(unittest.TestCase):
    def test_change_studio_requires_provenance(self) -> None:
        with self.assertRaises(ContractError):
            compose_change_model(
                normalized_intent="change auth",
                repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
                primary_targets=[{"path": "src/auth", "supportLevel": "SUPPORTED", "evidenceReferences": ["e1"]}],
                provenance=[],
            )

    def test_change_studio_blocks_missing_required_evidence(self) -> None:
        model = compose_change_model(
            normalized_intent="change auth",
            repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
            primary_targets=[{"path": "src/auth", "supportLevel": "SUPPORTED", "evidenceReferences": ["e1"]}],
            required_evidence=[{"id": "auth-tests", "status": "MISSING"}],
            provenance=[{"source": "graph", "digest": "d"}],
        )
        self.assertEqual(model["decision"], "BLOCKED")

    def test_change_studio_unknown_for_unsupported_primary_target(self) -> None:
        model = compose_change_model(
            normalized_intent="change auth",
            repository_snapshot={"repositoryIdentity": "r", "commitIdentity": "c", "treeIdentity": "t"},
            primary_targets=[{"path": "src/auth", "supportLevel": "UNKNOWN", "evidenceReferences": []}],
            provenance=[{"source": "graph"}],
        )
        self.assertEqual(model["decision"], "UNKNOWN")

    def test_architecture_delta_rejects_cross_repository_comparison(self) -> None:
        with self.assertRaises(ContractError):
            normalize_architecture_delta(
                base_snapshot={"repositoryIdentity": "a"},
                head_snapshot={"repositoryIdentity": "b"},
                categories={},
                provenance=[{"source": "x"}],
            )

    def test_architecture_delta_counts_material_changes(self) -> None:
        delta = normalize_architecture_delta(
            base_snapshot={"repositoryIdentity": "r", "commitIdentity": "a"},
            head_snapshot={"repositoryIdentity": "r", "commitIdentity": "b"},
            categories={
                "dependencyEdges": [{"status": "added", "edge": "a->b"}],
                "ciTestGates": [{"status": "unchanged"}],
            },
            provenance=[{"source": "snapshot-compare"}],
        )
        self.assertEqual(delta["materialChangeCount"], 1)

    def test_junit_parser(self) -> None:
        result = parse_junit_xml('<testsuite name="auth" tests="2" failures="0" errors="0" skipped="1"></testsuite>')
        self.assertEqual(result["tests"], 2)
        self.assertTrue(result["passed"])

    def test_junit_parser_rejects_malformed_xml(self) -> None:
        with self.assertRaises(ContractError):
            parse_junit_xml('<testsuite>')

    def test_sarif_parser_summarizes_levels(self) -> None:
        result = parse_sarif({"version": "2.1.0", "runs": [{"results": [{"level": "error", "ruleId": "R1"}]}]})
        self.assertEqual(result["levels"]["error"], 1)
        self.assertEqual(result["ruleIds"], ["R1"])

    def test_codeowners_parser_preserves_rules(self) -> None:
        result = parse_codeowners('# comment\n/src/auth/ @security @platform\n')
        self.assertEqual(result["ruleCount"], 1)
        self.assertEqual(result["rules"][0]["owners"], ["@security", "@platform"])

    def test_coverage_parser_requires_recognized_metrics(self) -> None:
        with self.assertRaises(ContractError):
            parse_coverage_summary({"total": {"unknown": {"pct": 90}}})

    def test_ci_parser_is_fail_closed(self) -> None:
        with self.assertRaises(ContractError):
            normalize_ci_result({"status": "completed", "conclusion": "maybe", "checks": []})


if __name__ == "__main__":
    unittest.main()
