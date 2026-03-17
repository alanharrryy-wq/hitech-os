from pathlib import Path

def build_rollback_instructions(plan_payload, execution_result, backup_manifest=None):
    actions = []

    if backup_manifest:
        for relpath in backup_manifest.get("copied", []):
            actions.append({
                "action": "restore_from_backup",
                "path": relpath,
            })

    for item in execution_result.get("applied", []):
        if item["action"] == "add":
            actions.append({
                "action": "remove_applied_addition",
                "path": item["path"],
            })

    return {
        "mode": "manual_only",
        "actions": actions,
        "counts": {
            "actions": len(actions),
        },
        "notes": [
            "Rollback instructions describe manual recovery steps.",
            "This bundle does not auto-rollback.",
        ],
    }
