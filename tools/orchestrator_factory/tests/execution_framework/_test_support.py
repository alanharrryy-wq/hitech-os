"""Shared helpers for one-button v1.2 test suites.

These helpers intentionally use only the Python standard library so the tests
can run in constrained Windows environments without adding dependencies.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


THIS_FILE = Path(__file__).resolve()
TESTS_ROOT = THIS_FILE.parent.parent
FRAMEWORK_ROOT = TESTS_ROOT.parent
FIXTURES_ROOT = TESTS_ROOT / 'fixtures' / 'execution_framework'


class OneButtonFrameworkTestCase(unittest.TestCase):
    maxDiff = None

    def make_temp_framework(self) -> Path:
        """Create an isolated framework copy suitable for mutating in tests.

        The test suite copies only the subtrees required by the one-button v1.2
        implementation. This keeps test setup fast while still exercising the
        real runtime modules from the current workspace.
        """
        temp_dir = Path(tempfile.mkdtemp(prefix='one_button_test_framework_'))
        framework_root = temp_dir / 'tools' / 'orchestrator_factory'
        required_paths = [
            ('tools/execution_framework', 'tools/execution_framework'),
            ('tools/one_button.ps1', 'tools/one_button.ps1'),
            ('configs/execution_framework', 'configs/execution_framework'),
            ('schemas/execution_framework', 'schemas/execution_framework'),
        ]
        for source_rel, target_rel in required_paths:
            source_path = FRAMEWORK_ROOT / source_rel
            target_path = framework_root / target_rel
            if not source_path.exists():
                continue
            if source_path.is_dir():
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
        (framework_root / 'ops' / 'projects').mkdir(parents=True, exist_ok=True)
        if os.environ.get('ONE_BUTTON_TEST_SKIP_CLEANUP', '1') != '1':
            self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        self._ensure_acceptance_schema(framework_root)
        return framework_root

    def seed_existing_project(
        self,
        framework_root: Path,
        *,
        project_id: str = 'alpha_project',
        project_name: str = 'Alpha Project',
        initiative_type: str = 'platform',
        run_id: str = 'run_001',
        latest_round_id: str = 'round_002',
    ) -> Path:
        """Seed a realistic existing project fixture under ops/projects."""
        fixture_root = FIXTURES_ROOT / 'sample_existing_project_state'
        project_root = framework_root / 'ops' / 'projects' / project_id
        round_root = project_root / 'runs' / run_id / 'rounds' / latest_round_id
        snapshots_root = round_root / 'coordination' / 'snapshots'
        reports_root = round_root / 'reports'
        snapshots_root.mkdir(parents=True, exist_ok=True)
        reports_root.mkdir(parents=True, exist_ok=True)

        self._write_json(
            project_root / 'project_manifest.json',
            self._load_fixture_json('sample_existing_project_state/project_manifest.json', project_id=project_id, project_name=project_name, initiative_type=initiative_type),
        )
        self._write_json(
            project_root / 'runs' / run_id / 'run_manifest.json',
            self._load_fixture_json('sample_existing_project_state/run_manifest.json', project_id=project_id, run_id=run_id),
        )
        self._write_json(
            round_root / 'round_manifest.json',
            self._load_fixture_json('sample_existing_project_state/round_manifest.json', project_id=project_id, run_id=run_id, round_id=latest_round_id),
        )
        self._write_json(
            snapshots_root / 'coordination_snapshot.latest.json',
            self._load_fixture_json('sample_existing_project_state/coordination_snapshot.latest.json', project_id=project_id, run_id=run_id, round_id=latest_round_id),
        )
        (snapshots_root / 'coordination_snapshot.latest.md').write_text(
            self._load_fixture_text('sample_existing_project_state/coordination_snapshot.latest.md').format(project_id=project_id, run_id=run_id, round_id=latest_round_id),
            encoding='utf-8',
        )
        self._write_json(
            reports_root / 'readiness_report.json',
            self._load_fixture_json('sample_existing_project_state/readiness_report.json', project_id=project_id, run_id=run_id, round_id=latest_round_id),
        )
        self._write_json(
            reports_root / 'acceptance_report.json',
            self._load_fixture_json('sample_existing_project_state/acceptance_report.json', project_id=project_id, run_id=run_id, round_id=latest_round_id),
        )
        return project_root

    def run_launcher(self, framework_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        entrypoint = framework_root / 'tools' / 'execution_framework' / 'one_button_session.py'
        command = [sys.executable, str(entrypoint), '--framework-root', str(framework_root), *args]
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def parse_json_output(self, process: subprocess.CompletedProcess[str]) -> Dict[str, Any]:
        payload = process.stdout.strip() or process.stderr.strip()
        self.assertTrue(payload, msg='Expected JSON output from launcher, but stdout/stderr were empty.')
        return json.loads(payload)

    def load_expected_required_files(self) -> List[str]:
        payload = self._load_fixture_json('expected_session_zip_contract.json')
        return list(payload['required_files'])

    def read_zip_json(self, zip_path: Path, member_path: str) -> Dict[str, Any]:
        import zipfile

        with zipfile.ZipFile(zip_path, 'r') as archive:
            raw = archive.read(member_path)
        return json.loads(raw.decode('utf-8'))

    def list_zip_paths(self, zip_path: Path) -> List[str]:
        import zipfile

        with zipfile.ZipFile(zip_path, 'r') as archive:
            return sorted(info.filename.replace('\\', '/') for info in archive.infolist() if not info.is_dir())

    def _ensure_acceptance_schema(self, framework_root: Path) -> None:
        target = framework_root / 'schemas' / 'execution_framework' / 'acceptance_result.schema.json'
        if target.exists():
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FIXTURES_ROOT / 'acceptance_result.schema.json', target)

    def _load_fixture_json(self, relative_path: str, **replacements: str) -> Dict[str, Any]:
        text = self._load_fixture_text(relative_path, **replacements)
        return json.loads(text)

    def _load_fixture_text(self, relative_path: str, **replacements: str) -> str:
        text = (FIXTURES_ROOT / relative_path).read_text(encoding='utf-8')
        token_map = {
            '__PROJECT_ID__': replacements.get('project_id', '__PROJECT_ID__'),
            '__PROJECT_NAME__': replacements.get('project_name', '__PROJECT_NAME__'),
            '__INITIATIVE_TYPE__': replacements.get('initiative_type', '__INITIATIVE_TYPE__'),
            '__RUN_ID__': replacements.get('run_id', '__RUN_ID__'),
            '__ROUND_ID__': replacements.get('round_id', '__ROUND_ID__'),
        }
        for token, value in token_map.items():
            text = text.replace(token, value)
        return text

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)


def assert_acceptance_stub_shape(testcase: unittest.TestCase, payload: Dict[str, Any]) -> None:
    required = [
        'schema_version',
        'project_id',
        'run_id',
        'round_id',
        'generated_at_utc',
        'overall_status',
        'package_results',
    ]
    for key in required:
        testcase.assertIn(key, payload)
    testcase.assertEqual(payload['schema_version'], '1.0')
    testcase.assertEqual(payload['overall_status'], 'pending')
    testcase.assertEqual(payload['package_results'], [])
    testcase.assertIn('has_bundles', payload)
    testcase.assertIn('accepted_bundles', payload)
    testcase.assertIn('rejected_bundles', payload)
    testcase.assertIn('notes', payload)
    testcase.assertIsInstance(payload['notes'], list)
