def build_rollback_manifest(preflight_payload):
    diff = preflight_payload["diff_manifest"]

    actions = []

    for relpath in diff.get("added", []):
        actions.append({
            "action": "remove_candidate_addition",
            "path": relpath,
            "source_of_truth": "baseline_absent",
        })

    for relpath in diff.get("removed", []):
        actions.append({
            "action": "restore_from_baseline",
            "path": relpath,
            "source_of_truth": "baseline",
        })

    for relpath in diff.get("changed", []):
        actions.append({
            "action": "restore_from_baseline",
            "path": relpath,
            "source_of_truth": "baseline",
        })

    return {
        "mode": "manual_only",
        "actions": actions,
        "counts": {
            "actions": len(actions),
            "added": len(diff.get("added", [])),
            "removed": len(diff.get("removed", [])),
            "changed": len(diff.get("changed", [])),
        },
        "notes": [
            "Rollback manifest describes how to revert candidate state back to baseline.",
            "This bundle never performs rollback automatically.",
        ],
    }
