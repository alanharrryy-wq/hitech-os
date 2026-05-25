from __future__ import annotations

import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config_loader import LOG_ROOT, load_safety_policy, load_state, save_state
from ports_inspector import process_exists
from process_classifier import classify_process


CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
DETACHED_PROCESS = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def stop_process_safely(owner: dict[str, Any], action: str, service_id: str | None, timeline: list[dict[str, Any]]) -> dict[str, Any]:
    classification = classify_process(owner, action=action, service_id=service_id)
    pid = int(owner.get("pid") or 0)
    result = {
        "pid": pid,
        "action": "stop-process",
        "classification": classification,
        "status": "SKIPPED",
        "message": "",
    }
    if not classification.get("allowedToStop"):
        result["status"] = "BLOCKED_UNKNOWN_PROCESS"
        result["message"] = classification.get("reason", "Process is not safe to stop.")
        timeline.append({"time": now_iso(), "event": "blocked-stop", "detail": result})
        return result

    policy = load_safety_policy()
    if policy.get("dryRun", False):
        result["status"] = "DRY_RUN"
        result["message"] = "Dry-run enabled; process was not stopped."
        timeline.append({"time": now_iso(), "event": "dry-run-stop", "detail": result})
        return result

    graceful_timeout = int(policy.get("gracefulStopTimeoutSeconds", 8))
    kill_timeout = int(policy.get("killTimeoutSeconds", 5))
    subprocess.run(
        ["taskkill.exe", "/PID", str(pid), "/T"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=graceful_timeout + 5,
    )
    deadline = time.time() + graceful_timeout
    while time.time() < deadline:
        if not process_exists(pid):
            result["status"] = "STOPPED_GRACEFULLY"
            result["message"] = "Process stopped without force."
            timeline.append({"time": now_iso(), "event": "stopped-process", "detail": result})
            return result
        time.sleep(0.5)
    subprocess.run(
        ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=kill_timeout + 5,
    )
    result["status"] = "FORCE_STOPPED"
    result["message"] = "Process required force stop after graceful timeout."
    timeline.append({"time": now_iso(), "event": "force-stopped-process", "detail": result})
    return result


def register_managed_process(service_id: str, pid: int, command: str, cwd: str, log_path: str) -> None:
    state = load_state()
    entries = [item for item in state.get("managedProcesses", []) if int(item.get("pid", 0) or 0) != int(pid)]
    entries.append(
        {
            "serviceId": service_id,
            "pid": int(pid),
            "command": command,
            "cwd": cwd,
            "logPath": log_path,
            "startedAt": now_iso(),
        }
    )
    state["managedProcesses"] = entries[-80:]
    save_state(state)


def start_detached_process(service_id: str, command: str, cwd: str, env_extra: dict[str, str] | None = None) -> dict[str, Any]:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_ROOT / f"service_{service_id}_{stamp}.log"
    env = os.environ.copy()
    env["PRISMA_CONTROL_CENTER"] = "1"
    env["PRISMA_CONTROL_CENTER_SERVICE_ID"] = service_id
    if env_extra:
        env.update(env_extra)
    cwd_path = Path(cwd)
    if not cwd_path.exists():
        return {
            "status": "FAILED",
            "pid": 0,
            "logPath": str(log_path),
            "message": f"cwd does not exist: {cwd}",
        }
    handle = log_path.open("ab")
    process = subprocess.Popen(
        command,
        cwd=str(cwd_path),
        stdout=handle,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        shell=True,
        env=env,
        creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,
    )
    register_managed_process(service_id, process.pid, command, str(cwd_path), str(log_path))
    return {
        "status": "STARTED",
        "pid": int(process.pid),
        "logPath": str(log_path),
        "message": "Process started and registered.",
    }


def run_command_capture(command: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return {
            "command": command,
            "returnCode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "timedOut": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returnCode": 124,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
            "timedOut": True,
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returnCode": 127,
            "stdout": "",
            "stderr": str(exc),
            "timedOut": False,
        }
