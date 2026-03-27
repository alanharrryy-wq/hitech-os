from __future__ import annotations

from pathlib import Path
import json

from .checklist import build_cutover_checklist
from .manifest_io import write_json, write_text
from .matrix import build_risk_matrix
from .preflight import run_preflight
from .rollback import build_rollback_manifest
from .smoke import run_smoke_checks
from .summary import evaluate_cutover_readiness

def _summary_md(payload: dict) -> str:
    return (
        "# Cutover readiness\n\n"
        f"Status: {payload['status']}\n\n"
        f"Overall risk: {payload['overall_risk']}\n"
    )

def build_cutover_readiness_bundle(workspace_root: str | Path, policy: dict | None = None) -> dict:
    workspace = Path(workspace_root)
    diff_manifest = json.loads((workspace / "metadata" / "diff_manifest.json").read_text(encoding="utf-8"))
    preflight = run_preflight(workspace)
    risk = build_risk_matrix(diff_manifest, policy=policy)
    smoke = run_smoke_checks(workspace)
    summary = evaluate_cutover_readiness(preflight, risk, smoke)
    rollback = build_rollback_manifest(workspace)
    bundle_dir = workspace / "cutover_bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    payload = {**summary, "preflight": preflight, "risk_matrix": risk, "rollback": rollback, "checklist": build_cutover_checklist()}
    write_json(bundle_dir / "cutover_summary.json", payload)
    write_text(bundle_dir / "cutover_summary.md", _summary_md(payload))
    return {
        "bundle_dir": str(bundle_dir),
        "overall_risk": payload["overall_risk"],
        "reviewers": ["platform", "repo-owner"],
        "status": payload["status"],
    }
