from pathlib import Path

from .path_guard import assert_safe_relpath, is_protected_path
from .workspace import load_workspace_context

def build_execution_plan(workspace_root, target_root, policy):
    ctx = load_workspace_context(workspace_root)
    diff = ctx["diff_manifest"]
    cutover = ctx["cutover_summary"]
    promotion_review = ctx["promotion_review"]

    cutover_status = cutover.get("status")
    allowed_status = set(policy.get("cutover_status_allowed_for_execution", []))
    if cutover_status not in allowed_status:
        raise RuntimeError(
            f"Cutover status does not allow execution: {cutover_status}; allowed={sorted(allowed_status)}"
        )

    decision = promotion_review.get("decision", {})
    reviewers = decision.get("reviewers", [])

    actions = []
    blocked = []
    warnings = []

    for relpath in sorted(diff.get("added", [])):
        _append_action(actions, blocked, warnings, relpath, "add", ctx, policy)

    for relpath in sorted(diff.get("changed", [])):
        _append_action(actions, blocked, warnings, relpath, "update", ctx, policy)

    for relpath in sorted(diff.get("removed", [])):
        _append_action(actions, blocked, warnings, relpath, "delete", ctx, policy)

    return {
        "workspace_root": str(ctx["workspace_root"]),
        "target_root": str(Path(target_root)),
        "run_id": ctx["run_manifest"].get("run_id"),
        "cutover_status": cutover_status,
        "reviewers": reviewers,
        "actions": actions,
        "blocked": blocked,
        "warnings": warnings,
        "counts": {
            "actions": len(actions),
            "blocked": len(blocked),
            "warnings": len(warnings),
            "adds": len([x for x in actions if x["action"] == "add"]),
            "updates": len([x for x in actions if x["action"] == "update"]),
            "deletes": len([x for x in actions if x["action"] == "delete"]),
        },
    }

def _append_action(actions, blocked, warnings, relpath, action, ctx, policy):
    relpath = assert_safe_relpath(relpath, policy)

    if is_protected_path(relpath, policy):
        blocked.append({
            "path": relpath,
            "reason": "protected_prefix_block",
            "action": action,
        })
        return

    candidate_path = ctx["candidate_dir"] / relpath
    baseline_path = ctx["baseline_dir"] / relpath

    if action in ("add", "update"):
        if not candidate_path.exists():
            blocked.append({
                "path": relpath,
                "reason": "candidate_missing_for_apply",
                "action": action,
            })
            return
        source_path = candidate_path
    else:
        source_path = baseline_path if baseline_path.exists() else None

    if action == "delete" and not policy.get("allow_delete", False):
        warnings.append({
            "path": relpath,
            "reason": "delete_requested_but_policy_disallows_delete",
            "action": action,
        })
        blocked.append({
            "path": relpath,
            "reason": "delete_not_allowed",
            "action": action,
        })
        return

    actions.append({
        "path": relpath,
        "action": action,
        "candidate_exists": candidate_path.exists(),
        "baseline_exists": baseline_path.exists(),
        "source_path": str(source_path) if source_path else None,
    })
