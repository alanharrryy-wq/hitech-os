from pathlib import Path
import json

def _write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def _write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

def build_review_pack(workspace, apply_result, finalize_result):
    apply_manifest = apply_result["manifest"]
    diff_payload = finalize_result["diff"]
    gate_payload = finalize_result["gate"]

    review_payload = {
        "run_id": workspace.run_id,
        "workspace_root": str(workspace.root),
        "candidate_dir": str(workspace.candidate_dir),
        "apply_counts": apply_manifest["counts"],
        "diff_counts": diff_payload["counts"],
        "gate": gate_payload,
        "top_changed_files": diff_payload["changed"][:25],
        "top_added_files": diff_payload["added"][:25],
        "top_removed_files": diff_payload["removed"][:25],
    }

    review_json_path = Path(workspace.manifests_dir) / "review_pack.json"
    _write_json(review_json_path, review_payload)

    md = []
    md.append(f"# Shadow Review Pack | {workspace.run_id}")
    md.append("")
    md.append("## Apply counts")
    md.append(f"- applied: {apply_manifest['counts']['applied']}")
    md.append(f"- skipped: {apply_manifest['counts']['skipped']}")
    md.append(f"- rejected: {apply_manifest['counts']['rejected']}")
    md.append("")
    md.append("## Diff counts")
    md.append(f"- added: {diff_payload['counts']['added']}")
    md.append(f"- removed: {diff_payload['counts']['removed']}")
    md.append(f"- changed: {diff_payload['counts']['changed']}")
    md.append(f"- total_touched: {diff_payload['counts']['total_touched']}")
    md.append("")
    md.append("## Promotion gate")
    md.append(f"- allowed: {gate_payload['allowed']}")
    md.append(f"- promotion_mode: {gate_payload['promotion_mode']}")
    md.append("")
    if gate_payload.get("violations"):
        md.append("## Violations")
        for item in gate_payload["violations"][:50]:
            md.append(f"- {item['type']}: {item['path']}")
        md.append("")
    if diff_payload.get("changed"):
        md.append("## Changed files")
        for item in diff_payload["changed"][:50]:
            md.append(f"- {item}")
        md.append("")

    review_md_path = Path(workspace.manifests_dir) / "review_pack.md"
    _write_text(review_md_path, "\n".join(md) + "\n")

    return {
        "review_json_path": review_json_path,
        "review_md_path": review_md_path,
        "review": review_payload,
    }
