
from __future__ import annotations

import unittest

from ark_contract_validator_bundle.runtime.rule_exclusions import evaluate


class ReportsRealExclusionTests(unittest.TestCase):
    def test_reports_real_write_is_blocking(self) -> None:
        case = {
            'case_id': 'reports_real_violation',
            'paths_examined': ['reports_real/registries/module_registry.json'],
            'excluded_paths_written': ['reports_real/validator_outputs/validation_report.json'],
        }
        findings = evaluate(case)
        severities = {item.severity for item in findings}
        self.assertIn('critical', severities)
