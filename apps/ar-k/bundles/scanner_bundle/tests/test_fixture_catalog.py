from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from contracts_py.scanner_logic import scan_tree
from fixtures_py.catalog import get_case, selected_verification_cases

class FixtureCatalogTests(unittest.TestCase):
    def test_selected_cases_generate_required_outputs(self) -> None:
        for case in selected_verification_cases()[:2]:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / case.name
                case.write_tree(root)
                artifacts = scan_tree(root)
                self.assertIn('scan_observed_modules.json', artifacts)
                self.assertIn('scan_observed_boundaries.json', artifacts)
                self.assertIn('scan_observed_paths.json', artifacts)
                self.assertIn('scan_observed_summary.json', artifacts)

    def test_case_lookup_works(self) -> None:
        case = get_case('case_001_payments_console')
        self.assertEqual(case.name, 'case_001_payments_console')

if __name__ == '__main__':
    unittest.main()
