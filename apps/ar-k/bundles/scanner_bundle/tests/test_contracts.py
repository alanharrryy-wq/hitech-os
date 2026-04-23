from __future__ import annotations

import unittest

from contracts_py.legacy_compat import canonicalize_index_name
from contracts_py.ownership_rules import scanner_may_write, scanner_must_not_write
from contracts_py.scanner_contract import validate_scanner_write_target

class ContractTests(unittest.TestCase):
    def test_legacy_index_uses_explicit_shim(self) -> None:
        name, used = canonicalize_index_name('query_index.json')
        self.assertEqual(name, 'registry_index.json')
        self.assertTrue(used)

    def test_scanner_scope_rejects_canonical_writes(self) -> None:
        self.assertTrue(scanner_may_write('scan_observed_modules.json'))
        self.assertTrue(scanner_must_not_write('registry_index.json'))
        with self.assertRaises(ValueError):
            validate_scanner_write_target('registry_index.json')

if __name__ == '__main__':
    unittest.main()
