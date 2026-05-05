from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.count_bundle_mix import inspect_directory, inspect_zip


class CountBundleMixTests(unittest.TestCase):
    def test_directory_py_ratio_exceeds_threshold(self) -> None:
        root = Path(__file__).resolve().parents[1]
        data = inspect_directory(root)
        self.assertGreaterEqual(data['py_ratio'], 0.9)
        self.assertGreater(data['py_count'], data['non_py_count'])
        self.assertEqual(data['dirty_entry_count'], 0)

    def test_zip_inspection_flags_compiled_junk(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            zip_path = Path(td) / 'dirty.zip'
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('ark_ai_annotator_bundle/good.py', 'print("ok")\n')
                zf.writestr('ark_ai_annotator_bundle/__pycache__/good.cpython-313.pyc', b'junk')
            data = inspect_zip(zip_path)
            self.assertEqual(data['file_count'], 2)
            self.assertEqual(data['py_count'], 1)
            self.assertEqual(data['dirty_entry_count'], 1)
            self.assertIn('ark_ai_annotator_bundle/__pycache__/good.cpython-313.pyc', data['dirty_entries'])
            self.assertLess(data['py_ratio'], 0.9)


if __name__ == '__main__':
    unittest.main()
