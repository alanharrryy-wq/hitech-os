
from __future__ import annotations

import unittest

from core.case_loader import load_cases


class CaseInventoryTests(unittest.TestCase):
    def test_case_volume_and_family_coverage(self) -> None:
        cases = load_cases()
        families = {case['family'] for case in cases}
        self.assertGreaterEqual(len(cases), 180)
        self.assertEqual(families, {'advisory_cases', 'ambiguity_cases', 'forbidden_override_cases', 'safe_ignore_cases'})
        self.assertTrue(any('reports_real/' in ' '.join(case['path_examples']) for case in cases))


if __name__ == '__main__':
    unittest.main()
