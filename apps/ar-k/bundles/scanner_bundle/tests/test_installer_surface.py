from __future__ import annotations

import unittest

import scanner_installer

class InstallerSurfaceTests(unittest.TestCase):
    def test_cli_only_exposes_homologated_flags(self) -> None:
        parser = scanner_installer.build_parser()
        options = {opt for action in parser._actions for opt in action.option_strings}
        expected = {'--dry-run', '--apply', '--verify', '--rollback', '--root', '--log-dir', '--install-rel'}
        self.assertTrue(expected.issubset(options))
        self.assertFalse({'--payload', '--bundle'}.intersection(options))

    def test_default_install_rel_is_homologated(self) -> None:
        parser = scanner_installer.build_parser()
        args = parser.parse_args(['--dry-run', '--root', '/tmp/demo'])
        self.assertEqual(args.install_rel, 'bundles/scanner_bundle')

if __name__ == '__main__':
    unittest.main()
