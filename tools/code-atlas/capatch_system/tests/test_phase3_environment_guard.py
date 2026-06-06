from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from capatch_runtime.environment_guard import capture_environment_guard, evaluate_environment_guard


class EnvironmentGuardTests(unittest.TestCase):
    def test_capture_and_evaluate_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'capatch_system'
            root.mkdir(parents=True, exist_ok=True)
            (root / 'reports').mkdir()
            payload = capture_environment_guard(root, root)
            verdict = evaluate_environment_guard(payload)
            self.assertIn(verdict['status'], {'healthy', 'degraded'})
            self.assertTrue(payload['environment_fingerprint'])
            self.assertEqual(str(root.resolve()), payload['base_dir'])

    def test_guard_blocks_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'capatch_system'
            root.mkdir(parents=True, exist_ok=True)
            missing = root / 'missing'
            verdict = evaluate_environment_guard(capture_environment_guard(root, missing))
            self.assertEqual('blocked', verdict['status'])
            self.assertIn('target_missing', verdict['reasons'])


if __name__ == '__main__':
    unittest.main()
