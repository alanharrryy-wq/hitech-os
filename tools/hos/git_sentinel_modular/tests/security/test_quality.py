from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.security.quality import SecurityQualityDataset, SecurityQualityEvaluator
from tools.hos.git_sentinel_modular.shared.contracts import SecurityFinding


class SecurityQualityEvaluatorTestCase(unittest.TestCase):
    def test_evaluate_perfect_match(self):
        findings = [
            SecurityFinding(
                rule_id="SEC_SECRET",
                path="src/config.env",
                severity="critical",
                message="Potential inline secret assignment",
                secret_like=True,
            ).validate()
        ]
        dataset = SecurityQualityDataset(
            expected_rule_ids={"SEC_SECRET"},
            expected_paths={"src/config.env"},
        )
        result = SecurityQualityEvaluator().evaluate(findings, dataset)
        self.assertEqual(result.precision, 1.0)
        self.assertEqual(result.recall, 1.0)

    def test_evaluate_with_unexpected(self):
        findings = [
            SecurityFinding(
                rule_id="SEC_TOKEN",
                path="src/config.env",
                severity="medium",
                message="Potential access token marker",
                secret_like=True,
            ).validate()
        ]
        dataset = SecurityQualityDataset(
            expected_rule_ids={"SEC_SECRET"},
            expected_paths={"src/config.env"},
        )
        result = SecurityQualityEvaluator().evaluate(findings, dataset)
        self.assertEqual(result.matched_findings, 0)
        self.assertGreaterEqual(result.unexpected_findings, 1)


if __name__ == "__main__":
    unittest.main()
