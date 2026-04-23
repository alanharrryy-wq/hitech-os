
from __future__ import annotations

import unittest

from checks.advisory_only_checks import AdvisoryBoundaryError, assert_forbidden_write_names, assert_no_promotion_language
from checks.authoritative_override_checks import OverrideError, assert_no_gate_override, assert_no_switch_override
from checks.path_exclusion_checks import PathPolicyError, assert_runtime_output_path, assert_safe_ignore
from core.case_loader import load_cases


class AdvisoryBoundaryTests(unittest.TestCase):
    def test_corpus_cases_do_not_target_authoritative_writes(self) -> None:
        cases = load_cases()
        for case in cases[:30]:
            joined = ' '.join(case['forbidden_actions'])
            with self.assertRaises(AdvisoryBoundaryError):
                assert_no_promotion_language(joined + ' promote canonicalize')

    def test_forbidden_writes_are_rejected(self) -> None:
        with self.assertRaises(AdvisoryBoundaryError):
            assert_forbidden_write_names(['module_registry.json'])

    def test_switch_and_gate_override_are_rejected(self) -> None:
        with self.assertRaises(OverrideError):
            assert_no_switch_override({'proposed_switch_value': True})
        with self.assertRaises(OverrideError):
            assert_no_gate_override({'proposed_gate': 'READY'})

    def test_reports_real_is_safe_ignore(self) -> None:
        assert_safe_ignore('reports_real/registries/module_registry.json')
        with self.assertRaises(PathPolicyError):
            assert_runtime_output_path('reports_real/annotations/annotations.json')


if __name__ == '__main__':
    unittest.main()
