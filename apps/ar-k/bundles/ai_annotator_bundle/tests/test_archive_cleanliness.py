from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.count_bundle_mix import inspect_zip


BUNDLE_ROOT = Path(__file__).resolve().parents[1]
BUILD_TOOL = BUNDLE_ROOT / 'tools' / 'build_clean_bundle.py'


class ArchiveCleanlinessTests(unittest.TestCase):
    def test_rebuilt_zip_is_clean_and_python_heavy(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            zip_path = Path(td) / 'bundle.zip'
            env = dict(os.environ)
            env['PYTHONDONTWRITEBYTECODE'] = '1'
            subprocess.run([sys.executable, str(BUILD_TOOL), str(zip_path)], check=True, capture_output=True, text=True, env=env)
            data = inspect_zip(zip_path)
            self.assertEqual(data['dirty_entry_count'], 0)
            self.assertGreaterEqual(data['py_ratio'], 0.9)
            self.assertEqual(data['top_level_entries'], ['ark_ai_annotator_bundle'])


if __name__ == '__main__':
    unittest.main()
