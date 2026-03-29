from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.hos.git_sentinel_modular.app.cli import main


class CLITestCase(unittest.TestCase):
    def test_cli_main_runs(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True, exist_ok=True)
        (repo / "src").mkdir()
        (repo / "src" / "config.env").write_text("SECRET=my-secret\n", encoding="utf-8")
        learning_db = Path(tmp.name) / "learning.sqlite3"
        report_json = Path(tmp.name) / "report.json"
        report_md = Path(tmp.name) / "report.md"

        with patch("builtins.print") as mocked_print:
            rc = main([
                "--repo-root", str(repo),
                "--learning-db", str(learning_db),
                "--report-json", str(report_json),
                "--report-md", str(report_md),
                "--no-alerting",
            ])
        self.assertEqual(rc, 0)
        self.assertTrue(mocked_print.called)


if __name__ == "__main__":
    unittest.main()
