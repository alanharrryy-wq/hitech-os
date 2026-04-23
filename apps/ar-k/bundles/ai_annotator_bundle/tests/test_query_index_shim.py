
from __future__ import annotations

import unittest

from checks.registry_index_shim_checks import IndexShimError, assert_index_shim_context
from core.index_compat import IndexNameError, canonical_index_name


class QueryIndexShimTests(unittest.TestCase):
    def test_legacy_alias_maps_to_canonical_name(self) -> None:
        self.assertEqual(canonical_index_name('query_index.json'), 'registry_index.json')
        assert_index_shim_context('query_index.json', 'reader_compat')

    def test_illegal_context_is_rejected(self) -> None:
        with self.assertRaises(IndexShimError):
            assert_index_shim_context('query_index.json', 'writer')
        with self.assertRaises(IndexNameError):
            canonical_index_name('weird_index.json')


if __name__ == '__main__':
    unittest.main()
