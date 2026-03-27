from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

from lib.common import deterministic_zip_dir


class DeterministicZipTests(unittest.TestCase):
    def test_zip_bytes_are_stable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source = tmp / "source"
            source.mkdir()
            (source / "a.txt").write_text("hello\n", encoding="utf-8")
            zip1 = tmp / "one.zip"
            zip2 = tmp / "two.zip"
            deterministic_zip_dir(source, zip1)
            deterministic_zip_dir(source, zip2)
            self.assertEqual(hashlib.sha256(zip1.read_bytes()).hexdigest(), hashlib.sha256(zip2.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
