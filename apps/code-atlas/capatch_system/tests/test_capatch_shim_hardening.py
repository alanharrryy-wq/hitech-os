from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class _BrokenStderr:
    def write(self, _value: str) -> int:
        raise OSError('broken stderr')

    def flush(self) -> None:
        return None


class CapatchShimHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(self.root))
        self.capatch = importlib.import_module('capatch')
        self.capatch = importlib.reload(self.capatch)

    def tearDown(self) -> None:
        try:
            sys.path.remove(str(self.root))
        except ValueError:
            pass

    def test_shutdown_cleaner_failure_does_not_mask_cli_failure(self) -> None:
        with patch.object(self.capatch, '_bool_env', return_value=False):
            with patch.object(self.capatch, '_cli_main', side_effect=RuntimeError('root-cause')):
                with patch.object(self.capatch, 'load_workspace_cleaner_policy', return_value={}):
                    with patch.object(self.capatch, 'run_startup_cleaner', return_value={'status': 'ok'}):
                        with patch.object(self.capatch, 'run_shutdown_cleaner', side_effect=RuntimeError('cleanup-failed')):
                            with self.assertRaises(RuntimeError) as raised:
                                self.capatch.main(['--ops-file', 'ops.json'])
        self.assertEqual('root-cause', str(raised.exception))

    def test_startup_cleaner_failure_degrades_but_keeps_cli_result(self) -> None:
        with patch.object(self.capatch, '_bool_env', return_value=False):
            with patch.object(self.capatch, '_cli_main', return_value=7):
                with patch.object(self.capatch, 'load_workspace_cleaner_policy', return_value={}):
                    with patch.object(self.capatch, 'run_startup_cleaner', side_effect=RuntimeError('startup-failed')):
                        with patch.object(self.capatch, 'run_shutdown_cleaner', return_value=None):
                            code = self.capatch.main(['--ops-file', 'ops.json'])
        self.assertEqual(7, code)

    def test_compat_notice_cannot_fail_on_broken_stderr(self) -> None:
        with patch.object(self.capatch, '_bool_env', return_value=True):
            with patch.object(self.capatch, '_cli_main', return_value=0):
                with patch.object(self.capatch.sys, 'stderr', _BrokenStderr()):
                    self.assertEqual(0, self.capatch.main(['--self-test']))


if __name__ == '__main__':
    unittest.main()
