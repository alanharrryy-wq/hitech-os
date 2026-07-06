from __future__ import annotations

import json
from pathlib import Path
import datetime as dt
import re

def _write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def _write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")

def _count_validation_failures(validations):
    return len([x for x in validations or [] if x.get("ok") is False])

def write_plan_dashboard(report: Path, plan: dict, noise_summary: dict | None = None, validations: list | None = None):
    blockers = plan.get("blockers") or []
    warnings = plan.get("warnings") or []
    groups = plan.get("commit_groups") or []
    decision = "BLOCKED" if blockers else "APPLY_READY"
    state = {
        "schema": "autogit.ag98_dashboard.v1",
        "kind": "plan",
        "created_at": dt.datetime.now().isoformat(),
        "decision": decision,
        "plan_id": plan.get("plan_id"),
        "head": plan.get("head"),
        "branch": plan.get("branch"),
        "blockers": len(blockers),
        "warnings": len(warnings),
        "validation_failures": _count_validation_failures(validations),
        "commit_groups": [{"group": g.get("group"), "files": len(g.get("paths") or []), "message": g.get("message")} for g in groups],
        "runtime_excluded": len((noise_summary or {}).get("excluded") or []),
        "next": "Run apply-plan with this AUTOGIT_PLAN.lock.json" if not blockers else "Resolve blockers and regenerate plan",
    }
    _write_json(report / "MACHINE_STATE.json", state)
    md = ["# AutoGit 98 Dashboard", "", f"Decision: `{decision}`", "", f"Plan ID: `{plan.get('plan_id')}`", f"Blockers: `{len(blockers)}`", f"Warnings: `{len(warnings)}`", f"Runtime/generated exclusions: `{state['runtime_excluded']}`", "", "## Commit groups"]
    for g in state["commit_groups"]:
        md.append(f"- `{g['group']}`: {g['files']} files · {g['message']}")
    if (noise_summary or {}).get("excluded"):
        md.append("\n## Excluded safe runtime/generated noise")
        for x in (noise_summary or {}).get("excluded", [])[:80]:
            md.append(f"- `{x.get('path')}` · {x.get('kind')}: {x.get('detail')}")
    md.append("\n## Next")
    md.append(state["next"])
    _write_text(report / "HUMAN_SUMMARY.md", "\n".join(md) + "\n")
    _write_text(report / "AG98_DASHBOARD.md", "\n".join(md) + "\n")

def parse_checks_text(stdout: str, stderr: str = "") -> dict:
    rows = []
    text = (stdout or "") + "\n" + (stderr or "")
    for line in text.splitlines():
        raw = line.strip()
        if not raw or raw.lower().startswith("refreshing"):
            continue
        parts = re.split(r"\s{2,}|\t+", raw)
        if len(parts) >= 2:
            rows.append({"name": parts[0], "state": parts[1], "raw": line})
    failures = [r for r in rows if r.get("state", "").lower() in {"fail", "failure", "cancelled", "timed_out", "timed-out"}]
    pending = [r for r in rows if r.get("state", "").lower() in {"pending", "queued", "in_progress", "waiting"}]
    return {"rows": rows, "failures": failures, "pending": pending, "ok": not failures and not pending}

def write_ci_decision(report: Path, stdout: str, stderr: str, returncode: int, context: str = "pr_checks"):
    parsed = parse_checks_text(stdout, stderr)
    decision = {
        "schema": "autogit.ag98_ci_decision.v1",
        "context": context,
        "created_at": dt.datetime.now().isoformat(),
        "returncode": returncode,
        "ok": returncode == 0 or "no checks" in ((stdout or "") + (stderr or "")).lower(),
        "parsed": parsed,
        "merge_allowed": (returncode == 0 and not parsed.get("failures") and not parsed.get("pending")),
    }
    if "no checks" in ((stdout or "") + (stderr or "")).lower():
        decision["merge_allowed"] = False
        decision["requires_explicit_allow_merge_no_checks"] = True
    _write_json(report / "CI_DECISION.json", decision)
    lines = ["# CI Decision", "", f"Context: `{context}`", f"Return code: `{returncode}`", f"Merge allowed: `{decision['merge_allowed']}`", "", "## Checks"]
    for r in parsed.get("rows", [])[:100]:
        lines.append(f"- `{r.get('name')}`: `{r.get('state')}`")
    if parsed.get("failures"):
        lines.append("\n## Failures")
        for r in parsed["failures"]:
            lines.append(f"- `{r.get('name')}`: `{r.get('raw')}`")
    _write_text(report / "CI_DECISION.md", "\n".join(lines) + "\n")

def write_apply_dashboard(report: Path, summary: dict):
    state = {
        "schema": "autogit.ag98_dashboard.v1",
        "kind": "apply",
        "created_at": dt.datetime.now().isoformat(),
        "decision": "PR_READY" if summary.get("pr") and not summary.get("merged") else "APPLY_DONE",
        "branch": summary.get("branch"),
        "created_commits": len(summary.get("created_commits") or []),
        "pr": summary.get("pr"),
        "checks": summary.get("checks"),
        "merged": summary.get("merged"),
    }
    _write_json(report / "MACHINE_STATE.json", state)
    md = ["# AutoGit 98 Apply Dashboard", "", f"Decision: `{state['decision']}`", f"Branch: `{state.get('branch')}`", f"Commits: `{state['created_commits']}`"]
    if summary.get("pr"):
        md.append(f"PR: `{summary['pr'].get('url')}`")
    if summary.get("checks"):
        md.append(f"Checks ok: `{summary['checks'].get('ok')}`")
    if summary.get("merged"):
        md.append(f"Merged: `{summary['merged'].get('ok')}`")
    _write_text(report / "HUMAN_SUMMARY.md", "\n".join(md) + "\n")
    _write_text(report / "AG98_DASHBOARD.md", "\n".join(md) + "\n")
