from __future__ import annotations

import json
from pathlib import Path

from _test_support import OneButtonFrameworkTestCase


class TestOneButtonExistingFlow(OneButtonFrameworkTestCase):
    def test_existing_project_open_new_round_dry_run_resolves_next_round(self) -> None:
        framework_root = self.make_temp_framework()
        self.seed_existing_project(framework_root, project_id='alpha_project', run_id='run_001', latest_round_id='round_002')

        proc = self.run_launcher(
            framework_root,
            '--session-mode', 'existing_project',
            '--policy', 'open_new_round',
            '--project-id', 'alpha_project',
            '--intent', 'Advance planning for the next execution round',
            '--non-interactive',
            '--dry-run',
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = self.parse_json_output(proc)
        self.assertEqual(payload['status'], 'ready')
        self.assertEqual(payload['session_mode'], 'existing_project')
        self.assertEqual(payload['policy'], 'open_new_round')
        self.assertEqual(payload['run_id'], 'run_001')
        self.assertEqual(payload['round_id'], 'round_003')
        self.assertIn('canonical_zip_path', payload)
        self.assertTrue(payload['canonical_zip_path'].endswith('.zip'))
        self.assertIn('Wave 4 dry-run computed idempotency', ' '.join(payload['notes']))

    def test_existing_project_resume_latest_round_reuses_latest_identifiers(self) -> None:
        framework_root = self.make_temp_framework()
        self.seed_existing_project(framework_root, project_id='beta_project', run_id='run_004', latest_round_id='round_009')

        proc = self.run_launcher(
            framework_root,
            '--session-mode', 'existing_project',
            '--policy', 'resume_latest_round',
            '--project-id', 'beta_project',
            '--intent', 'Resume the active round without creating anything new',
            '--non-interactive',
            '--dry-run',
        )

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = self.parse_json_output(proc)
        self.assertEqual(payload['status'], 'ready')
        self.assertEqual(payload['run_id'], 'run_004')
        self.assertEqual(payload['round_id'], 'round_009')
        self.assertIn('project_manifest', payload['touched_paths'])
        self.assertTrue(payload['project_manifest_path'].endswith('project_manifest.json'))


if __name__ == '__main__':
    import unittest

    unittest.main()
