from __future__ import annotations

import pathlib
from datetime import datetime, timezone

from .constants import MAX_IMMEDIATE_ACTIONS, STATUS_OK


def build_meta_report(
    run_id: str,
    timestamp_iso: str,
    timezone_name: str,
    federation_status: str,
    repos: list[dict],
    blockers: dict,
    debt_summary: dict,
) -> str:
    lines: list[str] = []
    lines.append("# META_REPORT")
    lines.append("")
    lines.append("## Run Info")
    lines.append("")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- timestamp_iso: `{timestamp_iso}`")
    lines.append(f"- timezone: `{timezone_name}`")
    lines.append("")
    lines.append("## Federation Status")
    lines.append("")
    lines.append(f"- status: `{federation_status}`")
    lines.append(f"- generated_at: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`")
    lines.append("")
    lines.append("## Repos")
    lines.append("")
    lines.append("| repo | online | status | docs_doctor | report_path |")
    lines.append("|---|---:|---|---|---|")
    for repo in sorted(repos, key=lambda r: r["name"].lower()):
        lines.append(
            "| {name} | {online} | {status} | {doctor} | {report} |".format(
                name=repo["name"],
                online=str(repo["online"]).lower(),
                status=repo["status"],
                doctor=repo["docs_doctor"]["result"],
                report=repo["docs_doctor"]["report_path"],
            )
        )
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    lines.append("### Constitutional")
    lines.extend(_as_bullets(blockers.get("constitutional", [])))
    lines.append("")
    lines.append("### Policy")
    lines.extend(_as_bullets(blockers.get("policy", [])))
    lines.append("")
    lines.append("### Tooling")
    lines.extend(_as_bullets(blockers.get("tooling", [])))
    lines.append("")
    lines.append("## Debt Summary")
    lines.append("")
    totals = debt_summary.get("totals", {})
    for key in sorted(totals):
        lines.append(f"- {key}: {totals[key]}")
    lines.append("")
    lines.append("## Immediate Next Actions")
    lines.append("")
    actions = build_immediate_actions(federation_status, blockers, repos)
    if actions:
        for idx, action in enumerate(actions[:MAX_IMMEDIATE_ACTIONS], start=1):
            lines.append(f"{idx}. {action}")
    else:
        lines.append("1. No immediate action required.")
    lines.append("")
    lines.append("## Appendix: Repo Excerpts")
    lines.append("")
    for repo in sorted(repos, key=lambda r: r["name"].lower()):
        lines.append(f"### {repo['name']}")
        excerpt = repo.get("last_report_excerpt", [])
        if not excerpt:
            lines.append("- No report excerpt available.")
        else:
            lines.append("```md")
            lines.extend(excerpt)
            lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _as_bullets(items: list[str]) -> list[str]:
    if not items:
        return ["- none"]
    return [f"- {item}" for item in sorted(items)]


def build_immediate_actions(federation_status: str, blockers: dict, repos: list[dict]) -> list[str]:
    actions: list[str] = []
    if federation_status == STATUS_OK:
        actions.append("Continue normal governance operations; federation is healthy.")
        return actions
    if blockers.get("constitutional"):
        actions.append("Resolve constitutional blockers in online repos before any convergence actions.")
    if blockers.get("tooling"):
        actions.append("Restore missing tooling (Docs-Doctor / reports) for degraded repositories.")
    if blockers.get("policy"):
        actions.append("Address policy blockers and rerun federation orchestration.")
    offline = [repo["name"] for repo in repos if not repo["online"]]
    if offline:
        actions.append("Bring OFFLINE repos online or keep strict mode disabled for non-blocking execution.")
    actions.append("Re-run `python -m tools.meta.meta_orchestrator --registry docs/meta-gov/REPO_REGISTRY.yaml --write`.")
    dedup: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if action not in seen:
            seen.add(action)
            dedup.append(action)
    return dedup
