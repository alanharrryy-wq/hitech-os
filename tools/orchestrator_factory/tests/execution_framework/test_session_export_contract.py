from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _test_support import OneButtonFrameworkTestCase, assert_acceptance_stub_shape


class TestSessionExportContract(OneButtonFrameworkTestCase):
    def test_exported_zip_matches_required_contract_and_acceptance_stub_schema(self) -> None:
        framework_root = self.make_temp_framework()

        proc = self.run_launcher(
            framework_root,
            '--session-mode', 'new_project',
            '--policy', 'open_new_round',
            '--project-id', 'zeta_project',
            '--project-name', 'Zeta Project',
            '--initiative-type', 'operations',
            '--intent', 'Export a canonical zip for validation',
            '--non-interactive',
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = self.parse_json_output(proc)
        zip_path = Path(payload['canonical_zip_path'])
        self.assertTrue(zip_path.exists())

        zip_paths = self.list_zip_paths(zip_path)
        required_files = self.load_expected_required_files()
        for required_path in required_files:
            self.assertIn(required_path, zip_paths)

        session_manifest = self.read_zip_json(zip_path, 'session/session_manifest.json')
        self.assertEqual(session_manifest['status'], 'ready_for_dispatch')
        self.assertEqual(session_manifest['project']['project_id'], 'zeta_project')

        file_index = self.read_zip_json(zip_path, 'session/session_file_index.json')
        self.assertTrue(any(item['path'] == 'session/session_manifest.json' for item in file_index))
        self.assertTrue(all(sorted(item.keys()) == ['path', 'sha256', 'size_bytes'] for item in file_index))

        acceptance_report = self.read_zip_json(zip_path, 'round/reports/acceptance_report.json')
        assert_acceptance_stub_shape(self, acceptance_report)
        self.assertEqual(acceptance_report['project_id'], 'zeta_project')
        self.assertEqual(acceptance_report['run_id'], 'run_001')
        self.assertEqual(acceptance_report['round_id'], 'round_001')

        validator = framework_root / 'tools' / 'execution_framework' / 'validate_session_zip_contract.py'
        report_path = zip_path.with_suffix('.wave5.validation.json')
        validation = subprocess.run(
            [
                sys.executable,
                str(validator),
                '--framework-root',
                str(framework_root),
                '--zip-path',
                str(zip_path),
                '--output-report',
                str(report_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(validation.returncode, 0, msg=validation.stderr or validation.stdout)
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding='utf-8'))
        self.assertTrue(report['validation']['required_files_present'])
        self.assertTrue(report['validation']['acceptance_report_valid'])
        self.assertTrue(report['validation']['session_manifest_valid'])
        self.assertTrue(report['validation']['session_file_index_valid'])
        self.assertEqual(report['validation']['errors'], [])

    def test_acceptance_stub_from_validator_matches_schema_required_fields(self) -> None:
        framework_root = self.make_temp_framework()
        validator = framework_root / 'tools' / 'execution_framework' / 'validate_session_zip_contract.py'
        proc = subprocess.run(
            [
                sys.executable,
                str(validator),
                '--framework-root',
                str(framework_root),
                '--print-acceptance-stub',
                '--project-id', 'schema_demo',
                '--run-id', 'run_007',
                '--round-id', 'round_003',
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        payload = json.loads(proc.stdout)
        assert_acceptance_stub_shape(self, payload)
        self.assertEqual(payload['project_id'], 'schema_demo')
        self.assertEqual(payload['run_id'], 'run_007')
        self.assertEqual(payload['round_id'], 'round_003')


if __name__ == '__main__':
    import unittest

    unittest.main()
