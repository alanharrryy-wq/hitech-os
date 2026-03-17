from pathlib import Path

from .decision import evaluate_promotion_decision
from .manifest_io import read_json, write_json, write_text
from .policy_loader import load_policy

def _markdown_report(run_manifest, apply_manifest, diff_manifest, gate_manifest, decision):
    lines = []
    lines.append(f"# Promotion Review Bundle | {run_manifest.get('run_id', 'unknown')}")
    lines.append("")
    lines.append("## Decision")
    lines.append(f"- status: {decision['status']}")
    lines.append(f"- promotion_mode: {decision['promotion_mode']}")
    lines.append(f"- reviewers: {', '.join(decision['reviewers']) if decision['reviewers'] else 'none'}")
    lines.append("")
    lines.append("## Counts")
    lines.append(f"- applied: {apply_manifest.get('counts', {}).get('applied', 0)}")
    lines.append(f"- skipped: {apply_manifest.get('counts', {}).get('skipped', 0)}")
    lines.append(f"- rejected: {apply_manifest.get('counts', {}).get('rejected', 0)}")
    lines.append(f"- added: {diff_manifest.get('counts', {}).get('added', 0)}")
    lines.append(f"- removed: {diff_manifest.get('counts', {}).get('removed', 0)}")
    lines.append(f"- changed: {diff_manifest.get('counts', {}).get('changed', 0)}")
    lines.append(f"- total_touched: {diff_manifest.get('counts', {}).get('total_touched', 0)}")
    lines.append("")
    lines.append("## Blocked reasons")
    if decision["blocked_reasons"]:
        for item in decision["blocked_reasons"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Warnings")
    if decision["warnings"]:
        for item in decision["warnings"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Reviewers")
    if decision["reviewers"]:
        for reviewer in decision["reviewers"]:
            lines.append(f"- {reviewer}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Touched paths")
    for item in decision["touched_paths"][:100]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Upstream promotion gate")
    lines.append(f"- allowed: {gate_manifest.get('allowed', False)}")
    lines.append(f"- promotion_mode: {gate_manifest.get('promotion_mode', 'unknown')}")
    for note in gate_manifest.get("notes", []):
        lines.append(f"- note: {note}")
    lines.append("")
    return "\n".join(lines) + "\n"

def _reviewer_assignment_md(decision):
    lines = []
    lines.append("# Reviewer Assignment")
    lines.append("")
    lines.append(f"- status: {decision['status']}")
    lines.append(f"- promotion_mode: {decision['promotion_mode']}")
    lines.append("")
    if decision["reviewers"]:
        lines.append("## Assigned reviewers")
        for reviewer in decision["reviewers"]:
            lines.append(f"- {reviewer}")
    else:
        lines.append("## Assigned reviewers")
        lines.append("- none")
    lines.append("")
    lines.append("## Why")
    if decision["blocked_reasons"]:
        for item in decision["blocked_reasons"]:
            lines.append(f"- blocked: {item}")
    if decision["warnings"]:
        for item in decision["warnings"]:
            lines.append(f"- warning: {item}")
    if not decision["blocked_reasons"] and not decision["warnings"]:
        lines.append("- no special conditions triggered")
    lines.append("")
    return "\n".join(lines) + "\n"

def build_promotion_bundle(workspace_root, policy_path=None):
    workspace_root = Path(workspace_root)
    manifests_dir = workspace_root / "manifests"
    review_dir = workspace_root / "review_bundle"

    run_manifest = read_json(manifests_dir / "run_manifest.json")
    apply_manifest = read_json(manifests_dir / "apply_manifest.json")
    diff_manifest = read_json(manifests_dir / "diff_manifest.json")
    gate_manifest = read_json(manifests_dir / "promotion_gate.json")
    policy = load_policy(policy_path)

    decision = evaluate_promotion_decision(
        diff_payload=diff_manifest,
        gate_payload=gate_manifest,
        apply_payload=apply_manifest,
        policy=policy,
    )

    evidence_index = {
        "run_manifest": str(manifests_dir / "run_manifest.json"),
        "apply_manifest": str(manifests_dir / "apply_manifest.json"),
        "diff_manifest": str(manifests_dir / "diff_manifest.json"),
        "promotion_gate": str(manifests_dir / "promotion_gate.json"),
        "policy_path": str(policy_path) if policy_path else "default_policy",
        "workspace_root": str(workspace_root),
        "review_bundle_dir": str(review_dir),
    }

    review_payload = {
        "decision": decision,
        "evidence_index": evidence_index,
        "source_counts": {
            "apply": apply_manifest.get("counts", {}),
            "diff": diff_manifest.get("counts", {}),
        },
    }

    reviewer_assignment = {
        "status": decision["status"],
        "promotion_mode": decision["promotion_mode"],
        "reviewers": decision["reviewers"],
        "blocked_reasons": decision["blocked_reasons"],
        "warnings": decision["warnings"],
    }

    write_json(review_dir / "promotion_review.json", review_payload)
    write_text(
        review_dir / "promotion_review.md",
        _markdown_report(run_manifest, apply_manifest, diff_manifest, gate_manifest, decision),
    )
    write_json(review_dir / "reviewer_assignment.json", reviewer_assignment)
    write_text(
        review_dir / "reviewer_assignment.md",
        _reviewer_assignment_md(decision),
    )
    write_json(review_dir / "evidence_index.json", evidence_index)

    return {
        "review_dir": review_dir,
        "promotion_review_json": review_dir / "promotion_review.json",
        "promotion_review_md": review_dir / "promotion_review.md",
        "reviewer_assignment_json": review_dir / "reviewer_assignment.json",
        "reviewer_assignment_md": review_dir / "reviewer_assignment.md",
        "evidence_index_json": review_dir / "evidence_index.json",
        "decision": decision,
    }
