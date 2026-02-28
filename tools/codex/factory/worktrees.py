from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import time
import traceback
from pathlib import Path
from typing import Any

from .common import CODEX_DIR, DEFAULT_BRANCH_PREFIX, REPO_ROOT, RUNS_DIR, WORKERS, ensure_dir, write_json
from .locks import LockAcquisitionError, acquire_run_lock, acquire_worker_lock
from .worktree_contract import (
    FIXED_WORKTREE_MODE,
    fixed_worker_path,
    fixed_worktrees_root,
    is_run_scoped_worktree_segment,
    resolve_unified_worktree_mode,
)


def _debug_stack_enabled() -> bool:
    value = os.environ.get("HITECH_FACTORY_DEBUG_STACK", "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_code_cli() -> str | None:
    for candidate in ("code.cmd", "code"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _env_enabled(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_path_for_compare(value: str | None) -> str:
    if value is None:
        return ""
    candidate = str(value).strip().strip('"')
    if candidate.endswith("\\") or candidate.endswith("/"):
        candidate = candidate.rstrip("\\/")
    return candidate.lower()


def _path_entries(value: str | None) -> list[str]:
    if value is None:
        return []
    return [item.strip() for item in str(value).split(";") if item.strip()]


def _process_path_contains(entry: str) -> bool:
    if not entry:
        return False
    target = _normalize_path_for_compare(entry)
    for existing in _path_entries(os.environ.get("PATH")):
        if _normalize_path_for_compare(existing) == target:
            return True
    return False


def _append_process_path(entry: str) -> None:
    if not entry:
        return
    if _process_path_contains(entry):
        return
    existing = _path_entries(os.environ.get("PATH"))
    existing.append(entry)
    os.environ["PATH"] = ";".join(existing)


def _is_code_process_name(name: str | None) -> bool:
    value = (name or "").strip().lower()
    return value in {"code.exe", "code"}


def _list_code_pids() -> list[int]:
    try:
        import psutil  # type: ignore

        pids: list[int] = []
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            name = proc.info.get("name")
            if _is_code_process_name(name):
                pid = int(proc.info["pid"])
                pids.append(pid)
        return sorted(set(pids))
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH", "/FI", "IMAGENAME eq Code.exe"],
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except Exception:
        return []

    if proc.returncode != 0:
        return []

    rows = [line for line in proc.stdout.splitlines() if line.strip()]
    reader = csv.reader(rows)
    pids: list[int] = []
    for row in reader:
        if not row or row[0].strip().lower() == "info:":
            continue
        if len(row) < 2:
            continue
        raw_pid = row[1].replace(",", "").strip()
        if raw_pid.isdigit():
            pids.append(int(raw_pid))
    return sorted(set(pids))


def _probe_pid_ownership(pid: int) -> dict[str, Any]:
    try:
        import psutil  # type: ignore

        try:
            process = psutil.Process(int(pid))
            return {
                "exists": True,
                "is_code": _is_code_process_name(process.name()),
            }
        except psutil.NoSuchProcess:
            return {"exists": False, "is_code": False}
        except psutil.AccessDenied:
            return {"exists": True, "is_code": False}
        except psutil.Error:
            return {"exists": True, "is_code": False}
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH", "/FI", f"PID eq {int(pid)}"],
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except Exception:
        return {"exists": False, "is_code": False}

    if proc.returncode != 0:
        return {"exists": False, "is_code": False}

    rows = [line for line in proc.stdout.splitlines() if line.strip()]
    reader = csv.reader(rows)
    for row in reader:
        if not row:
            continue
        first = row[0].strip().lower()
        if first == "info:":
            continue
        if len(row) < 2:
            continue
        row_pid = row[1].replace(",", "").strip()
        if not row_pid.isdigit() or int(row_pid) != int(pid):
            continue
        return {
            "exists": True,
            "is_code": _is_code_process_name(row[0]),
        }
    return {"exists": False, "is_code": False}


def _find_code_descendants_psutil(wrapper_pid: int) -> list[int]:
    try:
        import psutil  # type: ignore

        root = psutil.Process(int(wrapper_pid))
        pids: list[int] = []
        for child in root.children(recursive=True):
            try:
                if _is_code_process_name(child.name()):
                    pids.append(int(child.pid))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return sorted(set(pids))
    except Exception:
        return []


def _find_code_descendants_cim(wrapper_pid: int) -> list[int]:
    script = (
        f"$root={int(wrapper_pid)};"
        "$queue=New-Object System.Collections.Generic.Queue[int];"
        "$seen=New-Object System.Collections.Generic.HashSet[int];"
        "$hits=New-Object System.Collections.Generic.List[int];"
        "$queue.Enqueue($root);"
        "while($queue.Count -gt 0){"
        "$parent=$queue.Dequeue();"
        "$children=Get-CimInstance Win32_Process -Filter \"ParentProcessId=$parent\" -ErrorAction SilentlyContinue;"
        "foreach($child in $children){"
        "$pid=[int]$child.ProcessId;"
        "if($seen.Add($pid)){"
        "$queue.Enqueue($pid);"
        "if($child.Name -ieq 'Code.exe'){$hits.Add($pid)|Out-Null}"
        "}"
        "}"
        "};"
        "$hits|Sort-Object -Unique|ForEach-Object{Write-Output $_}"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            cwd=str(REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    pids: list[int] = []
    for line in proc.stdout.splitlines():
        value = line.strip()
        if value.isdigit():
            pids.append(int(value))
    return sorted(set(pids))


def _resolve_code_pid_from_wrapper(
    wrapper_pid: int | None,
    *,
    baseline_code_pids: list[int],
    max_wait_seconds: float = 8.0,
    poll_seconds: float = 0.25,
) -> int | None:
    baseline = set(int(item) for item in baseline_code_pids)
    deadline = time.monotonic() + max(0.5, float(max_wait_seconds))
    while time.monotonic() <= deadline:
        candidates: list[int] = []
        if isinstance(wrapper_pid, int):
            candidates = _find_code_descendants_psutil(wrapper_pid)
            if not candidates:
                candidates = _find_code_descendants_cim(wrapper_pid)
        if candidates:
            return int(sorted(set(candidates))[0])

        after_pids = _list_code_pids()
        new_pids = sorted(set(after_pids) - baseline)
        if new_pids:
            return int(new_pids[0])

        time.sleep(max(0.05, float(poll_seconds)))
    return None


def _taskkill(pid: int, *, force: bool) -> dict[str, Any]:
    cmd = ["taskkill"]
    if force:
        cmd.append("/F")
    cmd.extend(["/PID", str(pid)])
    result = _run(cmd, dry_run=False)
    text = f"{result.get('stdout', '')}\n{result.get('stderr', '')}".lower()
    if result.get("rc", 1) == 0:
        return {
            "pid": pid,
            "action": "killed" if force else "closed_gracefully",
            "detail": "",
        }
    if "not found" in text or "no running instance" in text or "cannot find the process" in text:
        return {
            "pid": pid,
            "action": "already_gone",
            "detail": "",
        }
    return {
        "pid": pid,
        "action": "error",
        "detail": text.strip(),
    }


def _session_file_path(run_id: str) -> Path:
    return RUNS_DIR / run_id / "_debug" / "VSCODE_SESSION.json"


def _cleanup_report_path(run_id: str) -> Path:
    return RUNS_DIR / run_id / "_debug" / "VSCODE_CLEANUP_REPORT.txt"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _scan_registry_sessions(current_run_id: str, *, include_current: bool) -> list[dict[str, Any]]:
    session_files = sorted(RUNS_DIR.glob("*/_debug/VSCODE_SESSION.json"), key=lambda item: item.as_posix())
    rows: list[dict[str, Any]] = []
    for session_file in session_files:
        source_run_id = session_file.parent.parent.name
        if not include_current and source_run_id == current_run_id:
            continue
        try:
            payload = _load_json(session_file)
        except Exception:
            continue
        sessions = payload.get("sessions", [])
        if not isinstance(sessions, list):
            continue
        for item in sessions:
            if not isinstance(item, dict):
                continue
            run_id = str(item.get("run_id", source_run_id)).strip() or source_run_id
            if not include_current and run_id == current_run_id:
                continue
            worker = str(item.get("worker", "")).strip()
            opened = str(item.get("opened_folder_path", "")).strip()
            raw_pid = item.get("pid")
            pid: int | None
            if isinstance(raw_pid, int):
                pid = raw_pid
            else:
                pid = None
            rows.append(
                {
                    "run_id": run_id,
                    "worker": worker,
                    "opened_folder_path": opened,
                    "pid": pid,
                    "window_handle": item.get("window_handle"),
                }
            )
    rows.sort(key=lambda entry: (str(entry["run_id"]), str(entry["worker"]), str(entry["opened_folder_path"]), str(entry["pid"])))
    return rows


def _write_cleanup_report(run_id: str, *, clean_enabled: bool, nuke_enabled: bool, sessions: list[dict[str, Any]], actions: list[dict[str, Any]]) -> str:
    target = _cleanup_report_path(run_id)
    ensure_dir(target.parent)
    lines: list[str] = []
    lines.append(f"run_id={run_id}")
    lines.append(f"clean_enabled={str(clean_enabled).lower()}")
    lines.append(f"nuke_enabled={str(nuke_enabled).lower()}")
    lines.append(f"sessions_found={len(sessions)}")
    lines.append(f"sessions_targeted={len(actions)}")
    lines.append("")
    lines.append("sessions:")
    for entry in sessions:
        pid_text = "null" if entry.get("pid") is None else str(entry.get("pid"))
        lines.append(f"{entry.get('run_id','')}|{entry.get('worker','')}|{pid_text}|{entry.get('opened_folder_path','')}")
    lines.append("")
    lines.append("actions:")
    for action in actions:
        pid_text = "null" if action.get("pid") is None else str(action.get("pid"))
        lines.append(
            f"{action.get('run_id','')}|{action.get('worker','')}|{pid_text}|{action.get('action','')}|{action.get('detail','')}"
        )
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return target.as_posix()


def _cleanup_vscode_sessions(run_id: str) -> dict[str, Any]:
    clean_enabled = _env_enabled("HITECH_FACTORY_VSCODE_CLEAN", True)
    nuke_enabled = _env_enabled("HITECH_FACTORY_VSCODE_NUKE", False)
    sessions = _scan_registry_sessions(run_id, include_current=nuke_enabled)

    actions: list[dict[str, Any]] = []
    if clean_enabled:
        handled: dict[int, dict[str, Any]] = {}
        for entry in sessions:
            pid = entry.get("pid")
            if not isinstance(pid, int):
                actions.append(
                    {
                        "run_id": entry.get("run_id", ""),
                        "worker": entry.get("worker", ""),
                        "pid": None,
                        "action": "missing_pid",
                        "detail": "",
                    }
                )
                continue
            if pid in handled:
                reused = handled[pid]
                actions.append(
                    {
                        "run_id": entry.get("run_id", ""),
                        "worker": entry.get("worker", ""),
                        "pid": pid,
                        "action": reused["action"],
                        "detail": reused["detail"],
                    }
                )
                continue

            ownership = _probe_pid_ownership(pid)
            if not ownership.get("exists"):
                result = {
                    "pid": pid,
                    "action": "already_gone",
                    "detail": "",
                }
            elif not ownership.get("is_code"):
                result = {
                    "pid": pid,
                    "action": "ownership_mismatch",
                    "detail": "",
                }
            else:
                graceful = _taskkill(pid, force=False)
                result = graceful
                if graceful["action"] == "error":
                    forced = _taskkill(pid, force=True)
                    result = forced
            handled[pid] = result
            actions.append(
                {
                    "run_id": entry.get("run_id", ""),
                    "worker": entry.get("worker", ""),
                    "pid": pid,
                    "action": result["action"],
                    "detail": result["detail"],
                }
            )
    else:
        for entry in sessions:
            actions.append(
                {
                    "run_id": entry.get("run_id", ""),
                    "worker": entry.get("worker", ""),
                    "pid": entry.get("pid"),
                    "action": "skipped_clean_disabled",
                    "detail": "",
                }
            )

    report_path = _write_cleanup_report(
        run_id,
        clean_enabled=clean_enabled,
        nuke_enabled=nuke_enabled,
        sessions=sessions,
        actions=actions,
    )
    return {
        "clean_enabled": clean_enabled,
        "nuke_enabled": nuke_enabled,
        "sessions_found": len(sessions),
        "actions": actions,
        "report": report_path,
    }


def _write_vscode_session_registry(run_id: str, sessions: list[dict[str, Any]]) -> str:
    ordered = sorted(
        [
            {
                "opened_folder_path": str(item.get("opened_folder_path", "")),
                "pid": int(item["pid"]) if isinstance(item.get("pid"), int) else None,
                "run_id": str(item.get("run_id", run_id)),
                "worker": str(item.get("worker", "")),
                "window_handle": None,
            }
            for item in sessions
        ],
        key=lambda entry: (str(entry["run_id"]), str(entry["worker"]), str(entry["opened_folder_path"]), str(entry["pid"])),
    )
    payload = {
        "run_id": run_id,
        "sessions": ordered,
    }
    target = _session_file_path(run_id)
    write_json(target, payload)
    return target.as_posix()


def worktree_root(run_id: str) -> Path:
    _ = run_id
    return fixed_worktrees_root()


def worktree_path(run_id: str, worker: str) -> Path:
    _ = run_id
    return fixed_worker_path(worker)


def branch_name(run_id: str, worker: str, branch_prefix: str = DEFAULT_BRANCH_PREFIX) -> str:
    _ = run_id
    return f"{branch_prefix}/{worker}"


def _run(args: list[str], cwd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 0,
            "stdout": "",
            "stderr": "",
            "dry_run": True,
        }
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd or REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "dry_run": False,
        }
    except FileNotFoundError as exc:
        detail = f"command not found: {args[0]} ({exc})"
        if _debug_stack_enabled():
            detail = f"{detail}\n{traceback.format_exc()}"
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 127,
            "stdout": "",
            "stderr": detail,
            "dry_run": False,
        }
    except Exception as exc:
        detail = f"subprocess execution failed: {exc!r}"
        if _debug_stack_enabled():
            detail = f"{detail}\n{traceback.format_exc()}"
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 1,
            "stdout": "",
            "stderr": detail,
            "dry_run": False,
        }


def _run_with_wrapper_pid(
    args: list[str],
    *,
    cwd: Path | None = None,
    dry_run: bool = False,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    if dry_run:
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 0,
            "stdout": "",
            "stderr": "",
            "dry_run": True,
            "wrapper_pid": None,
        }

    try:
        proc = subprocess.Popen(
            args,
            cwd=str(cwd or REPO_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        detail = f"command not found: {args[0]} ({exc})"
        if _debug_stack_enabled():
            detail = f"{detail}\n{traceback.format_exc()}"
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 127,
            "stdout": "",
            "stderr": detail,
            "dry_run": False,
            "wrapper_pid": None,
        }
    except Exception as exc:
        detail = f"subprocess execution failed: {exc!r}"
        if _debug_stack_enabled():
            detail = f"{detail}\n{traceback.format_exc()}"
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 1,
            "stdout": "",
            "stderr": detail,
            "dry_run": False,
            "wrapper_pid": None,
        }

    wrapper_pid = int(proc.pid)
    try:
        stdout, stderr = proc.communicate(timeout=max(0.5, float(timeout_seconds)))
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": int(proc.returncode),
            "stdout": stdout or "",
            "stderr": stderr or "",
            "dry_run": False,
            "wrapper_pid": wrapper_pid,
        }
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        timeout_detail = (stderr or "").strip()
        if timeout_detail:
            timeout_detail = f"{timeout_detail}\n"
        timeout_detail = f"{timeout_detail}code CLI launch timed out"
        return {
            "cmd": args,
            "cwd": str(cwd or REPO_ROOT),
            "rc": 124,
            "stdout": stdout or "",
            "stderr": timeout_detail,
            "dry_run": False,
            "wrapper_pid": wrapper_pid,
        }


def _resolve_commit(ref: str, *, cwd: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"ref": ref, "rc": 0, "commit": "DRYRUN", "stderr": "", "stdout": ""}
    proc = subprocess.run(
        ["git", "rev-parse", ref],
        cwd=str(cwd or REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "ref": ref,
        "rc": proc.returncode,
        "commit": proc.stdout.strip(),
        "stderr": proc.stderr,
        "stdout": proc.stdout,
    }


def create_worktrees(
    run_id: str,
    *,
    workers: list[str] | None = None,
    base_ref: str = "HEAD",
    branch_prefix: str = DEFAULT_BRANCH_PREFIX,
    dry_run: bool = False,
) -> dict[str, Any]:
    chosen = workers or list(WORKERS)
    try:
        mode_info = resolve_unified_worktree_mode()
    except ValueError as exc:
        return {
            "run_id": run_id,
            "operation": "create",
            "status": "BLOCKED",
            "steps": [],
            "blocked": len(chosen),
            "lock_error": "",
            "base_ref": base_ref,
            "base_ref_commit": _resolve_commit(base_ref, dry_run=dry_run),
            "worktree_mode": "",
            "contract_path": "",
            "error": str(exc),
        }

    root = worktree_root(run_id)
    ensure_dir(root)
    steps: list[dict[str, Any]] = []
    base_ref_commit = _resolve_commit(base_ref, dry_run=dry_run)
    lock_errors: list[str] = []

    try:
        run_lock = acquire_run_lock(run_id, owner="worktrees.create")
    except LockAcquisitionError as exc:
        return {
            "run_id": run_id,
            "operation": "create",
            "status": "BLOCKED",
            "steps": [],
            "blocked": len(chosen),
            "lock_error": str(exc),
            "base_ref": base_ref,
            "base_ref_commit": base_ref_commit,
        }

    try:
        for worker in chosen:
            target = worktree_path(run_id, worker)
            worker_actions: list[dict[str, Any]] = []
            if is_run_scoped_worktree_segment(worker):
                detail = f"guard_trip: run-scoped worker id is forbidden in unified mode ({worker})"
                lock_errors.append(detail)
                steps.append(
                    {
                        "worker": worker,
                        "status": "BLOCKED",
                        "detail": detail,
                        "path": target.as_posix(),
                        "actions": [],
                        "base_ref_commit": base_ref_commit,
                        "worktree_mode": mode_info["worktree_mode"],
                    }
                )
                continue
            try:
                worker_lock = acquire_worker_lock(run_id, worker, owner="worktrees.create")
            except LockAcquisitionError as exc:
                lock_errors.append(str(exc))
                steps.append(
                    {
                        "worker": worker,
                        "status": "BLOCKED",
                        "detail": str(exc),
                        "path": target.as_posix(),
                        "actions": [],
                        "base_ref_commit": base_ref_commit,
                        "worktree_mode": mode_info["worktree_mode"],
                    }
                )
                continue

            try:
                if target.exists():
                    git_dir = target / ".git"
                    head_commit = _resolve_commit("HEAD", cwd=target, dry_run=dry_run)
                    ok = git_dir.exists()
                    step_payload = {
                        "worker": worker,
                        "status": "PASS" if ok else "BLOCKED",
                        "detail": "worktree already exists" if ok else "path exists but is not a git worktree",
                        "path": target.as_posix(),
                        "actions": [],
                        "base_ref_commit": base_ref_commit,
                        "worktree_commit": head_commit,
                        "commit_match": (head_commit.get("commit") == base_ref_commit.get("commit") and ok) or dry_run,
                        "worktree_mode": mode_info["worktree_mode"],
                    }
                    steps.append(step_payload)
                    continue

                add_cmd = ["git", "worktree", "add", "--detach", target.as_posix(), base_ref]
                add_result = _run(add_cmd, dry_run=dry_run)
                worker_actions.append(add_result)

                head_commit = _resolve_commit("HEAD", cwd=target, dry_run=dry_run)
                worker_actions.append({"commit_check": head_commit})
                commit_match = head_commit.get("commit") == base_ref_commit.get("commit") or dry_run

                status = "PASS" if add_result["rc"] == 0 and commit_match else "BLOCKED"
                detail = "created" if status == "PASS" else "failed to create worktree or commit mismatch"
                steps.append(
                    {
                        "worker": worker,
                        "status": status,
                        "detail": detail,
                        "path": target.as_posix(),
                        "actions": worker_actions,
                        "base_ref_commit": base_ref_commit,
                        "worktree_commit": head_commit,
                        "commit_match": commit_match,
                        "worktree_mode": mode_info["worktree_mode"],
                    }
                )
            finally:
                worker_lock.release()
    finally:
        run_lock.release()

    blocked = [step for step in steps if step["status"] != "PASS"]
    payload = {
        "run_id": run_id,
        "operation": "create",
        "status": "PASS" if not blocked else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked),
        "lock_errors": lock_errors,
        "base_ref": base_ref,
        "base_ref_commit": base_ref_commit,
        "worktree_mode": mode_info["worktree_mode"],
        "contract_path": str(mode_info["contract_path"]),
        "branch_prefix_ignored": branch_prefix,
    }
    state_path = RUNS_DIR / run_id / "WORKTREE_STATE.json"
    write_json(state_path, payload)
    return payload


def verify_worktrees(run_id: str, *, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = workers or list(WORKERS)
    steps: list[dict[str, Any]] = []
    for worker in chosen:
        target = worktree_path(run_id, worker)
        git_dir = target / ".git"
        ok = target.exists() and git_dir.exists()
        commit_info = _resolve_commit("HEAD", cwd=target, dry_run=not ok)
        steps.append(
            {
                "worker": worker,
                "status": "PASS" if ok else "BLOCKED",
                "path": target.as_posix(),
                "git_marker": git_dir.as_posix(),
                "detail": "verified" if ok else "missing worktree or git marker",
                "head_commit": commit_info.get("commit", ""),
            }
        )
    blocked = [step for step in steps if step["status"] != "PASS"]
    return {
        "run_id": run_id,
        "operation": "verify",
        "status": "PASS" if not blocked else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked),
    }


def sync_worktrees(run_id: str, *, workers: list[str] | None = None, dry_run: bool = False) -> dict[str, Any]:
    chosen = workers or list(WORKERS)
    steps: list[dict[str, Any]] = []
    for worker in chosen:
        target = worktree_path(run_id, worker)
        if not target.exists():
            steps.append(
                {
                    "worker": worker,
                    "status": "BLOCKED",
                    "detail": "worktree does not exist",
                    "path": target.as_posix(),
                    "actions": [],
                }
            )
            continue

        actions = [
            _run(["git", "fetch", "--all", "--prune"], cwd=target, dry_run=dry_run),
            _run(["git", "status", "--porcelain=v1"], cwd=target, dry_run=dry_run),
            _resolve_commit("HEAD", cwd=target, dry_run=dry_run),
        ]
        blocked = [item for item in actions if item["rc"] != 0]
        steps.append(
            {
                "worker": worker,
                "status": "PASS" if not blocked else "BLOCKED",
                "detail": "synced" if not blocked else "sync failed",
                "path": target.as_posix(),
                "actions": actions,
            }
        )

    blocked_steps = [step for step in steps if step["status"] != "PASS"]
    return {
        "run_id": run_id,
        "operation": "sync",
        "status": "PASS" if not blocked_steps else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked_steps),
    }


def open_worktrees(run_id: str, *, workers: list[str] | None = None, dry_run: bool = False) -> dict[str, Any]:
    chosen = workers or list(WORKERS)
    steps: list[dict[str, Any]] = []
    cleanup_result = _cleanup_vscode_sessions(run_id) if not dry_run else {
        "clean_enabled": _env_enabled("HITECH_FACTORY_VSCODE_CLEAN", True),
        "nuke_enabled": _env_enabled("HITECH_FACTORY_VSCODE_NUKE", False),
        "sessions_found": 0,
        "actions": [],
        "report": _cleanup_report_path(run_id).as_posix(),
    }
    code_cli = _resolve_code_cli()
    session_entries: list[dict[str, Any]] = []
    for worker in chosen:
        target = worktree_path(run_id, worker)
        if not target.exists():
            steps.append(
                {
                    "worker": worker,
                    "status": "BLOCKED",
                    "detail": "worktree missing",
                    "path": target.as_posix(),
                    "actions": [],
                }
            )
            continue

        before_pids = _list_code_pids() if not dry_run else []
        if code_cli is None and not dry_run:
            action = {
                "cmd": ["code", target.as_posix()],
                "cwd": str(REPO_ROOT),
                "rc": 127,
                "stdout": "",
                "stderr": "code CLI command not found (resolved candidates: code.cmd, code)",
                "dry_run": False,
                "wrapper_pid": None,
            }
        else:
            command_name = code_cli if code_cli is not None else "code"
            action = _run_with_wrapper_pid([command_name, target.as_posix()], dry_run=dry_run, timeout_seconds=30.0)
        discovered_pid: int | None = None
        wrapper_pid = action.get("wrapper_pid")
        if not dry_run and action["rc"] == 0:
            discovered_pid = _resolve_code_pid_from_wrapper(
                int(wrapper_pid) if isinstance(wrapper_pid, int) else None,
                baseline_code_pids=before_pids,
                max_wait_seconds=8.0,
                poll_seconds=0.2,
            )
        action["pid"] = discovered_pid
        action["wrapper_pid"] = int(wrapper_pid) if isinstance(wrapper_pid, int) else None
        action["pid_kind"] = "Code.exe" if isinstance(discovered_pid, int) else "unresolved"
        if action["rc"] == 0:
            if isinstance(discovered_pid, int):
                step_status = "PASS"
                step_detail = "opened"
            else:
                step_status = "WARN"
                step_detail = "opened but Code.exe PID unresolved"
        elif action["rc"] == 127:
            step_status = "BLOCKED"
            step_detail = "code CLI command not found"
        elif action["rc"] == 124:
            step_status = "BLOCKED"
            step_detail = "code CLI launch timed out"
        else:
            step_status = "WARN"
            step_detail = "failed to open VS Code"
        steps.append(
            {
                "worker": worker,
                "status": step_status,
                "detail": step_detail,
                "path": target.as_posix(),
                "actions": [action],
            }
        )
        session_entries.append(
            {
                "run_id": run_id,
                "worker": worker,
                "opened_folder_path": target.as_posix(),
                "pid": discovered_pid,
                "window_handle": None,
            }
        )

    blocked_steps = [step for step in steps if step["status"] == "BLOCKED"]
    session_registry_path = _write_vscode_session_registry(run_id, sessions=session_entries)
    return {
        "run_id": run_id,
        "operation": "open",
        "status": "PASS" if not blocked_steps else "BLOCKED",
        "steps": steps,
        "blocked": len(blocked_steps),
        "cleanup": cleanup_result,
        "session_registry": session_registry_path,
    }
