from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.core.orchestrator import OrchestratorConfig, SentinelOrchestrator


class SentinelOrchestratorTestCase(unittest.TestCase):
    def test_run_once(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True, exist_ok=True)
        (repo / "src").mkdir()
        (repo / "src" / "config.env").write_text("SECRET=my-secret\n", encoding="utf-8")
        (repo / "dist").mkdir()
        (repo / "dist" / "app.js").write_text("console.log('x')\n", encoding="utf-8")
        runtime = Path(tmp.name) / "runtime"
        runtime.mkdir()

        config = OrchestratorConfig(
            repo_root=str(repo),
            learning_db_path=str(runtime / "learning.sqlite3"),
            report_json_path=str(runtime / "report.json"),
            report_md_path=str(runtime / "report.md"),
            alert_output_path=str(runtime / "alert.txt"),
        )
        result = SentinelOrchestrator(config).run_once()
        self.assertIn("report", result)
        self.assertTrue((runtime / "report.json").exists())
        self.assertTrue((runtime / "report.md").exists())
        self.assertTrue((runtime / "alert.txt").exists())


if __name__ == "__main__":
    unittest.main()
