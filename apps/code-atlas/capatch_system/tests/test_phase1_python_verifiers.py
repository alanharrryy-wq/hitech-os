from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from capatch_verify.registry import run_required_verifiers
from capatch_policy.verification_requirements import assess_verification_outcome, compute_verification_policy


class Phase1PythonVerifierTests(unittest.TestCase):
    def test_python_import_smoke_performs_real_import(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase1_import_') as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / 'pkg'
            pkg.mkdir(parents=True, exist_ok=True)
            (pkg / '__init__.py').write_text('', encoding='utf-8')
            target = pkg / 'service.py'
            target.write_text('from pkg.missing import nope\n', encoding='utf-8')
            rows = run_required_verifiers(
                [str(target)],
                ['python-parse', 'python-compile-smoke', 'python-import-smoke'],
                {'root_dir': str(root)},
            )
            by_id = {row['verifier_id']: row for row in rows}
            self.assertTrue(by_id['python-parse']['ok'])
            self.assertTrue(by_id['python-compile-smoke']['ok'])
            self.assertFalse(by_id['python-import-smoke']['ok'])
            self.assertEqual('ModuleNotFoundError', by_id['python-import-smoke']['metrics'].get('exception_class'))

    def test_python_boot_smoke_checks_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase1_boot_') as tmp_dir:
            root = Path(tmp_dir)
            target = root / 'main.py'
            target.write_text('def main() -> int:\n    return 0\n', encoding='utf-8')
            rows = run_required_verifiers([str(target)], ['python-boot-smoke'], {'root_dir': str(root)})
            self.assertEqual(1, len(rows))
            self.assertTrue(rows[0]['ok'])

    def test_verification_policy_requires_compile_and_import_for_python(self) -> None:
        policy = compute_verification_policy({'risk_level': 'medium'}, ['pkg/service.py'])
        self.assertEqual('runtime', policy['verification_floor'])
        self.assertIn('python-compile-smoke', policy['required_verifiers'])
        self.assertIn('python-import-smoke', policy['required_verifiers'])

    def test_assessment_fails_when_required_verifier_missing(self) -> None:
        assessment = assess_verification_outcome(
            {'risk_level': 'medium'},
            ['pkg/service.py'],
            [
                {'verifier_id': 'python-parse', 'ok': True},
                {'verifier_id': 'python-compile-smoke', 'ok': True},
            ],
        )
        self.assertFalse(assessment['passed'])
        self.assertIn('python-import-smoke', assessment['missing_required_verifiers'])

    def test_typescript_parse_fallback_detects_hook_boundary_issue(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_phase1_ts_') as tmp_dir:
            root = Path(tmp_dir)
            target = root / 'Component.tsx'
            target.write_text(
                "import { useState } from 'react';\n\nexport function Component() {\n    const [count] = useState(0);\n    return <div>{count}</div>;\n}\n",
                encoding='utf-8',
            )
            with patch('capatch_verify.builtin_typescript.shutil.which', return_value=None):
                rows = run_required_verifiers([str(target)], ['typescript-parse'], {'root_dir': str(root)})
            self.assertEqual(1, len(rows))
            self.assertFalse(rows[0]['ok'])
            self.assertIn('use client', rows[0]['detail'])

    def test_verification_policy_requires_typescript_parse_for_ts_targets(self) -> None:
        policy = compute_verification_policy({'risk_level': 'medium'}, ['ui/Component.tsx'])
        self.assertEqual('syntax', policy['verification_floor'])
        self.assertIn('typescript-parse', policy['required_verifiers'])


if __name__ == '__main__':
    unittest.main()
