from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import unittest

from compat.query_index_alias import (
    adapt_registry_index_for_legacy,
    canonical_name,
    legacy_alias_metadata,
    legacy_name,
    resolve_requested_name,
)
from fixtures.catalog import load_all_cases
from policy.promotion_policy import build_canonical_outputs


class QueryIndexCompatTests(unittest.TestCase):
    def test_canonical_name_stays_registry_index(self) -> None:
        self.assertEqual(canonical_name(), 'registry_index.json')
        self.assertEqual(legacy_name(), 'query_index.json')

    def test_requested_name_always_resolves_to_canonical_source(self) -> None:
        self.assertEqual(resolve_requested_name('registry_index.json'), 'registry_index.json')
        self.assertEqual(resolve_requested_name('query_index.json'), 'registry_index.json')
        with self.assertRaises(ValueError):
            resolve_requested_name('totally_not_real.json')

    def test_legacy_payload_is_explicit_alias_only(self) -> None:
        case = load_all_cases()[0]
        outputs = build_canonical_outputs(case['observed_signals'], execution_id=case['scenario_id'])
        legacy_view = adapt_registry_index_for_legacy(outputs['registry_index'])
        self.assertEqual(legacy_view['canonical_source'], 'registry_index.json')
        self.assertEqual(legacy_view['requested_name'], 'query_index.json')
        self.assertEqual(legacy_view['authoritative'], 'false')
        self.assertEqual(len(legacy_view['entries']), len(outputs['registry_index']))
        self.assertEqual(legacy_alias_metadata()['canonical_source'], 'registry_index.json')


if __name__ == '__main__':
    unittest.main()
