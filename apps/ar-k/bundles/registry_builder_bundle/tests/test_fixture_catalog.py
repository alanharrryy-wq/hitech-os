from __future__ import annotations

import sys
from pathlib import Path
import unittest

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

from fixtures.catalog import case_ids, load_all_cases


class FixtureCatalogTests(unittest.TestCase):
    def test_fixture_count_is_large_and_python_heavy(self) -> None:
        self.assertGreaterEqual(len(case_ids()), 240)
        cases = load_all_cases()
        self.assertEqual(len(cases), len(case_ids()))
        self.assertTrue(any(case['legacy_runtime_requests_query_index'] for case in cases))
        self.assertTrue(any('reports_real/' in path for case in cases for path in case['excluded_paths']))


if __name__ == '__main__':
    unittest.main()
