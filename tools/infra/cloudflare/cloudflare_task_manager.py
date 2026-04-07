#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_INFRA_DIR = DEFAULT_REPO_ROOT / r"tools\infra\cloudflare"
DEFAULT_SETUP_PS1 = DEFAULT_INFRA_DIR / "setup_tunnel_forever.ps1"
DEFAULT_PUBLIC_HEALTH_PS1 = DEFAULT_INFRA_DIR / "public_health_probe.ps1"

GUARD_TASK = "HITECH-Cloudflared-TunnelGuard"
PUBLIC_TASK = "HITECH-Cloudflared-PublicHealth"
FULL_TASK = "HITECH-Cloudflared-FullRepair"


def is_windows() -> bool:
    return os.name == "nt"


def quote_arg(arg: str) -> str:
    if not arg:
        return '""'
    return str(arg)


def build_pwsh_task_run(script_path: Path, extra_args: Iterable[str] = ()) -> str:
    parts = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
    ]
    parts.extend(extra_args)
    # schtasks /TR wants one command line string. Use Windows-safe quoting.
    return subprocess.list2cmdline(parts)


@dataclass
class TaskSpec:
    name: str
    task_run: str
    schedule: str  # minute or daily
    modifier: int | None = None
    start_time: str | None = None
    user: str = "SYSTEM"
    runlevel: str = "HIGHEST"
    enabled: bool = True

    def create_args(self) -> list[str]:
        args = [
            "schtasks",
            "/Create",
            "/TN",
            self.name,
            "/TR",
            self.task_run,
            "/RU",
            self.user,
            "/RL",
            self.runlevel,
            "/F",
        ]
        if self.schedule.lower() == "minute":
            args.extend(["/SC", "MINUTE", "/MO", str(self.modifier or 5)])
        elif self.schedule.lower() == "daily":
            args.extend(["/SC", "DAILY", "/ST", str(self.start_time or "03:15")])
        else:
            raise ValueError(f"Unsupported schedule: {self.schedule}")
        return args


def run(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(args, capture_output=True, text=True, shell=False)
    if check and cp.returncode != 0:
        raise RuntimeError(
            f"Command failed ({cp.returncode}): {' '.join(shlex.quote(a) for a in args)}\n"
            f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        )
    return cp


def task_exists(name: str) -> bool:
    cp = run(["schtasks", "/Query", "/TN", name])
    return cp.returncode == 0


def create_or_update_task(spec: TaskSpec) -> dict:
    cp = run(spec.create_args())
    ok = cp.returncode == 0
    if ok and spec.enabled:
        run(["schtasks", "/Change", "/TN", spec.name, "/ENABLE"])
    return {
        "task": spec.name,
        "ok": ok,
        "changed": ok,
        "returncode": cp.returncode,
        "stdout": cp.stdout.strip(),
        "stderr": cp.stderr.strip(),
        "task_run": spec.task_run,
    }


def delete_task(name: str) -> dict:
    if not task_exists(name):
        return {"task": name, "ok": True, "changed": False, "message": "not installed"}
    cp = run(["schtasks", "/Delete", "/TN", name, "/F"])
    return {
        "task": name,
        "ok": cp.returncode == 0,
        "changed": cp.returncode == 0,
        "returncode": cp.returncode,
        "stdout": cp.stdout.strip(),
        "stderr": cp.stderr.strip(),
    }


def run_now(name: str) -> dict:
    cp = run(["schtasks", "/Run", "/TN", name])
    return {
        "task": name,
        "ok": cp.returncode == 0,
        "returncode": cp.returncode,
        "stdout": cp.stdout.strip(),
        "stderr": cp.stderr.strip(),
    }


def inspect_task(name: str) -> dict:
    cp = run(["schtasks", "/Query", "/TN", name, "/V", "/FO", "LIST"])
    payload: dict[str, str | bool | int] = {
        "task": name,
        "installed": cp.returncode == 0,
        "returncode": cp.returncode,
        "stdout": cp.stdout.strip(),
        "stderr": cp.stderr.strip(),
    }
    if cp.returncode != 0:
        return payload
    for line in cp.stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip()
    return payload


def require_admin() -> None:
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise PermissionError("Run this script from an elevated PowerShell (Admin).")
    except Exception as exc:
        if isinstance(exc, PermissionError):
            raise
        # If admin check fails oddly, keep going; schtasks will still error clearly.


def build_specs(repo_root: Path, guard_minutes: int, public_minutes: int, with_full_daily: bool, full_time: str) -> list[TaskSpec]:
    infra = repo_root / r"tools\infra\cloudflare"
    setup = infra / "setup_tunnel_forever.ps1"
    public_probe = infra / "public_health_probe.ps1"
    specs = [
        TaskSpec(
            name=GUARD_TASK,
            task_run=build_pwsh_task_run(setup, ["-GuardOnly"]),
            schedule="minute",
            modifier=guard_minutes,
        ),
        TaskSpec(
            name=PUBLIC_TASK,
            task_run=build_pwsh_task_run(public_probe),
            schedule="minute",
            modifier=public_minutes,
        ),
    ]
    if with_full_daily:
        specs.append(
            TaskSpec(
                name=FULL_TASK,
                task_run=build_pwsh_task_run(setup),
                schedule="daily",
                start_time=full_time,
            )
        )
    return specs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Install/update/query Cloudflare tunnel scheduled tasks for HITECH-OS.")
    p.add_argument("command", choices=["install", "status", "run-now", "remove"], help="Action to perform")
    p.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT), help="Monorepo root")
    p.add_argument("--guard-minutes", type=int, default=5, help="Interval in minutes for GuardOnly task")
    p.add_argument("--public-minutes", type=int, default=5, help="Interval in minutes for public health task")
    p.add_argument("--with-full-daily", action="store_true", help="Also install a daily full repair/validation task")
    p.add_argument("--full-time", default="03:15", help="Daily time for the full repair task (HH:MM)")
    p.add_argument("--no-public", action="store_true", help="Do not manage the public health task")
    p.add_argument("--task", choices=["guard", "public", "full", "all"], default="all", help="Task subset for status/run-now/remove")
    p.add_argument("--json", action="store_true", help="Print JSON only")
    return p.parse_args()


def task_names_from_selector(selector: str, include_full: bool = True) -> list[str]:
    mapping = {
        "guard": [GUARD_TASK],
        "public": [PUBLIC_TASK],
        "full": [FULL_TASK],
        "all": [GUARD_TASK, PUBLIC_TASK] + ([FULL_TASK] if include_full else []),
    }
    return mapping[selector]


def main() -> int:
    if not is_windows():
        print("This script is for Windows only.", file=sys.stderr)
        return 2

    args = parse_args()
    repo_root = Path(args.repo_root)
    require_admin()

    specs = build_specs(
        repo_root=repo_root,
        guard_minutes=max(1, int(args.guard_minutes)),
        public_minutes=max(1, int(args.public_minutes)),
        with_full_daily=bool(args.with_full_daily),
        full_time=str(args.full_time),
    )
    if args.no_public:
        specs = [s for s in specs if s.name != PUBLIC_TASK]

    available_names = {s.name for s in specs}
    all_possible = {GUARD_TASK, PUBLIC_TASK, FULL_TASK}

    results: list[dict] = []

    try:
        if args.command == "install":
            for spec in specs:
                results.append(create_or_update_task(spec))
        elif args.command == "status":
            selector = args.task
            names = task_names_from_selector(selector, include_full=True)
            for name in names:
                if name in all_possible:
                    results.append(inspect_task(name))
        elif args.command == "run-now":
            names = task_names_from_selector(args.task, include_full=True)
            for name in names:
                results.append(run_now(name))
        elif args.command == "remove":
            names = task_names_from_selector(args.task, include_full=True)
            for name in names:
                results.append(delete_task(name))
    except Exception as exc:
        payload = {"ok": False, "error": str(exc), "results": results}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
            if results:
                print(json.dumps(results, indent=2, ensure_ascii=False))
        return 2

    ok = all(bool(r.get("ok", False) or r.get("installed", False) or r.get("changed", False) is False) for r in results)
    payload = {"ok": ok, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
