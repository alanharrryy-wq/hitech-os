from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.scanning.repository import RepositoryScanner


class RepositoryScannerTestCase(unittest.TestCase):
    def _make_repo(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ".git").mkdir()
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
        (root / "README.md").write_text("# hello\n", encoding="utf-8")
        (root / "node_modules").mkdir()
        (root / "node_modules" / "ignore.js").write_text("ignored", encoding="utf-8")
        return root

    def test_scan_paths_skips_ignored_directories(self):
        repo = self._make_repo()
        scanner = RepositoryScanner()
        request = scanner.build_request(repo)
        snapshot = scanner.scan_paths(request)
        self.assertIn("src/main.py", snapshot.discovered_files)
        self.assertIn("README.md", snapshot.discovered_files)
        self.assertNotIn("node_modules/ignore.js", snapshot.discovered_files)

    def test_scan_repository_returns_typed_result(self):
        repo = self._make_repo()
        scanner = RepositoryScanner()
        result = scanner.scan_repository(str(repo))
        self.assertEqual(result.repo_root, str(repo.resolve()))
        self.assertGreaterEqual(result.stats.scanned_files, 2)


if __name__ == "__main__":
    unittest.main()
