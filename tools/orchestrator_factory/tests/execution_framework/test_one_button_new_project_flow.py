from __future__ import annotations

from pathlib import Path

from _test_support import OneButtonFrameworkTestCase


class TestOneButtonNewProjectFlow(OneButtonFrameworkTestCase):
    def test_new_project_dry_run_returns_clear_runtime_summary(self) -> None:
        framework_root = self.make_temp_framework()

        proc = self.run_launcher(
            framework_root,
            '--session-mode', 'new_project',
            '--policy', 'open_new_round',
            '--project-id', 'gamma_project',
            '--project-name', 'Gamma Project',
            '--initiative-type', 'platform',
            '--intent', 'Bootstrap a brand new project session',
            '--non-interactive',
            '--dry-run',
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = self.parse_json_output(proc)
        self.assertEqual(payload['status'], 'ready')
        self.assertEqual(payload['run_id'], 'run_001')
        self.assertEqual(payload['round_id'], 'round_001')
        self.assertEqual(payload['project_name'], 'Gamma Project')
        self.assertTrue(payload['canonical_zip_path'].endswith('.zip'))

    def test_new_project_full_run_exports_canonical_zip(self) -> None:
        framework_root = self.make_temp_framework()

        proc = self.run_launcher(
            framework_root,
            '--session-mode', 'new_project',
            '--policy', 'open_new_round',
            '--project-id', 'delta_project',
            '--project-name', 'Delta Project',
            '--initiative-type', 'research',
            '--intent', 'Export a canonical session bundle for downstream dispatch',
            '--non-interactive',
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = self.parse_json_output(proc)
        self.assertEqual(payload['status'], 'ready_for_dispatch')
        zip_path = Path(payload['canonical_zip_path'])
        self.assertTrue(zip_path.exists(), msg=f'Expected ZIP to exist at {zip_path}')
        self.assertTrue((zip_path.with_suffix('.sha256')).exists())
        self.assertTrue((zip_path.with_suffix('.manifest.json')).exists())
        self.assertTrue(Path(payload['ledger_path']).exists())


if __name__ == '__main__':
    import unittest

    unittest.main()
