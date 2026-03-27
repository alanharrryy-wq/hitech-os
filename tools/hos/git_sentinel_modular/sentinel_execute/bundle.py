from __future__ import annotations

from pathlib import Path

from .backup import create_backup
from .executor import execute_plan
from .plan import build_execution_plan
from .policy_loader import default_policy
from .post_smoke import run_post_execution_smoke
from .report import write_execution_reports
from .rollback import build_rollback_instructions
from .workspace import load_workspace_context

def _final_status(result: dict) -> str:
    return result["status"]

def build_execution_bundle(
    workspace_root: str | Path,
    target_root: str | Path,
    policy: dict | None = None,
    *,
    plan_only: bool = True,
) -> dict:
    context = load_workspace_context(workspace_root)
    plan = build_execution_plan(context["diff_manifest"], target_root, context["candidate_root"], policy=policy or default_policy())
    execution_dir = Path(workspace_root) / "execution_bundle"
    execution_dir.mkdir(parents=True, exist_ok=True)
    backup_dir = create_backup(target_root, execution_dir)
    rollback = build_rollback_instructions(str(backup_dir), str(target_root))
    payload = {
        "execution_dir": str(execution_dir),
        "blocked": plan["blocked"],
        "planned_actions": len(plan["actions"]),
        "counts": plan["counts"],
        "rollback": rollback,
        "mode": "plan_only" if plan_only else "execute",
    }
    write_execution_reports(execution_dir, {
        "status": "planned_only" if plan_only else "ready_to_execute",
        "counts": {"planned_actions": len(plan["actions"])},
    })
    return payload

def execute_manual_promotion(
    workspace_root: str | Path,
    target_root: str | Path,
    *,
    do_execute: bool = False,
    confirm_token: str | None = None,
) -> dict:
    if do_execute and confirm_token != "EXECUTE_MANUAL_PROMOTION":
        raise ValueError("Missing or invalid confirm token.")
    context = load_workspace_context(workspace_root)
    execution_dir = Path(workspace_root) / "execution_bundle"
    execution_dir.mkdir(parents=True, exist_ok=True)
    plan = build_execution_plan(context["diff_manifest"], target_root, context["candidate_root"], policy=default_policy())
    result = execute_plan(plan, target_root, do_execute=do_execute)
    smoke = run_post_execution_smoke(target_root) if do_execute else {"status": "skipped"}
    payload = {
        "status": _final_status(result),
        "mode": "manual_execute" if do_execute else "dry_run",
        "run_id": Path(workspace_root).name,
        "target_root": str(target_root),
        "execution_dir": str(execution_dir),
        "counts": {
            "planned_actions": len(plan["actions"]),
            "applied": result["applied"],
            "post_smoke_failures": 0 if smoke["status"] in {"ok", "skipped"} else 1,
            "post_smoke_warnings": 0,
        },
    }
    write_execution_reports(execution_dir, payload)
    return payload
