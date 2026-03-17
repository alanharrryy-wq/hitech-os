def build_cutover_checklist(summary_payload):
    lines = []
    lines.append(f"# Cutover Checklist | {summary_payload.get('run_id', 'unknown')}")
    lines.append("")
    lines.append(f"- [ ] Confirm status is acceptable for manual cutover: `{summary_payload['status']}`")
    lines.append("- [ ] Confirm promotion remains manual_only")
    lines.append("- [ ] Review promotion blockers and warnings")
    lines.append("- [ ] Review smoke failures and warnings")
    lines.append("- [ ] Review rollback manifest and make sure recovery path is understood")
    lines.append("- [ ] Review critical paths touched")
    lines.append("- [ ] Review reviewers / owners assigned")
    lines.append("- [ ] Approve or reject cutover manually")
    lines.append("")
    lines.append("## Decision summary")
    lines.append(f"- status: {summary_payload['status']}")
    lines.append(f"- cutover_mode: {summary_payload['cutover_mode']}")
    lines.append(f"- overall_risk: {summary_payload['overall_risk']}")
    lines.append("")
    if summary_payload.get("blockers"):
        lines.append("## Blockers")
        for item in summary_payload["blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    if summary_payload.get("attention_items"):
        lines.append("## Attention items")
        for item in summary_payload["attention_items"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("## Reviewers")
    for reviewer in summary_payload.get("reviewers", []):
        lines.append(f"- {reviewer}")
    if not summary_payload.get("reviewers"):
        lines.append("- none")
    lines.append("")
    return "\n".join(lines) + "\n"
