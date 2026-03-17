from pathlib import Path

from .manifest_io import write_json, write_text
from .policy_loader import load_policy
from .preflight import run_preflight
from .smoke import run_smoke_checks
from .matrix import build_risk_matrix
from .rollback import build_rollback_manifest
from .summary import evaluate_cutover_readiness
from .checklist import build_cutover_checklist

def build_cutover_readiness_bundle(workspace_root, policy_path=None):
    workspace_root = Path(workspace_root)
    bundle_dir = workspace_root / "cutover_bundle"
    policy = load_policy(policy_path)

    preflight_payload = run_preflight(workspace_root)
    if not preflight_payload["ok"]:
        smoke_payload = {
            "ok": False,
            "failures": ["preflight_failed"],
            "warnings": [],
            "checks": [],
            "counts": {"touched_paths": 0, "failures": 1, "warnings": 0, "checks": 0},
        }
        matrix_payload = {
            "overall_risk": "critical",
            "dimensions": {
                "scope": "critical",
                "smoke": "critical",
                "promotion_decision": "critical",
                "critical_paths": "critical",
            },
            "critical_hits": [],
            "counts": {"total_touched": 0, "critical_hits": 0, "smoke_failures": 1, "smoke_warnings": 0},
        }
        rollback_payload = {
            "mode": "manual_only",
            "actions": [],
            "counts": {"actions": 0, "added": 0, "removed": 0, "changed": 0},
            "notes": ["Preflight failed; rollback manifest not built from diff."],
        }
    else:
        smoke_payload = run_smoke_checks(workspace_root, preflight_payload, policy)
        matrix_payload = build_risk_matrix(preflight_payload, smoke_payload, policy)
        rollback_payload = build_rollback_manifest(preflight_payload)

    summary_payload = evaluate_cutover_readiness(
        preflight_payload=preflight_payload,
        smoke_payload=smoke_payload,
        matrix_payload=matrix_payload,
        policy=policy,
    )

    evidence_index = {
        "workspace_root": str(workspace_root),
        "bundle_dir": str(bundle_dir),
        "policy_path": str(policy_path) if policy_path else "default_policy",
        "source_manifests": {
            "run_manifest": str(workspace_root / "manifests" / "run_manifest.json"),
            "apply_manifest": str(workspace_root / "manifests" / "apply_manifest.json"),
            "diff_manifest": str(workspace_root / "manifests" / "diff_manifest.json"),
            "promotion_gate": str(workspace_root / "manifests" / "promotion_gate.json"),
            "promotion_review": str(workspace_root / "review_bundle" / "promotion_review.json"),
        },
    }

    write_json(bundle_dir / "preflight_report.json", preflight_payload)
    write_json(bundle_dir / "smoke_report.json", smoke_payload)
    write_json(bundle_dir / "risk_matrix.json", matrix_payload)
    write_json(bundle_dir / "rollback_manifest.json", rollback_payload)
    write_json(bundle_dir / "release_candidate_summary.json", summary_payload)
    write_text(bundle_dir / "release_candidate_summary.md", _summary_md(summary_payload, matrix_payload))
    write_text(bundle_dir / "cutover_checklist.md", build_cutover_checklist(summary_payload))
    write_json(bundle_dir / "evidence_index.json", evidence_index)

    return {
        "bundle_dir": bundle_dir,
        "summary_path": bundle_dir / "release_candidate_summary.json",
        "summary_md_path": bundle_dir / "release_candidate_summary.md",
        "checklist_path": bundle_dir / "cutover_checklist.md",
        "decision": summary_payload,
    }

def _summary_md(summary_payload, matrix_payload):
    lines = []
    lines.append(f"# Release Candidate Summary | {summary_payload.get('run_id', 'unknown')}")
    lines.append("")
    lines.append("## Status")
    lines.append(f"- status: {summary_payload['status']}")
    lines.append(f"- cutover_mode: {summary_payload['cutover_mode']}")
    lines.append(f"- overall_risk: {summary_payload['overall_risk']}")
    lines.append("")
    lines.append("## Counts")
    for k, v in summary_payload.get("counts", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Risk matrix")
    for k, v in matrix_payload.get("dimensions", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Blockers")
    if summary_payload["blockers"]:
        for item in summary_payload["blockers"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Attention items")
    if summary_payload["attention_items"]:
        for item in summary_payload["attention_items"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Reviewers")
    if summary_payload["reviewers"]:
        for item in summary_payload["reviewers"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines) + "\n"
