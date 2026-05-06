
from __future__ import annotations

import unittest

from ark_contract_validator_bundle.fixtures.case_index import load_all_cases
from ark_contract_validator_bundle.runtime.evaluator import evaluate_case


class EvaluatorSmokeTests(unittest.TestCase):
    def test_first_case_evaluates(self) -> None:
        case = load_all_cases()[0]
        result = evaluate_case(case)
        self.assertIn('summary', result)
        self.assertIn('gates', result)
        self.assertGreater(len(result['findings']), 0)
