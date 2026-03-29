from __future__ import annotations

from pathlib import Path
from typing import Any

from ..shared.contracts import ScanConfig
from ..shared.provider import ScanAdapterProvider


def build_legacy_scan_once_adapter(repo_root: str, runtime_root: str) -> dict[str, Any]:
    """
    Adapter for legacy code to run a single scan through a sentinel orchestrator.
    
    H1.1B (True Boundary Closure): This function imports ONLY from shared layer
    (ScanConfig and ScanAdapterProvider). It has ZERO direct imports from core.orchestrator.
    
    The boundary seam works like this:
    - legacy/adapters.py imports: shared.contracts.ScanConfig, shared.provider.ScanAdapterProvider
    - shared.provider internally (lazily) depends on core.orchestrator
    - legacy code never sees core.orchestrator in its namespace
    
    Args:
        repo_root: Repository root path to scan
        runtime_root: Directory for runtime artifacts (learning DB, reports, alerts)
    
    Returns:
        Dictionary with repo_root, ci_gate status, and paths to generated reports
    """
    runtime = Path(runtime_root).resolve()
    runtime.mkdir(parents=True, exist_ok=True)

    # Build config using boundary-safe ScanConfig from shared
    config = ScanConfig(
        repo_root=repo_root,
        learning_db_path=str(runtime / "learning.sqlite3"),
        report_json_path=str(runtime / "report.json"),
        report_md_path=str(runtime / "report.md"),
        alert_output_path=str(runtime / "alert.txt"),
        run_alerting=True,
    ).validate()
    
    # Get adapter class from provider (boundary seam, not direct core import)
    adapter_class = ScanAdapterProvider.get()
    
    # Instantiate and run
    adapter = adapter_class(config)
    result = adapter.run_once()
    
    return {
        "repo_root": result["repo_root"],
        "ci_gate": result["ci_gate"],
        "report_json_path": config.report_json_path,
        "report_md_path": config.report_md_path,
        "alert_output_path": config.alert_output_path,
    }
