from pathlib import Path
import ast

def run_smoke_checks(workspace_root, preflight_payload, policy):
    workspace_root = Path(workspace_root)
    candidate_dir = workspace_root / "candidate"
    baseline_dir = workspace_root / "baseline"

    diff = preflight_payload["diff_manifest"]
    touched = sorted(set(diff.get("added", []) + diff.get("changed", []) + diff.get("removed", [])))

    failures = []
    warnings = []
    checks = []

    checks.append(_check_dir_exists(candidate_dir, "candidate_dir_exists"))
    checks.append(_check_dir_exists(baseline_dir, "baseline_dir_exists"))

    blocked_suffixes = {s.lower() for s in policy.get("blocked_suffixes", [])}
    blocked_parts = set(policy.get("blocked_path_parts", []))

    for relpath in touched:
        parts = Path(relpath).parts
        if any(part in blocked_parts for part in parts):
            failures.append(f"blocked_path_part:{relpath}")
        if Path(relpath).suffix.lower() in blocked_suffixes:
            failures.append(f"blocked_suffix:{relpath}")

    removed = diff.get("removed", [])
    if policy.get("fail_on_removed_legacy", True):
        for relpath in removed:
            if str(relpath).replace("\\", "/").startswith("legacy/"):
                failures.append(f"removed_legacy_path:{relpath}")

    for relpath in diff.get("added", []) + diff.get("changed", []):
        candidate_file = candidate_dir / relpath
        if not candidate_file.exists():
            failures.append(f"candidate_missing:{relpath}")
            continue
        if candidate_file.suffix.lower() == ".py" and policy.get("require_python_parse_for_changed_py", True):
            ok, msg = _python_parse_check(candidate_file)
            checks.append({
                "name": f"python_parse:{relpath}",
                "ok": ok,
                "detail": msg,
            })
            if not ok:
                failures.append(f"python_parse_failed:{relpath}")

    for relpath in diff.get("removed", []) + diff.get("changed", []):
        baseline_file = baseline_dir / relpath
        if not baseline_file.exists():
            warnings.append(f"baseline_missing:{relpath}")

    return {
        "ok": len(failures) == 0,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "checks": checks,
        "counts": {
            "touched_paths": len(touched),
            "failures": len(set(failures)),
            "warnings": len(set(warnings)),
            "checks": len(checks),
        },
    }

def _check_dir_exists(path, name):
    exists = Path(path).exists()
    return {
        "name": name,
        "ok": exists,
        "detail": str(path),
    }

def _python_parse_check(path):
    try:
        source = Path(path).read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        return True, "parsed"
    except Exception as exc:
        return False, str(exc)
