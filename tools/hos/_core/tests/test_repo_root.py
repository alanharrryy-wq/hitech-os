from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos._core.repo_root import find_repo_root, probe_repo_root


class RepoRootTests(unittest.TestCase):
    def test_probe_repo_root_from_nested_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "package.json").write_text("{}", encoding="utf-8")
            (root / "pnpm-workspace.yaml").write_text("packages: []\n", encoding="utf-8")
            (root / "turbo.json").write_text("{}", encoding="utf-8")

            nested = root / "apps" / "demo" / "src"
            nested.mkdir(parents=True, exist_ok=True)
            found = probe_repo_root(start=nested)
            self.assertIsNotNone(found)
            assert found is not None
            self.assertEqual(found.root.resolve(), root.resolve())

    def test_find_repo_root_raises_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested = root / "x" / "y"
            nested.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(FileNotFoundError):
                _ = find_repo_root(start=nested)


if __name__ == "__main__":
    unittest.main()

