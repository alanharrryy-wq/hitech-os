from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.fs_guard import WriteGuard, WritePolicyError  # noqa: E402


class WriteGuardTests(unittest.TestCase):
    def test_write_inside_allowed_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="guard_allow_") as temp_dir:
            root = Path(temp_dir)
            guard = WriteGuard(root)
            target = root / "a" / "b" / "file.txt"
            guard.write_text(target, "ok")
            self.assertTrue(target.exists())
            self.assertEqual("ok", target.read_text(encoding="utf-8"))

    def test_write_outside_allowed_root_raises(self) -> None:
        with tempfile.TemporaryDirectory(prefix="guard_block_") as temp_dir:
            root = Path(temp_dir) / "allowed"
            root.mkdir(parents=True, exist_ok=True)
            guard = WriteGuard(root)
            outside = root.parent / "outside.txt"
            with self.assertRaises(WritePolicyError):
                guard.write_text(outside, "blocked")

    def test_append_line_inside_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="guard_append_") as temp_dir:
            root = Path(temp_dir)
            guard = WriteGuard(root)
            log = root / "LOGS" / "integration.log.txt"
            guard.append_line(log, "first")
            guard.append_line(log, "second")
            self.assertEqual("first\nsecond\n", log.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

