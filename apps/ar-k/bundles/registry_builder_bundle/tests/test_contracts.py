from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import unittest

from contracts.module_registry_contract import validate_document as validate_modules
from contracts.boundary_registry_contract import validate_document as validate_boundaries
from contracts.registry_index_contract import validate_document as validate_index
from fixtures.catalog import load_all_cases
from policy.promotion_policy import build_canonical_outputs


class ContractTests(unittest.TestCase):
    def test_generated_outputs_satisfy_contracts(self) -> None:
        for case in load_all_cases()[:20]:
            outputs = build_canonical_outputs(case['observed_signals'], execution_id=case['scenario_id'])
            self.assertEqual(validate_modules(outputs['module_registry']), [])
            self.assertEqual(validate_boundaries(outputs['boundary_registry']), [])
            self.assertEqual(validate_index(outputs['registry_index']), [])


if __name__ == '__main__':
    unittest.main()
