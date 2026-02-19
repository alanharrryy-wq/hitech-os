from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REQUIRED_WORKER_FILES: tuple[str, ...] = (
    "STATUS.json",
    "SUMMARY.md",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "SUGGESTIONS.md",
    "SCOPE_LOCK.json",
    "HANDOFF_NOTE.json",
    "LOGS/INDEX.json",
)

REQUIRED_INTEGRATOR_FILES: tuple[str, ...] = (
    "STATUS.json",
    "FINAL_REPORT.txt",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "MERGE_PLAN.md",
    "LOGS/INDEX.json",
)

ROLE_TO_WORKER: tuple[tuple[str, str], ...] = (
    ("A_core", "A_worker"),
    ("B_tooling", "B_worker"),
    ("C_features", "C_worker"),
    ("D_validation", "D_worker"),
    ("Z_integrator", "Z_integrator"),
)

TARGET_PACKAGES: tuple[str, ...] = (
    "packages/render-core",
    "packages/module-registry",
    "packages/desktop-bridge",
)

IGNORE_DIRS: tuple[str, ...] = (
    ".cache",
    ".turbo",
    "dist",
    "logs",
    "node_modules",
)

BUNDLE_ARTIFACT_BASENAMES: tuple[str, ...] = (
    "STATUS.json",
    "SUMMARY.md",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "SUGGESTIONS.md",
    "SCOPE_LOCK.json",
    "HANDOFF_NOTE.json",
    "INDEX.json",
)


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    rc: int
    stdout: str
    stderr: str
    error: str = ""


def _repo_root_from_script(script_path: Path) -> Path:
    current = script_path.resolve()
    if current.is_file():
        current = current.parent
    while True:
        if (current / ".git").exists() or (current / "KERNEL_CONTEXT.md").exists():
            return current
        if current.parent == current:
            raise RuntimeError("unable to resolve repo root (.git or KERNEL_CONTEXT.md not found)")
        current = current.parent


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(_read_text(path))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_command(command: list[str], cwd: Path) -> CommandResult:
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        return CommandResult(
            command=list(command),
            rc=int(proc.returncode),
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
        )
    except OSError as exc:
        return CommandResult(
            command=list(command),
            rc=127,
            stdout="",
            stderr="",
            error=str(exc),
        )


def _extract_last_json_object(text: str) -> Any | None:
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    stack: list[int] = []
    spans: list[tuple[int, int]] = []
    for idx, char in enumerate(text):
        if char == "{":
            stack.append(idx)
        elif char == "}" and stack:
            start = stack.pop()
            if not stack:
                spans.append((start, idx + 1))
    for start, end in reversed(spans):
        candidate = text[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _find_run_dir(runs_root: Path, run_id: str) -> Path | None:
    direct = runs_root / run_id
    if direct.exists():
        return direct
    target = run_id.lower()
    candidates = sorted(path for path in runs_root.glob("*") if path.is_dir())
    matches = [path for path in candidates if path.name.lower() == target]
    if len(matches) == 1:
        return matches[0]
    return None


def _status_excerpt(status_obj: Any) -> dict[str, Any]:
    if not isinstance(status_obj, dict):
        return {}
    required_checks = status_obj.get("required_checks", [])
    normalized_checks: list[dict[str, Any]] = []
    if isinstance(required_checks, list):
        for check in required_checks:
            if isinstance(check, dict):
                normalized_checks.append(
                    {
                        "name": str(check.get("name", "")),
                        "status": str(check.get("status", "")),
                        "rc": check.get("rc"),
                    }
                )
    normalized_checks.sort(key=lambda item: (item["name"], item["status"], str(item["rc"])))
    return {
        "status": str(status_obj.get("status", "")),
        "worker_id": str(status_obj.get("worker_id", "")),
        "errors_count": len(status_obj.get("errors", [])) if isinstance(status_obj.get("errors"), list) else 0,
        "warnings_count": len(status_obj.get("warnings", [])) if isinstance(status_obj.get("warnings"), list) else 0,
        "required_checks": normalized_checks,
    }


def _files_changed_summary(files_changed_obj: Any) -> dict[str, Any]:
    if not isinstance(files_changed_obj, dict):
        return {"count": 0, "paths": []}
    changes = files_changed_obj.get("changes", [])
    paths: list[str] = []
    if isinstance(changes, list):
        for change in changes:
            if isinstance(change, dict):
                paths.append(str(change.get("path", "")).replace("\\", "/"))
            elif isinstance(change, str):
                paths.append(change.replace("\\", "/"))
    cleaned = sorted(path for path in paths if path)
    return {"count": len(cleaned), "paths": cleaned}


def _bundle_inventory(
    repo_root: Path,
    run_dir: Path,
    run_id: str,
    role_name: str,
    worker_name: str,
) -> dict[str, Any]:
    worker_dir = run_dir / worker_name
    role_dir = run_dir / role_name
    is_integrator = worker_name == "Z_integrator"
    required_files = REQUIRED_INTEGRATOR_FILES if is_integrator else REQUIRED_WORKER_FILES

    status_path = worker_dir / "STATUS.json"
    files_changed_path = worker_dir / "FILES_CHANGED.json"
    summary_path = worker_dir / "SUMMARY.md"
    diff_patch_path = worker_dir / "DIFF.patch"
    files_snapshot_dir = worker_dir / "FILES"
    worktree_prompt_path = repo_root / "tools" / "codex" / "worktrees" / run_id / worker_name / "PROMPT_WORKER.txt"
    prompts_payload_path = repo_root / "tools" / "codex" / "prompts" / run_id / f"PROMPT_{worker_name}.txt"

    status_obj = _read_json(status_path) if status_path.exists() else {}
    files_changed_obj = _read_json(files_changed_path) if files_changed_path.exists() else {}

    summary_lines: list[str] = []
    if summary_path.exists():
        summary_lines = _read_text(summary_path).splitlines()[:12]

    files_list: list[str] = []
    if worker_dir.exists():
        files_list = sorted(
            path.relative_to(worker_dir).as_posix()
            for path in worker_dir.rglob("*")
            if path.is_file()
        )

    required_presence = {name: (worker_dir / name).exists() for name in sorted(required_files)}

    return {
        "role_name": role_name,
        "worker_name": worker_name,
        "role_dir_path": role_dir.as_posix(),
        "role_dir_exists": role_dir.exists(),
        "worker_dir_path": worker_dir.as_posix(),
        "worker_dir_exists": worker_dir.exists(),
        "required_files_present": required_presence,
        "bundle_files": files_list,
        "status": _status_excerpt(status_obj),
        "files_changed": _files_changed_summary(files_changed_obj),
        "summary_head": summary_lines,
        "diff_patch_exists": diff_patch_path.exists(),
        "diff_patch_size_bytes": diff_patch_path.stat().st_size if diff_patch_path.exists() else 0,
        "diff_patch_nonempty": bool(_read_text(diff_patch_path).strip()) if diff_patch_path.exists() else False,
        "files_snapshot_dir_exists": files_snapshot_dir.exists(),
        "worktree_prompt_path": worktree_prompt_path.as_posix(),
        "worktree_prompt_exists": worktree_prompt_path.exists(),
        "prompt_payload_path": prompts_payload_path.as_posix(),
        "prompt_payload_exists": prompts_payload_path.exists(),
    }


def _inventory_md(inventory: dict[str, Any]) -> str:
    run_mode = inventory.get("run_mode", {})
    lines = [
        "# VERIFY_INVENTORY",
        "",
        f"- Run ID: `{inventory['run_id']}`",
        f"- Run dir: `{inventory['run_dir']}`",
        f"- Run dir exists: `{str(inventory['run_dir_exists']).lower()}`",
        f"- WORKTREE_STATE exists: `{str(run_mode.get('worktree_state_exists', False)).lower()}`",
        f"- Observed dry_run flags: `{run_mode.get('observed_dry_run_values', [])}`",
        f"- Inferred real run: `{str(run_mode.get('inferred_real_run', False)).lower()}`",
        "",
        "## Worker Bundles",
    ]
    for bundle in inventory["workers"]:
        lines.extend(
            [
                f"### {bundle['role_name']} ({bundle['worker_name']})",
                f"- Worker dir exists: `{str(bundle['worker_dir_exists']).lower()}`",
                f"- Role alias dir exists: `{str(bundle['role_dir_exists']).lower()}`",
                f"- STATUS: `{bundle['status'].get('status', '')}`",
                f"- FILES_CHANGED count: `{bundle['files_changed']['count']}`",
                f"- DIFF.patch nonempty: `{str(bundle['diff_patch_nonempty']).lower()}`",
                f"- FILES/ snapshot dir exists: `{str(bundle['files_snapshot_dir_exists']).lower()}`",
                f"- Worktree prompt exists: `{str(bundle['worktree_prompt_exists']).lower()}`",
                f"- Prompt payload exists: `{str(bundle['prompt_payload_exists']).lower()}`",
                "- Required files:",
            ]
        )
        for file_name in sorted(bundle["required_files_present"]):
            present = bundle["required_files_present"][file_name]
            lines.append(f"  - `{file_name}`: `{str(present).lower()}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _parse_bullet_section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    out: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            out.append(line.strip()[2:].strip())
    return out


def _run_mode_summary(run_dir: Path) -> dict[str, Any]:
    worktree_state_path = run_dir / "WORKTREE_STATE.json"
    summary = {
        "worktree_state_path": worktree_state_path.as_posix(),
        "worktree_state_exists": worktree_state_path.exists(),
        "observed_dry_run_values": [],
        "inferred_real_run": False,
    }
    if not worktree_state_path.exists():
        return summary
    try:
        payload = _read_json(worktree_state_path)
    except (json.JSONDecodeError, OSError):
        return summary
    dry_values: list[bool] = []
    if isinstance(payload, dict):
        steps = payload.get("steps", [])
        if isinstance(steps, list):
            for step in steps:
                if not isinstance(step, dict):
                    continue
                actions = step.get("actions", [])
                if not isinstance(actions, list):
                    continue
                for action in actions:
                    if isinstance(action, dict) and "dry_run" in action:
                        dry_values.append(bool(action.get("dry_run")))
    observed = sorted(set(dry_values))
    summary["observed_dry_run_values"] = observed
    summary["inferred_real_run"] = bool(observed) and (False in observed)
    return summary


def _final_report_summary(run_dir: Path) -> dict[str, Any]:
    report_path = run_dir / "Z_integrator" / "FINAL_REPORT.txt"
    status_path = run_dir / "Z_integrator" / "STATUS.json"
    z_files_changed_path = run_dir / "Z_integrator" / "FILES_CHANGED.json"
    z_diff_path = run_dir / "Z_integrator" / "DIFF.patch"
    report_exists = report_path.exists()
    report_text = _read_text(report_path) if report_exists else ""
    summary_bullets = _parse_bullet_section(report_text, "## Summary")
    check_bullets = _parse_bullet_section(report_text, "## Required Checks")
    input_bullets = _parse_bullet_section(report_text, "## Inputs")
    blocking_bullets = _parse_bullet_section(report_text, "## Blocking Conditions")
    report_status = ""
    for bullet in summary_bullets:
        if bullet.lower().startswith("final status:"):
            report_status = bullet.partition(":")[2].strip()
            break
    status_json = _read_json(status_path) if status_path.exists() else {}
    z_files_changed_obj = _read_json(z_files_changed_path) if z_files_changed_path.exists() else {}
    z_files_changed = _files_changed_summary(z_files_changed_obj)
    z_status = str(status_json.get("status", "")) if isinstance(status_json, dict) else ""
    lower_text = report_text.lower()
    return {
        "report_path": report_path.as_posix(),
        "report_exists": report_exists,
        "report_status": report_status,
        "z_status_json": z_status,
        "summary_bullets": summary_bullets,
        "required_checks": check_bullets,
        "inputs": input_bullets,
        "blocking_conditions": blocking_bullets,
        "contains_blocked_token": "blocked" in lower_text,
        "mentions_determinism": "determin" in lower_text,
        "mentions_feature_flags": "feature flag" in lower_text or "feature_flags" in lower_text,
        "mentions_forbidden_src": "src/**" in lower_text,
        "z_files_changed_count": int(z_files_changed["count"]),
        "z_files_changed_paths": list(z_files_changed["paths"]),
        "z_diff_nonempty": bool(_read_text(z_diff_path).strip()) if z_diff_path.exists() else False,
        "text_sha256": _sha256_text(report_text) if report_exists else "",
    }


def _final_report_md(final_report: dict[str, Any]) -> str:
    lines = [
        "# VERIFY_FINAL_REPORT",
        "",
        f"- Report path: `{final_report['report_path']}`",
        f"- Report exists: `{str(final_report['report_exists']).lower()}`",
        f"- Summary Final status: `{final_report['report_status']}`",
        f"- Z STATUS.json status: `{final_report['z_status_json']}`",
        f"- Report sha256: `{final_report['text_sha256']}`",
        "",
        "## Generated/Modified Evidence",
        f"- Z FILES_CHANGED count: `{final_report['z_files_changed_count']}`",
        f"- Z DIFF.patch nonempty: `{str(final_report['z_diff_nonempty']).lower()}`",
    ]
    if final_report["z_files_changed_paths"]:
        lines.append("- Z FILES_CHANGED paths:")
        for item in final_report["z_files_changed_paths"]:
            lines.append(f"  - {item}")
    else:
        lines.append("- Z FILES_CHANGED paths: <none>")
    lines.extend(
        [
            "",
            "## Required Checks",
        ]
    )
    if final_report["required_checks"]:
        for item in final_report["required_checks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## Inputs",
        ]
    )
    if final_report["inputs"]:
        for item in final_report["inputs"]:
            lines.append(f"- {item}")
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## Blocking Conditions",
        ]
    )
    if final_report["blocking_conditions"]:
        for item in final_report["blocking_conditions"]:
            lines.append(f"- {item}")
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## Signals",
            f"- Contains BLOCKED token: `{str(final_report['contains_blocked_token']).lower()}`",
            f"- Mentions determinism explicitly: `{str(final_report['mentions_determinism']).lower()}`",
            f"- Mentions feature flags: `{str(final_report['mentions_feature_flags']).lower()}`",
            f"- Mentions forbidden src/** paths: `{str(final_report['mentions_forbidden_src']).lower()}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _git_changed_paths(repo_root: Path) -> list[str]:
    result = _run_command(["git", "status", "--porcelain=v1"], cwd=repo_root)
    if result.rc != 0:
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        payload = line[3:] if len(line) > 3 else line
        changed.append(payload.replace("\\", "/").strip())
    return sorted(changed)


def _worker_execution_conclusion(inventory: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    worker_rows = [row for row in inventory["workers"] if row["worker_name"] != "Z_integrator"]
    executed: list[dict[str, Any]] = []
    not_executed: list[dict[str, Any]] = []
    for row in worker_rows:
        status = row["status"].get("status", "")
        files_changed_count = int(row["files_changed"]["count"])
        diff_nonempty = bool(row["diff_patch_nonempty"])
        has_execution_evidence = status not in ("", "PENDING") or files_changed_count > 0 or diff_nonempty
        evidence = {
            "worker": row["worker_name"],
            "status": status,
            "files_changed_count": files_changed_count,
            "diff_patch_nonempty": diff_nonempty,
        }
        if has_execution_evidence:
            executed.append(evidence)
        else:
            not_executed.append(evidence)
    if executed and not not_executed:
        conclusion_code = 1
        conclusion_text = "Workers executed and changes were applied."
    elif executed and not_executed:
        conclusion_code = 3
        conclusion_text = "Partial execution: some workers ran, others did not."
    else:
        conclusion_code = 2
        conclusion_text = "Workers did NOT execute; only prompts/bundles were prepared (manual step required)."

    changed_paths = _git_changed_paths(repo_root)
    target_changed_paths = sorted(
        path for path in changed_paths if any(path.startswith(prefix + "/") or path == prefix for prefix in TARGET_PACKAGES)
    )
    return {
        "conclusion_code": conclusion_code,
        "conclusion_text": conclusion_text,
        "executed_workers": sorted(executed, key=lambda item: item["worker"]),
        "not_executed_workers": sorted(not_executed, key=lambda item: item["worker"]),
        "git_changed_paths_total": len(changed_paths),
        "git_changed_target_paths": target_changed_paths,
    }


def _worker_execution_md(execution: dict[str, Any]) -> str:
    lines = [
        "# VERIFY_WORKER_EXECUTION",
        "",
        f"- Conclusion code: `{execution['conclusion_code']}`",
        f"- Conclusion: {execution['conclusion_text']}",
        f"- Git changed paths (total): `{execution['git_changed_paths_total']}`",
        "",
        "## Executed Workers",
    ]
    if execution["executed_workers"]:
        for row in execution["executed_workers"]:
            lines.append(
                f"- {row['worker']}: status={row['status']} files_changed={row['files_changed_count']} diff_nonempty={str(row['diff_patch_nonempty']).lower()}"
            )
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## Not Executed Workers",
        ]
    )
    if execution["not_executed_workers"]:
        for row in execution["not_executed_workers"]:
            lines.append(
                f"- {row['worker']}: status={row['status']} files_changed={row['files_changed_count']} diff_nonempty={str(row['diff_patch_nonempty']).lower()}"
            )
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## Target Package Paths In Current Git Status",
        ]
    )
    if execution["git_changed_target_paths"]:
        for path in execution["git_changed_target_paths"]:
            lines.append(f"- {path}")
    else:
        lines.append("- <none>")
    return "\n".join(lines).rstrip() + "\n"


def _iter_repo_files(path: Path) -> Iterable[Path]:
    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        rel_parts = {part.lower() for part in file_path.relative_to(path).parts}
        if rel_parts & set(IGNORE_DIRS):
            continue
        yield file_path


def _detect_feature_flags_on(json_obj: Any, *, path_prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(json_obj, dict):
        for key in sorted(json_obj):
            value = json_obj[key]
            child_prefix = f"{path_prefix}.{key}" if path_prefix else str(key)
            key_lower = str(key).lower()
            if isinstance(value, bool) and value and ("flag" in key_lower or "feature" in key_lower):
                hits.append(child_prefix)
            hits.extend(_detect_feature_flags_on(value, path_prefix=child_prefix))
    elif isinstance(json_obj, list):
        for index, item in enumerate(json_obj):
            child_prefix = f"{path_prefix}[{index}]"
            hits.extend(_detect_feature_flags_on(item, path_prefix=child_prefix))
    return hits


def _scaffold_validation(repo_root: Path) -> dict[str, Any]:
    packages: list[dict[str, Any]] = []
    hard_violations: list[str] = []
    for package_rel in sorted(TARGET_PACKAGES):
        package_path = repo_root / package_rel
        package_info: dict[str, Any] = {
            "path": package_rel,
            "exists": package_path.exists(),
            "package_json_exists": (package_path / "package.json").exists(),
            "src_artifact_violations": [],
            "feature_flags_on": [],
        }
        if not package_path.exists():
            hard_violations.append(f"Missing required scaffold package: {package_rel}")
            packages.append(package_info)
            continue
        if not (package_path / "package.json").exists():
            hard_violations.append(f"Missing package.json in required scaffold package: {package_rel}")
        src_dir = package_path / "src"
        if src_dir.exists():
            violations: list[str] = []
            for src_file in sorted(src_dir.rglob("*")):
                if not src_file.is_file():
                    continue
                rel = src_file.relative_to(package_path).as_posix()
                name = src_file.name
                if name in BUNDLE_ARTIFACT_BASENAMES or name.endswith(".patch"):
                    violations.append(rel)
                if "dump" in name.lower() or "backup" in name.lower() or name.lower().endswith(".bak"):
                    violations.append(rel)
            package_info["src_artifact_violations"] = sorted(set(violations))
            if package_info["src_artifact_violations"]:
                hard_violations.append(
                    f"Forbidden artifact-like files found under {package_rel}/src: {', '.join(package_info['src_artifact_violations'])}"
                )

        feature_hits: list[str] = []
        for json_file in sorted(package_path.rglob("*.json")):
            rel_parts = {part.lower() for part in json_file.relative_to(package_path).parts}
            if rel_parts & set(IGNORE_DIRS):
                continue
            try:
                parsed = _read_json(json_file)
            except json.JSONDecodeError:
                continue
            hits = _detect_feature_flags_on(parsed)
            for hit in sorted(hits):
                feature_hits.append(f"{json_file.relative_to(package_path).as_posix()}::{hit}")
        package_info["feature_flags_on"] = sorted(set(feature_hits))
        if package_info["feature_flags_on"]:
            hard_violations.append(
                f"Feature flag defaults ON detected in {package_rel}: {', '.join(package_info['feature_flags_on'])}"
            )
        packages.append(package_info)

    return {"packages": packages, "hard_violations": sorted(set(hard_violations))}


def _scaffold_md(scaffold: dict[str, Any]) -> str:
    lines = [
        "# VERIFY_SCAFFOLD",
        "",
        "## Target Packages",
    ]
    for package in scaffold["packages"]:
        lines.extend(
            [
                f"### {package['path']}",
                f"- Exists: `{str(package['exists']).lower()}`",
                f"- package.json exists: `{str(package['package_json_exists']).lower()}`",
                "- src/** artifact violations:",
            ]
        )
        if package["src_artifact_violations"]:
            for item in package["src_artifact_violations"]:
                lines.append(f"  - {item}")
        else:
            lines.append("  - <none>")
        lines.append("- Feature flags ON by default:")
        if package["feature_flags_on"]:
            for item in package["feature_flags_on"]:
                lines.append(f"  - {item}")
        else:
            lines.append("  - <none>")
        lines.append("")
    lines.extend(
        [
            "## Hard Violations",
        ]
    )
    if scaffold["hard_violations"]:
        for item in scaffold["hard_violations"]:
            lines.append(f"- {item}")
    else:
        lines.append("- <none>")
    return "\n".join(lines).rstrip() + "\n"


def _hash_scaffold(repo_root: Path) -> tuple[str, dict[str, Any]]:
    lines = [
        "# VERIFY_SCAFFOLD_HASHES",
        "",
    ]
    package_meta: dict[str, Any] = {}
    for package_rel in sorted(TARGET_PACKAGES):
        package_path = repo_root / package_rel
        lines.append(f"[{package_rel}]")
        if not package_path.exists():
            lines.append("MISSING")
            lines.append("")
            package_meta[package_rel] = {"exists": False, "aggregate_sha256": "", "files": 0}
            continue
        entries: list[str] = []
        for file_path in _iter_repo_files(package_path):
            rel_repo_path = file_path.relative_to(repo_root).as_posix()
            entries.append(f"{rel_repo_path} {_sha256_file(file_path)}")
        for entry in sorted(entries):
            lines.append(entry)
        aggregate = _sha256_text("\n".join(sorted(entries)))
        lines.append(f"AGGREGATE_SHA256 {aggregate}")
        lines.append("")
        package_meta[package_rel] = {"exists": True, "aggregate_sha256": aggregate, "files": len(entries)}
    return ("\n".join(lines).rstrip() + "\n", package_meta)


def _safe_check_results(repo_root: Path) -> dict[str, Any]:
    health_path = repo_root / "tools" / "health"
    health_result: dict[str, Any] = {
        "command": ["node", "tools/health/src/check_repo_health.mjs"],
        "available": health_path.exists(),
        "rc": None,
        "status": "SKIP",
        "note": "",
    }
    if health_path.exists():
        result = _run_command(["node", "tools/health/src/check_repo_health.mjs"], cwd=repo_root)
        health_result["rc"] = result.rc
        health_result["status"] = "PASS" if result.rc == 0 else "FAIL"
        health_result["note"] = (result.stdout + "\n" + result.stderr).strip().splitlines()[0] if (result.stdout or result.stderr) else ""
        if result.error:
            health_result["note"] = result.error
            health_result["status"] = "FAIL"
            health_result["rc"] = 127

    doctor_cmd = ["python", "-m", "tools.codex.factory", "doctor"]
    doctor_result = _run_command(doctor_cmd, cwd=repo_root)
    doctor_payload = _extract_last_json_object((doctor_result.stdout + "\n" + doctor_result.stderr).strip())
    doctor_summary: dict[str, Any] = {
        "command": doctor_cmd,
        "rc": doctor_result.rc,
        "status": "",
        "blocked": None,
        "warnings": None,
        "checks_total": None,
        "checks_fail": None,
    }
    if isinstance(doctor_payload, dict):
        checks = doctor_payload.get("checks", [])
        checks_fail = 0
        checks_total = len(checks) if isinstance(checks, list) else 0
        if isinstance(checks, list):
            for item in checks:
                if isinstance(item, dict) and str(item.get("status", "")).upper() in {"FAIL", "BLOCKED"}:
                    checks_fail += 1
        doctor_summary.update(
            {
                "status": str(doctor_payload.get("status", "")),
                "blocked": doctor_payload.get("blocked"),
                "warnings": doctor_payload.get("warnings"),
                "checks_total": checks_total,
                "checks_fail": checks_fail,
            }
        )
    return {"health": health_result, "doctor": doctor_summary}


def _verdict_md(
    run_id: str,
    inventory: dict[str, Any],
    final_report: dict[str, Any],
    execution: dict[str, Any],
    scaffold: dict[str, Any],
    checks: dict[str, Any],
) -> tuple[str, list[str]]:
    hard_violations: list[str] = []
    if not inventory["run_dir_exists"]:
        hard_violations.append(f"Run folder missing: tools/codex/runs/{run_id}")
    if not final_report["report_exists"]:
        hard_violations.append("Missing final report: tools/codex/runs/<RUN_ID>/Z_integrator/FINAL_REPORT.txt")
    hard_violations.extend(scaffold["hard_violations"])

    expected: list[str] = []
    unexpected: list[str] = []
    risks: list[str] = []

    if inventory["run_dir_exists"]:
        expected.append(f"Run directory exists with canonical worker folders under `tools/codex/runs/{run_id}/`.")
    run_mode = inventory.get("run_mode", {})
    if run_mode.get("inferred_real_run"):
        expected.append("WORKTREE_STATE evidence indicates worktrees were created in non-dry-run mode.")
    else:
        unexpected.append("Could not prove non-dry-run execution from WORKTREE_STATE dry_run evidence.")
    expected.append("Prompt payloads exist for A/B/C/D in `tools/codex/prompts/<RUN_ID>/` and worktree `PROMPT_WORKER.txt` files exist.")
    if final_report["report_exists"]:
        expected.append("Integrator `FINAL_REPORT.txt` and `STATUS.json` are present under `Z_integrator`.")

    if execution["conclusion_code"] == 2:
        expected.append("Manual worker-step message is consistent with evidence: worker bundles remained `PENDING` with empty diffs.")
    elif execution["conclusion_code"] == 3:
        unexpected.append("Only partial worker execution detected; run state is mixed.")
    else:
        unexpected.append("Workers appear executed even though operator output referenced manual worker step.")

    if scaffold["hard_violations"]:
        unexpected.extend(scaffold["hard_violations"])

    worker_pending = [
        row["worker_name"]
        for row in inventory["workers"]
        if row["worker_name"] != "Z_integrator" and row["status"].get("status", "") == "PENDING"
    ]
    if worker_pending and final_report["report_status"].upper() == "PASS":
        unexpected.append(
            "Integrator report is PASS while worker STATUS values are still PENDING; this indicates prompt/bootstrap-only integration outcome."
        )
        risks.append("PASS can be misread as completed implementation when no worker changes were produced.")

    if final_report["report_status"] and final_report["z_status_json"] and final_report["report_status"] != final_report["z_status_json"]:
        unexpected.append("Final report status and Z STATUS.json status are inconsistent.")

    if checks["doctor"]["status"] not in ("PASS", ""):
        risks.append("Factory doctor did not return PASS during verification.")
    if checks["health"]["available"] and checks["health"]["status"] != "PASS":
        risks.append("Health check failed; source-tree hygiene may be compromised.")

    # Contract mismatch note required by prompt if assumptions differ.
    unexpected.append(
        "Prompt requested role folders `A_core/B_tooling/C_features/D_validation`, but contract/runtime uses `A_worker/B_worker/C_worker/D_worker`."
    )

    next_action = (
        "Execute the four worker prompts for RUN_PHASE1_EXTRACT_017 (A/B/C/D) and then rerun "
        "`python -m tools.codex.factory operator watch --run-id RUN_PHASE1_EXTRACT_017 --base-ref HEAD`."
    )

    lines = [
        "# VERIFY_VERDICT",
        "",
        f"- Run ID: `{run_id}`",
        f"- Worker execution conclusion code: `{execution['conclusion_code']}`",
        "",
        "## EXPECTED",
    ]
    for item in sorted(set(expected)):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## UNEXPECTED",
        ]
    )
    if unexpected:
        for item in sorted(set(unexpected)):
            lines.append(f"- {item}")
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## RISK",
        ]
    )
    if risks:
        for item in sorted(set(risks)):
            lines.append(f"- {item}")
    else:
        lines.append("- <none>")
    lines.extend(
        [
            "",
            "## NEXT ACTION",
            f"- {next_action}",
            "",
            "## Evidence Paths",
            f"- `tools/codex/runs/{run_id}/VERIFY_INVENTORY.json`",
            f"- `tools/codex/runs/{run_id}/VERIFY_FINAL_REPORT.md`",
            f"- `tools/codex/runs/{run_id}/VERIFY_WORKER_EXECUTION.md`",
            f"- `tools/codex/runs/{run_id}/VERIFY_SCAFFOLD.md`",
            f"- `tools/codex/runs/{run_id}/VERIFY_SCAFFOLD_HASHES.txt`",
        ]
    )
    return ("\n".join(lines).rstrip() + "\n", sorted(set(hard_violations)))


def run_verification(run_id: str) -> int:
    repo_root = _repo_root_from_script(Path(__file__))
    runs_root = repo_root / "tools" / "codex" / "runs"
    run_dir = _find_run_dir(runs_root, run_id)

    if run_dir is None:
        # Emit deterministic minimal outputs in canonical target location even when missing.
        target_dir = runs_root / run_id
        inventory_payload = {
            "run_id": run_id,
            "run_dir": target_dir.as_posix(),
            "run_dir_exists": False,
            "workers": [],
        }
        _write_json(target_dir / "VERIFY_INVENTORY.json", inventory_payload)
        _write_text(target_dir / "VERIFY_INVENTORY.md", _inventory_md(inventory_payload))
        _write_text(
            target_dir / "VERIFY_VERDICT.md",
            "# VERIFY_VERDICT\n\n## UNEXPECTED\n- Run folder not found.\n\n## NEXT ACTION\n- Confirm run id and rerun verifier.\n",
        )
        return 1

    run_id_resolved = run_dir.name

    workers_inventory = [
        _bundle_inventory(
            repo_root=repo_root,
            run_dir=run_dir,
            run_id=run_id_resolved,
            role_name=role,
            worker_name=worker,
        )
        for role, worker in ROLE_TO_WORKER
    ]
    inventory_payload = {
        "run_id": run_id_resolved,
        "run_dir": run_dir.as_posix(),
        "run_dir_exists": run_dir.exists(),
        "run_mode": _run_mode_summary(run_dir),
        "workers": workers_inventory,
    }
    _write_json(run_dir / "VERIFY_INVENTORY.json", inventory_payload)
    _write_text(run_dir / "VERIFY_INVENTORY.md", _inventory_md(inventory_payload))

    final_report_payload = _final_report_summary(run_dir)
    _write_text(run_dir / "VERIFY_FINAL_REPORT.md", _final_report_md(final_report_payload))

    worker_execution_payload = _worker_execution_conclusion(inventory_payload, repo_root)
    _write_text(run_dir / "VERIFY_WORKER_EXECUTION.md", _worker_execution_md(worker_execution_payload))

    scaffold_payload = _scaffold_validation(repo_root)
    _write_text(run_dir / "VERIFY_SCAFFOLD.md", _scaffold_md(scaffold_payload))

    hash_text, hash_meta = _hash_scaffold(repo_root)
    _write_text(run_dir / "VERIFY_SCAFFOLD_HASHES.txt", hash_text)

    safe_checks = _safe_check_results(repo_root)

    verdict_text, hard_violations = _verdict_md(
        run_id=run_id_resolved,
        inventory=inventory_payload,
        final_report=final_report_payload,
        execution=worker_execution_payload,
        scaffold=scaffold_payload,
        checks=safe_checks,
    )
    _write_text(run_dir / "VERIFY_VERDICT.md", verdict_text)

    report_payload = {
        "run_id": run_id_resolved,
        "run_dir": run_dir.as_posix(),
        "worker_execution_conclusion": worker_execution_payload["conclusion_code"],
        "hard_violations": hard_violations,
        "checks": safe_checks,
        "scaffold_hashes": hash_meta,
        "outputs": sorted(
            [
                str((run_dir / "VERIFY_INVENTORY.json").relative_to(repo_root)).replace("\\", "/"),
                str((run_dir / "VERIFY_INVENTORY.md").relative_to(repo_root)).replace("\\", "/"),
                str((run_dir / "VERIFY_FINAL_REPORT.md").relative_to(repo_root)).replace("\\", "/"),
                str((run_dir / "VERIFY_WORKER_EXECUTION.md").relative_to(repo_root)).replace("\\", "/"),
                str((run_dir / "VERIFY_SCAFFOLD.md").relative_to(repo_root)).replace("\\", "/"),
                str((run_dir / "VERIFY_SCAFFOLD_HASHES.txt").relative_to(repo_root)).replace("\\", "/"),
                str((run_dir / "VERIFY_VERDICT.md").relative_to(repo_root)).replace("\\", "/"),
            ]
        ),
    }
    _write_json(run_dir / "VERIFY_REPORT.json", report_payload)

    return 1 if hard_violations else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a Factory phase1-extract run.")
    parser.add_argument("--run-id", default="RUN_PHASE1_EXTRACT_017", help="Run id to verify.")
    args = parser.parse_args()
    return run_verification(run_id=str(args.run_id).strip())


if __name__ == "__main__":
    raise SystemExit(main())
