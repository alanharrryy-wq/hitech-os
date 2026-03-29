from __future__ import annotations

from pathlib import Path

from .manifest_io import write_json, write_text

def _summary_md(payload: dict) -> str:
    return (
        "# Execution summary\n\n"
        f"Status: {payload['status']}\n\n"
        f"Planned actions: {payload['counts']['planned_actions']}\n"
    )

def write_execution_reports(execution_dir: str | Path, payload: dict) -> None:
    root = Path(execution_dir)
    write_json(root / "execution_summary.json", payload)
    write_text(root / "execution_summary.md", _summary_md(payload))
