from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from ark_contract_validator_bundle.tools.validate_contract_validator_bundle import validate


class ValidateBundleToolTests(unittest.TestCase):
    def test_bundle_validates_from_archive_root(self) -> None:
        bundle_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_root = Path(tmpdir) / 'ark_contract_validator_bundle'
            shutil.copytree(bundle_root, archive_root)
            result = validate(archive_root)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['bundle_root_role'], 'archive_top_level')

    def test_bundle_validates_from_installed_subtree_name(self) -> None:
        bundle_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / 'contract_validator_bundle'
            shutil.copytree(bundle_root, target)
            result = validate(target)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['bundle_root_role'], 'installed_subtree')
        self.assertNotIn('top_level_dir_mismatch:contract_validator_bundle', result['issues'])
