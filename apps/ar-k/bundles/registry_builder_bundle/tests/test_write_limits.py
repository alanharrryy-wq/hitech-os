from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import unittest

from policy.write_limits import forbidden_outputs, may_write_path, normalized_allowed_outputs


class WriteLimitTests(unittest.TestCase):
    def test_forbidden_targets_remain_forbidden(self) -> None:
        forbidden = set(forbidden_outputs())
        self.assertIn('validation_report.json', forbidden)
        self.assertIn('annotations.json', forbidden)

    def test_allowed_paths_are_narrow(self) -> None:
        self.assertTrue(may_write_path('registries/module_registry.json'))
        self.assertTrue(may_write_path('indices/registry_index.json'))
        self.assertFalse(may_write_path('reports/validation_report.json'))
        self.assertFalse(may_write_path('annotations/annotations.json'))

    def test_allowed_outputs_include_portable_index(self) -> None:
        self.assertIn('registry_index.json', normalized_allowed_outputs())


if __name__ == '__main__':
    unittest.main()
