from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import unittest

from fixtures.catalog import load_all_cases
from policy.promotion_policy import observed_only, scanner_may_write, registry_builder_may_write, build_canonical_outputs


class PromotionPolicyTests(unittest.TestCase):
    def test_scanner_signals_are_observed_only(self) -> None:
        for case in load_all_cases()[:15]:
            for signal in case['observed_signals']:
                self.assertTrue(observed_only(signal) or signal['signal_type'] in {'import_edge', 'boundary_candidate'})

    def test_write_ownership_is_singular(self) -> None:
        self.assertTrue(scanner_may_write('signals'))
        self.assertFalse(scanner_may_write('module_registry'))
        self.assertTrue(registry_builder_may_write('module_registry'))
        self.assertTrue(registry_builder_may_write('registry_index'))
        self.assertFalse(registry_builder_may_write('switch_decision_registry'))
        self.assertFalse(registry_builder_may_write('validation_report'))

    def test_conflicts_yield_superseded_entries(self) -> None:
        conflict_case = next(case for case in load_all_cases() if case['category'] == 'conflict_python_service')
        outputs = build_canonical_outputs(conflict_case['observed_signals'], execution_id=conflict_case['scenario_id'])
        statuses = {entry['status'] for entry in outputs['module_registry']}
        self.assertIn('superseded', statuses)
        self.assertIn('canonical', statuses)


if __name__ == '__main__':
    unittest.main()
