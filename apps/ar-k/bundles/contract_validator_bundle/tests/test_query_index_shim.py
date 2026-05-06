
from __future__ import annotations

import unittest

from ark_contract_validator_bundle.runtime.query_index_shim import normalize_index_name


class QueryIndexShimTests(unittest.TestCase):
    def test_query_index_alias_normalizes(self) -> None:
        self.assertEqual(normalize_index_name('query_index.json'), 'registry_index.json')
        self.assertEqual(normalize_index_name('registry_index.json'), 'registry_index.json')
