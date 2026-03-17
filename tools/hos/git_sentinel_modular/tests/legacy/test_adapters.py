from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.legacy.adapters import build_legacy_scan_once_adapter


class LegacyAdaptersTestCase(unittest.TestCase):
    def test_build_legacy_scan_once_adapter(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        runtime = Path(tmp.name) / "runtime"
        (repo / ".git").mkdir(parents=True, exist_ok=True)
        (repo / "src").mkdir()
        (repo / "src" / "config.env").write_text("SECRET=my-secret\n", encoding="utf-8")

        result = build_legacy_scan_once_adapter(str(repo), str(runtime))
        self.assertTrue(Path(result["report_json_path"]).exists())
        self.assertIn("ci_gate", result)


if __name__ == "__main__":
    unittest.main()
