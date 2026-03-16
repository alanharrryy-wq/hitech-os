from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.orchestrator import OrchestratorConfig, SentinelOrchestrator


def build_legacy_scan_once_adapter(repo_root: str, runtime_root: str) -> dict[str, Any]:
    runtime = Path(runtime_root).resolve()
    runtime.mkdir(parents=True, exist_ok=True)

    config = OrchestratorConfig(
        repo_root=repo_root,
        learning_db_path=str(runtime / "learning.sqlite3"),
        report_json_path=str(runtime / "report.json"),
        report_md_path=str(runtime / "report.md"),
        alert_output_path=str(runtime / "alert.txt"),
        run_alerting=True,
    )
    result = SentinelOrchestrator(config).run_once()
    return {
        "repo_root": result["repo_root"],
        "ci_gate": result["ci_gate"],
        "report_json_path": config.report_json_path,
        "report_md_path": config.report_md_path,
        "alert_output_path": config.alert_output_path,
    }
