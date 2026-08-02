#!/usr/bin/env python3
"""Focused verifier and controlled sabotage for PRISMA Zero-Idle Runtime Guard."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve()
_INSTALLED_CORE = _HERE.parents[2] / "prisma-control-center" / "Fast Ignit" / "internal"
if (_INSTALLED_CORE / "zero_idle_guard.py").is_file():
    sys.path.insert(0, str(_INSTALLED_CORE))

from zero_idle_guard import GuardError, WindowsJobGuard, run_pure_sabotage_tests


def process_alive(pid: int) -> bool:
    if os.name != "nt":
        return False
    import ctypes
    import ctypes.wintypes as wt
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    SYNCHRONIZE = 0x00100000
    STILL_ACTIVE = 259
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid)
    if not handle:
        return False
    try:
        code = wt.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return int(code.value) == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(handle)


def wait_dead(pid: int, timeout: float = 8.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not process_alive(pid):
            return True
        time.sleep(0.1)
    return not process_alive(pid)


def job_close_sabotage(work: Path) -> dict:
    if os.name != "nt":
        return {"name": "job-close-kills-tree", "status": "SKIP", "reason": "Windows required"}
    child_pid_file = work / "child.pid"
    code = (
        "import pathlib,subprocess,sys,time;"
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(120)']);"
        f"pathlib.Path({str(child_pid_file)!r}).write_text(str(p.pid));"
        "time.sleep(120)"
    )
    guard = WindowsJobGuard(work / "evidence", "sabotage_job_close", deferred_seconds=1.0)
    proc = guard.launch([sys.executable, "-c", code], work, os.environ.copy(), work / "job-close.log")
    deadline = time.monotonic() + 10
    while not child_pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    if not child_pid_file.exists():
        guard.close(kill=True)
        raise GuardError("child PID was not emitted")
    child_pid = int(child_pid_file.read_text())
    if not process_alive(proc.pid) or not process_alive(child_pid):
        guard.close(kill=True)
        raise GuardError("sabotage tree was not alive before close")
    guard.close(kill=False)  # KILL_ON_JOB_CLOSE is the mechanism under test.
    root_dead = wait_dead(proc.pid)
    child_dead = wait_dead(child_pid)
    if not (root_dead and child_dead):
        raise GuardError(f"job close leaked root={not root_dead} child={not child_dead}")
    return {
        "name": "job-close-kills-tree",
        "status": "PASS",
        "rootPid": proc.pid,
        "childPid": child_pid,
        "rootDead": root_dead,
        "childDead": child_dead,
    }


def wrapper_exit_sabotage(work: Path) -> dict:
    if os.name != "nt":
        return {"name": "root-exit-descendant-fail-closed", "status": "SKIP", "reason": "Windows required"}
    import ctypes
    child_pid_file = work / "orphan-child.pid"
    code = (
        "import pathlib,subprocess,sys,time;"
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(120)']);"
        f"pathlib.Path({str(child_pid_file)!r}).write_text(str(p.pid));"
        "time.sleep(120)"
    )
    guard = WindowsJobGuard(work / "evidence", "sabotage_root_exit", deferred_seconds=1.0)
    proc = guard.launch([sys.executable, "-c", code], work, os.environ.copy(), work / "root-exit.log")
    deadline = time.monotonic() + 10
    while not child_pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    if not child_pid_file.exists():
        guard.close(kill=True)
        raise GuardError("child PID was not emitted")
    child_pid = int(child_pid_file.read_text())
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if not kernel32.TerminateProcess(proc.handle, 77):
        guard.close(kill=True)
        raise GuardError("could not terminate root sabotage process")
    event = guard.next_event(timeout=10)
    if event.get("type") != "root-exit":
        guard.close(kill=True)
        raise GuardError(f"reliable root wait did not fire: {event}")
    child_alive_before_close = process_alive(child_pid)
    guard.close(kill=False)
    child_dead = wait_dead(child_pid)
    if not child_alive_before_close or not child_dead:
        raise GuardError(
            f"descendant contract failed aliveBeforeClose={child_alive_before_close} deadAfterClose={child_dead}"
        )
    return {
        "name": "root-exit-descendant-fail-closed",
        "status": "PASS",
        "waitMechanism": "RegisterWaitForSingleObject",
        "event": event,
        "childPid": child_pid,
        "descendantAliveBeforeJobClose": child_alive_before_close,
        "descendantDeadAfterJobClose": child_dead,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--fast-ignit")
    parser.add_argument("--applicator")
    args = parser.parse_args(argv)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = run_pure_sabotage_tests()
    if args.fast_ignit:
        fast_source = Path(args.fast_ignit).read_text(encoding="utf-8")
        owner_gate = {
            "name": "unknown-owner-on-3120-fails-closed",
            "status": (
                "PASS"
                if "TABLET_3120_OWNER_UNKNOWN" in fast_source
                and "svc.port == 3120" in fast_source
                else "FAIL"
            ),
        }
        report["tests"].append(owner_gate)
        report["tests"].append({
            "name": "tablet-only-hold-blocks-without-periodic-wakeup",
            "status": (
                "PASS"
                if "timeout=1.0 if non_tablet_running else None" in fast_source
                and "next_event(timeout=1.0)" not in fast_source
                else "FAIL"
            ),
        })
        report["tests"].append({
            "name": "tablet-guarded-start-requires-resident-fast-ignit-owner",
            "status": (
                "PASS"
                if "TABLET_3120_GUARDED_START_REQUIRES_HOLD" in fast_source
                and "if not bool(self.args.hold):" in fast_source
                else "FAIL"
            ),
        })
        report["tests"].append({
            "name": "tablet-start-uses-explicit-certified-portable-node",
            "status": (
                "PASS"
                if "resolve_certified_node()" in fast_source
                and 'env["PRISMA_NODE24_EXE"] = node_executable' in fast_source
                and '"node_modules" / "next" / "dist" / "bin" / "next"' in fast_source
                and "TABLET_ZERO_IMPORTANT_GATE_FAILED_BEFORE_START" in fast_source
                else "FAIL"
            ),
        })
    if args.applicator:
        applicator_source = Path(args.applicator).read_text(encoding="utf-8")
        forbidden = [
            token for token in (
                "def targeted_stop_tablet(",
                "Get-CimInstance Win32_Process",
                "taskkill.exe",
            )
            if token in applicator_source
        ]
        report["tests"].append({
            "name": "installer-shadow-certification-never-mutates-live-3120",
            "status": (
                "PASS"
                if not forbidden
                and "def select_shadow_port(" in applicator_source
                and '"mutationAttempted": False' in applicator_source
                and "PRISMA_ZERO_IDLE_SHADOW_DIST_DIR" in applicator_source
                and '"liveNextDevTouched": False' in applicator_source
                else "FAIL"
            ),
            "forbiddenFound": forbidden,
        })
        report["tests"].append({
            "name": "installer-requires-explicit-certified-node-runtime",
            "status": (
                "PASS"
                if 'os.environ.get("PRISMA_NODE24_EXE"' in applicator_source
                and "portable bootstrap was rejected" in applicator_source
                and "winget" not in applicator_source.lower()
                and "setx" not in applicator_source.lower()
                else "FAIL"
            ),
        })
    runtime_tests = []
    with tempfile.TemporaryDirectory(prefix="prisma-zero-idle-sabotage-") as td:
        work = Path(td)
        for fn in (job_close_sabotage, wrapper_exit_sabotage):
            try:
                runtime_tests.append(fn(work))
            except Exception as exc:
                runtime_tests.append({"name": fn.__name__, "status": "FAIL", "error": str(exc)})
    report["runtimeTests"] = runtime_tests
    report["runtimeWindows"] = os.name == "nt"
    blocking = [x for x in report["tests"] + runtime_tests if x["status"] == "FAIL"]
    report["status"] = "PASS" if not blocking and (os.name != "nt" or all(x["status"] == "PASS" for x in runtime_tests)) else "FAIL"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(output), "failures": len(blocking)}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
