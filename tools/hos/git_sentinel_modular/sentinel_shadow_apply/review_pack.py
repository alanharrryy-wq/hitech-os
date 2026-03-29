from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def _write_text(path: str | Path, content: str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")
    return target

def _write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target

def build_review_pack(
    workspace_root: str | Path,
    diff_manifest: dict[str, Any],
    apply_result: dict[str, Any],
    gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace = Path(workspace_root)
    review_dir = workspace / "review_bundle"
    review_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "status": gate.get("status", "needs_review") if gate else "needs_review",
        "counts": diff_manifest.get("counts", {}),
        "apply_manifest": apply_result.get("manifest", apply_result),
        "gate": gate or {},
    }
    _write_json(review_dir / "review_summary.json", summary)
    _write_text(
        review_dir / "review_summary.md",
        f"# Review bundle\n\nStatus: {summary['status']}\n\nCounts: {summary['counts']}\n",
    )
    return {"review_dir": str(review_dir), "status": summary["status"]}
