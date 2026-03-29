from __future__ import annotations

import hashlib
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

        zip_sha256 = self._sha256_file(zip_path)
        zip_size = zip_path.stat().st_size
        sidecar_sha256 = self._read_sha256_sidecar(zip_path.with_suffix('.sha256'))
        self.assertEqual(sidecar_sha256, zip_sha256)

        sidecar_manifest = json.loads(zip_path.with_suffix('.manifest.json').read_text(encoding='utf-8'))
        artifacts = sidecar_manifest['artifacts']
        self.assertEqual(artifacts['session_zip_path'], str(zip_path))
        self.assertEqual(artifacts['session_zip_sha256'], zip_sha256)
        self.assertEqual(artifacts['session_zip_size_bytes'], zip_size)

        internal_manifest = self.read_zip_json(zip_path, 'session/session_manifest.json')
        self.assertEqual(internal_manifest['artifacts']['session_zip_sha256'], '0' * 64)
        self.assertEqual(internal_manifest['artifacts']['session_zip_size_bytes'], 0)

    def test_rerun_keeps_each_export_integrity_consistent(self) -> None:
        framework_root = self.make_temp_framework()
        launch_args = (
            '--session-mode', 'new_project',
            '--policy', 'open_new_round',
            '--project-id', 'zeta_reuse_project',
            '--project-name', 'Zeta Reuse Project',
            '--initiative-type', 'operations',
            '--intent', 'Export once and then reuse without drift',
            '--non-interactive',
        )

        first = self.run_launcher(framework_root, *launch_args)
        self.assertEqual(first.returncode, 0, msg=first.stderr)
        first_payload = self.parse_json_output(first)
        self.assertEqual(first_payload['status'], 'ready_for_dispatch')
        zip_path = Path(first_payload['canonical_zip_path'])
        first_zip_sha, first_sidecar_sha, first_manifest_payload = self._read_export_integrity(zip_path)

        second = self.run_launcher(framework_root, *launch_args)
        self.assertEqual(second.returncode, 0, msg=second.stderr)
        second_payload = self.parse_json_output(second)
        self.assertIn(second_payload['status'], {'ready_for_dispatch', 'reused'})
        second_zip_path = Path(second_payload['canonical_zip_path'])
        second_zip_sha, second_sidecar_sha, second_manifest_payload = self._read_export_integrity(second_zip_path)

        self.assertEqual(first_zip_sha, first_sidecar_sha)
        self.assertEqual(second_zip_sha, second_sidecar_sha)
        self.assertEqual(first_manifest_payload['artifacts']['session_zip_sha256'], first_zip_sha)
        self.assertEqual(second_manifest_payload['artifacts']['session_zip_sha256'], second_zip_sha)

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

    @staticmethod
    def _sha256_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open('rb') as fh:
            while True:
                chunk = fh.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _read_sha256_sidecar(path: Path) -> str:
        line = path.read_text(encoding='utf-8').strip()
        return line.split()[0] if line else ''

    def _read_export_integrity(self, zip_path: Path) -> tuple[str, str, dict]:
        zip_sha = self._sha256_file(zip_path)
        sidecar_sha = self._read_sha256_sidecar(zip_path.with_suffix('.sha256'))
        sidecar_manifest = json.loads(zip_path.with_suffix('.manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(sidecar_manifest['artifacts']['session_zip_path'], str(zip_path))
        self.assertEqual(sidecar_manifest['artifacts']['session_zip_sha256'], zip_sha)
        self.assertEqual(sidecar_manifest['artifacts']['session_zip_size_bytes'], zip_path.stat().st_size)
        return zip_sha, sidecar_sha, sidecar_manifest


if __name__ == '__main__':
    import unittest

    unittest.main()
