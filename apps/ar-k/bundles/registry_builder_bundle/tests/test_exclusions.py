from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import unittest

from policy.exclusions import exclusion_examples, is_excluded


class ExclusionTests(unittest.TestCase):
    def test_reports_real_is_excluded(self) -> None:
        self.assertTrue(is_excluded('reports_real/registries/module_registry.json'))

    def test_examples_match_expectations(self) -> None:
        expected = exclusion_examples()
        self.assertTrue(expected['reports/output.json'])
        self.assertTrue(expected['reports_real/registries/module_registry.json'])
        self.assertFalse(expected['src/app/service.py'])


if __name__ == '__main__':
    unittest.main()
