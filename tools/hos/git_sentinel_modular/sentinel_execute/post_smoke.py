from pathlib import Path
import ast

from .path_guard import resolve_target_path

def run_post_execution_smoke(target_root, execution_result, policy):
    target_root = Path(target_root)
    failures = []
    warnings = []
    checks = []

    for item in execution_result.get("applied", []):
        relpath = item["path"]
        action = item["action"]
        target = resolve_target_path(target_root, relpath)

        if action in ("add", "update"):
            exists = target.exists() and target.is_file()
            checks.append({
                "name": f"exists:{relpath}",
                "ok": exists,
                "detail": str(target),
            })
            if not exists:
                failures.append(f"target_missing_after_apply:{relpath}")
                continue

            if target.suffix.lower() == ".py" and policy.get("verify_python_parse_after_apply", True):
                ok, detail = _python_parse_check(target)
                checks.append({
                    "name": f"python_parse:{relpath}",
                    "ok": ok,
                    "detail": detail,
                })
                if not ok:
                    failures.append(f"python_parse_failed_after_apply:{relpath}")

        elif action == "delete":
            if target.exists():
                warnings.append(f"delete_not_confirmed_on_disk:{relpath}")

    return {
        "ok": len(failures) == 0,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "checks": checks,
        "counts": {
            "failures": len(set(failures)),
            "warnings": len(set(warnings)),
            "checks": len(checks),
        },
    }

def _python_parse_check(path):
    try:
        source = Path(path).read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        return True, "parsed"
    except Exception as exc:
        return False, str(exc)
