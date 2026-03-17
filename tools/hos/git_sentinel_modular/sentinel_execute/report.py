from pathlib import Path

from .manifest_io import write_json, write_text

def write_execution_reports(execution_dir, plan_payload, execution_result, post_smoke_payload, rollback_payload):
    execution_dir = Path(execution_dir)
    write_json(execution_dir / "execution_plan.json", plan_payload)
    write_json(execution_dir / "execution_result.json", execution_result)
    write_json(execution_dir / "post_smoke.json", post_smoke_payload)
    write_json(execution_dir / "rollback_instructions.json", rollback_payload)
    write_text(execution_dir / "execution_summary.md", _summary_md(plan_payload, execution_result, post_smoke_payload, rollback_payload))

    return {
        "plan_path": execution_dir / "execution_plan.json",
        "result_path": execution_dir / "execution_result.json",
        "post_smoke_path": execution_dir / "post_smoke.json",
        "rollback_path": execution_dir / "rollback_instructions.json",
        "summary_md_path": execution_dir / "execution_summary.md",
    }

def _summary_md(plan_payload, execution_result, post_smoke_payload, rollback_payload):
    lines = []
    lines.append(f"# Manual Promotion Execution Summary | {plan_payload.get('run_id', 'unknown')}")
    lines.append("")
    lines.append("## Plan counts")
    for key, value in plan_payload.get("counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Execution")
    lines.append(f"- mode: {execution_result.get('mode')}")
    lines.append(f"- ok: {execution_result.get('ok')}")
    lines.append(f"- applied: {execution_result.get('counts', {}).get('applied', 0)}")
    lines.append(f"- skipped: {execution_result.get('counts', {}).get('skipped', 0)}")
    lines.append(f"- blocked: {execution_result.get('counts', {}).get('blocked', 0)}")
    lines.append("")
    lines.append("## Post smoke")
    lines.append(f"- ok: {post_smoke_payload.get('ok')}")
    lines.append(f"- failures: {post_smoke_payload.get('counts', {}).get('failures', 0)}")
    lines.append(f"- warnings: {post_smoke_payload.get('counts', {}).get('warnings', 0)}")
    lines.append("")
    lines.append("## Rollback")
    lines.append(f"- mode: {rollback_payload.get('mode')}")
    lines.append(f"- actions: {rollback_payload.get('counts', {}).get('actions', 0)}")
    lines.append("")
    if execution_result.get("blocked"):
        lines.append("## Blocked items")
        for item in execution_result["blocked"][:100]:
            lines.append(f"- {item['reason']}: {item['path']}")
        lines.append("")
    if execution_result.get("applied"):
        lines.append("## Applied items")
        for item in execution_result["applied"][:100]:
            lines.append(f"- {item['action']}: {item['path']}")
        lines.append("")
    if post_smoke_payload.get("failures"):
        lines.append("## Post smoke failures")
        for item in post_smoke_payload["failures"][:100]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines) + "\n"
