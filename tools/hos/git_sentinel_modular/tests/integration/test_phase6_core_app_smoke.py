from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.app.dashboard import build_dashboard_snapshot
from tools.hos.git_sentinel_modular.core.orchestrator import OrchestratorConfig, SentinelOrchestrator
from tools.hos.git_sentinel_modular.reporting.generator import SentinelReportGenerator


class Phase6CoreAppSmokeTestCase(unittest.TestCase):
    def test_orchestrator_to_dashboard_smoke(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        runtime = Path(tmp.name) / "runtime"
        (repo / ".git").mkdir(parents=True, exist_ok=True)
        (repo / "src").mkdir()
        (repo / "src" / "config.env").write_text("SECRET=my-secret\n", encoding="utf-8")
        (repo / "dist").mkdir()
        (repo / "dist" / "app.js").write_text("console.log('x')\n", encoding="utf-8")
        runtime.mkdir()

        config = OrchestratorConfig(
            repo_root=str(repo),
            learning_db_path=str(runtime / "learning.sqlite3"),
            report_json_path=str(runtime / "report.json"),
            report_md_path=str(runtime / "report.md"),
            alert_output_path=str(runtime / "alert.txt"),
        )
        result = SentinelOrchestrator(config).run_once()
        report = SentinelReportGenerator().build_report(
            scan_result=SentinelReportGenerator().build_report(
                scan_result=None, predictions=None, repair_plan=None, cleanup_plan=None
            ) if False else None,
            predictions=[], repair_plan=None, cleanup_plan=None
        ) if False else None
        # real assertion path
        import json
        payload = json.loads(Path(runtime / "report.json").read_text(encoding="utf-8"))
        from tools.hos.git_sentinel_modular.shared.contracts import SentinelReport
        dashboard = build_dashboard_snapshot(SentinelReport(**payload).validate())
        self.assertEqual(dashboard["repo_root"], str(repo.resolve()))


if __name__ == "__main__":
    unittest.main()
