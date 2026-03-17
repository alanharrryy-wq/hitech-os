from pathlib import Path
import time

from .executor import execute_plan
from .manifest_io import write_json
from .plan import build_execution_plan
from .policy_loader import load_policy
from .post_smoke import run_post_execution_smoke
from .report import write_execution_reports
from .rollback import build_rollback_instructions
from .target_snapshot import snapshot_target_paths

def build_execution_bundle(workspace_root, target_root, policy_path=None):
    policy = load_policy(policy_path)
    plan_payload = build_execution_plan(workspace_root, target_root, policy)

    workspace_root = Path(workspace_root)
    execution_dir = workspace_root / policy.get("execution_dir_name", "execution_bundle")
    execution_dir.mkdir(parents=True, exist_ok=True)

    touched = [x["path"] for x in plan_payload.get("actions", [])]
    pre_snapshot = snapshot_target_paths(target_root, touched)
    write_json(execution_dir / "target_snapshot.before.json", pre_snapshot)
    write_json(execution_dir / "execution_plan.json", plan_payload)

    return {
        "execution_dir": execution_dir,
        "plan_payload": plan_payload,
        "pre_snapshot": pre_snapshot,
    }

def execute_manual_promotion(workspace_root, target_root, policy_path=None, *, do_execute=False, confirm_token=None):
    policy = load_policy(policy_path)
    bundle = build_execution_bundle(workspace_root, target_root, policy_path=policy_path)

    execution_dir = bundle["execution_dir"]
    plan_payload = bundle["plan_payload"]

    execution_result, backup_manifest = execute_plan(
        plan_payload=plan_payload,
        target_root=target_root,
        execution_dir=execution_dir,
        policy=policy,
        do_execute=do_execute,
        confirm_token=confirm_token,
    )

    post_smoke_payload = run_post_execution_smoke(
        target_root=target_root,
        execution_result=execution_result,
        policy=policy,
    )

    rollback_payload = build_rollback_instructions(
        plan_payload=plan_payload,
        execution_result=execution_result,
        backup_manifest=backup_manifest,
    )

    post_snapshot = snapshot_target_paths(target_root, [x["path"] for x in plan_payload.get("actions", [])])
    write_json(execution_dir / "target_snapshot.after.json", post_snapshot)
    if backup_manifest is not None:
        write_json(execution_dir / "backup_manifest.copy.json", backup_manifest)

    report_paths = write_execution_reports(
        execution_dir=execution_dir,
        plan_payload=plan_payload,
        execution_result=execution_result,
        post_smoke_payload=post_smoke_payload,
        rollback_payload=rollback_payload,
    )

    summary = {
        "status": _final_status(execution_result, post_smoke_payload),
        "mode": execution_result.get("mode"),
        "run_id": plan_payload.get("run_id"),
        "target_root": str(Path(target_root)),
        "execution_dir": str(execution_dir),
        "counts": {
            "planned_actions": plan_payload.get("counts", {}).get("actions", 0),
            "applied": execution_result.get("counts", {}).get("applied", 0),
            "post_smoke_failures": post_smoke_payload.get("counts", {}).get("failures", 0),
            "post_smoke_warnings": post_smoke_payload.get("counts", {}).get("warnings", 0),
        },
    }
    write_json(execution_dir / "execution_summary.json", summary)

    return {
        "execution_dir": execution_dir,
        "summary": summary,
        "report_paths": report_paths,
    }

def _final_status(execution_result, post_smoke_payload):
    if execution_result.get("mode") == "blocked_before_execution":
        return "blocked"
    if post_smoke_payload.get("failures"):
        return "needs_attention"
    if execution_result.get("mode") == "dry_run":
        return "planned_only"
    return "executed"
