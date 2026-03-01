from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos._core.hashing import hash_directory


class HashingTests(unittest.TestCase):
    def test_hash_directory_is_stable_for_same_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.txt").write_text("A\n", encoding="utf-8")
            (root / "b.txt").write_text("B\n", encoding="utf-8")
            first = hash_directory(root)
            second = hash_directory(root)
            self.assertEqual(first, second)

    def test_hash_directory_changes_after_modification(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "a.txt"
            target.write_text("A\n", encoding="utf-8")
            before = hash_directory(root)
            target.write_text("A2\n", encoding="utf-8")
            after = hash_directory(root)
            self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()

