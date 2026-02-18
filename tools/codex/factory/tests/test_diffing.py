from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import diffing  # noqa: E402


class DiffingTests(unittest.TestCase):
    def test_unified_patch_is_sorted_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="diffing_sorted_") as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "b.txt").write_text("new-b\n", encoding="utf-8")
            (repo_root / "a.txt").write_text("new-a\n", encoding="utf-8")

            def fake_show(path: str) -> str:
                return {
                    "a.txt": "old-a\n",
                    "b.txt": "old-b\n",
                }.get(path, "")

            with patch.object(diffing, "REPO_ROOT", repo_root), patch.object(diffing, "_git_show", side_effect=fake_show):
                patch_text = diffing.unified_patch_for_paths(["b.txt", "a.txt", "a.txt"])

            a_idx = patch_text.index("a/a.txt")
            b_idx = patch_text.index("a/b.txt")
            self.assertLess(a_idx, b_idx)
            self.assertIn("-old-a", patch_text)
            self.assertIn("+new-a", patch_text)
            self.assertIn("-old-b", patch_text)
            self.assertIn("+new-b", patch_text)

    def test_unified_patch_empty_when_no_changes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="diffing_empty_") as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "same.txt").write_text("same\n", encoding="utf-8")
            with patch.object(diffing, "REPO_ROOT", repo_root), patch.object(diffing, "_git_show", return_value="same\n"):
                patch_text = diffing.unified_patch_for_paths(["same.txt"])
            self.assertEqual("", patch_text)

    def test_unified_patch_handles_added_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="diffing_added_") as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "added.txt").write_text("brand new\n", encoding="utf-8")
            with patch.object(diffing, "REPO_ROOT", repo_root), patch.object(diffing, "_git_show", return_value=""):
                patch_text = diffing.unified_patch_for_paths(["added.txt"])
            self.assertIn("a/added.txt", patch_text)
            self.assertIn("b/added.txt", patch_text)
            self.assertIn("+brand new", patch_text)

    def test_unified_patch_handles_deleted_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="diffing_deleted_") as temp_dir:
            repo_root = Path(temp_dir)
            # missing file in workspace means deletion from HEAD.
            with patch.object(diffing, "REPO_ROOT", repo_root), patch.object(diffing, "_git_show", return_value="removed\n"):
                patch_text = diffing.unified_patch_for_paths(["deleted.txt"])
            self.assertIn("-removed", patch_text)
            self.assertIn("a/deleted.txt", patch_text)
            self.assertIn("b/deleted.txt", patch_text)


if __name__ == "__main__":
    unittest.main()

