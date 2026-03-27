from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .decision import evaluate_promotion_decision
from .manifest_io import write_json, write_text
from .policy_loader import default_policy, load_policy

def _markdown_report(payload: dict[str, Any]) -> str:
    return (
        "# Promotion bundle\n\n"
        f"Status: {payload['status']}\n\n"
        f"Reviewers: {', '.join(payload['reviewers'])}\n"
    )

def _reviewer_assignment_md(reviewers: list[str]) -> str:
    return "# Reviewers\n\n" + "\n".join(f"- {name}" for name in reviewers)

def build_promotion_bundle(
    workspace_root: str | Path,
    diff_manifest: dict[str, Any] | None = None,
    apply_result: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace = Path(workspace_root)
    if diff_manifest is None:
        diff_manifest = json.loads((workspace / "metadata" / "diff_manifest.json").read_text(encoding="utf-8"))
    payload = evaluate_promotion_decision(diff_manifest, apply_result, policy=policy or default_policy())
    review_dir = workspace / payload["review_dir_name"]
    review_dir.mkdir(parents=True, exist_ok=True)
    write_json(review_dir / "promotion_decision.json", payload)
    write_text(review_dir / "promotion_summary.md", _markdown_report(payload))
    write_text(review_dir / "reviewers.md", _reviewer_assignment_md(payload["reviewers"]))
    return {
        "review_dir": str(review_dir),
        "reviewers": payload["reviewers"],
        "status": payload["status"],
    }
