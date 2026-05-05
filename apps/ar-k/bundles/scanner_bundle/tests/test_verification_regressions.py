from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import payload_manifest
import scanner_installer
from contracts_py.scanner_contract import FORBIDDEN_SCANNER_WRITES


class VerificationRegressionTests(unittest.TestCase):
    def test_install_surface_covers_full_bundle_root(self) -> None:
        bundle_root = Path(__file__).resolve().parents[1]
        surface = payload_manifest.install_surface(bundle_root)
        self.assertGreater(len(surface), 100)
        self.assertIn('scanner_installer.py', surface)
        self.assertIn('tools/validate_scanner_bundle.py', surface)
        self.assertIn('payload/bundles/scanner_bundle/scanner_engine_snapshot.py', surface)

    def test_verify_fails_when_bundle_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as log_dir:
            self.assertEqual(scanner_installer.main(['--apply', '--root', root, '--log-dir', log_dir]), 0)
            install_root = Path(root) / 'bundles' / 'scanner_bundle'
            target = install_root / 'tests' / 'test_contracts.py'
            target.unlink()
            self.assertEqual(scanner_installer.main(['--verify', '--root', root, '--log-dir', log_dir]), 1)

    def test_verify_writes_examples_under_state_root_only(self) -> None:
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as log_dir:
            self.assertEqual(scanner_installer.main(['--apply', '--root', root, '--log-dir', log_dir]), 0)
            self.assertEqual(scanner_installer.main(['--verify', '--root', root, '--log-dir', log_dir]), 0)
            install_root = Path(root) / 'bundles' / 'scanner_bundle'
            state_root = Path(root) / '.ark_install' / 'scanner_bundle'
            self.assertFalse((install_root / 'generated_examples').exists())
            verification_root = state_root / 'verification_outputs'
            self.assertTrue(verification_root.exists())
            written = list(verification_root.rglob('*.json'))
            self.assertTrue(written)
            self.assertTrue(all(str(path).startswith(str(verification_root)) for path in written))
            self.assertTrue(set(FORBIDDEN_SCANNER_WRITES).isdisjoint({path.name for path in written}))


if __name__ == '__main__':
    unittest.main()
