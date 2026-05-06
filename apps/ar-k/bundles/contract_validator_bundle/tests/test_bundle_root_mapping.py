from __future__ import annotations

import unittest
from pathlib import Path

from ark_contract_validator_bundle.runtime.canon import (
    ARCHIVE_TOP_LEVEL_DIR,
    INSTALLED_BUNDLE_DIRNAME,
    bundle_root_role,
    canonical_bundle_mapping,
    is_canonical_bundle_root_name,
)


class BundleRootMappingTests(unittest.TestCase):
    def test_canon_mapping_accepts_archive_and_installed_names(self) -> None:
        mapping = canonical_bundle_mapping()
        self.assertEqual(mapping['archive_top_level_dir'], ARCHIVE_TOP_LEVEL_DIR)
        self.assertEqual(mapping['installed_subtree_name'], INSTALLED_BUNDLE_DIRNAME)
        self.assertTrue(is_canonical_bundle_root_name(ARCHIVE_TOP_LEVEL_DIR))
        self.assertTrue(is_canonical_bundle_root_name(INSTALLED_BUNDLE_DIRNAME))
        self.assertFalse(is_canonical_bundle_root_name('weird_bundle_name'))

    def test_bundle_root_role_classifies_expected_names(self) -> None:
        self.assertEqual(bundle_root_role(Path('/tmp') / ARCHIVE_TOP_LEVEL_DIR), 'archive_top_level')
        self.assertEqual(bundle_root_role(Path('/tmp') / INSTALLED_BUNDLE_DIRNAME), 'installed_subtree')
        self.assertEqual(bundle_root_role('odd_name'), 'unknown')
