#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_INFRA_DIR = DEFAULT_REPO_ROOT / r"tools\infra\cloudflare"
DEFAULT_LOG_DIR = Path(r"F:\descargasf")
DEFAULT_SETUP_PS1 = DEFAULT_INFRA_DIR / "setup_tunnel_forever.ps1"
DEFAULT_PUBLIC_HEALTH_PS1 = DEFAULT_INFRA_DIR / "public_health_probe.ps1"

GUARD_TASK = "HITECH-Cloudflared-TunnelGuard"
PUBLIC_TASK = "HITECH-Cloudflared-PublicHealth"
FULL_TASK = "HITECH-Cloudflared-FullRepair"


def is_windows() -> bool:
    return os.name == "nt"


def require_admin() -> None:
    if not ctypes.windll.shell32.IsUserAnAdmin():
        raise PermissionError("Run this script from an elevated PowerShell (Admin).")


def ensure_path_exists(path: Path, *, kind: str) -> None:
    if kind == "dir":
        path.mkdir(parents=True, exist_ok=True)
        return
    if not path.exists():
        raise FileNotFoundError(str(path))


def run(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(args, capture_output=True, text=True, shell=False)
    if check and cp.returncode != 0:
        raise RuntimeError(
            f"Command failed ({cp.returncode}): {' '.join(args)}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        )
    return cp


def build_pwsh_logged_task_run(script_path: Path, log_path: Path, extra_args: Iterable[str] = ()) -> str:
    arg_string = " ".join(f"'{str(a).replace("'", "''")}'" if (" " in str(a) or "'" in str(a)) else str(a) for a in extra_args)
    if arg_string:
        arg_string = " " + arg_string
    command = (
        f"$ErrorActionPreference='Continue'; "
        f"$log='{str(log_path).replace("'", "''")}'; "
        f"New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($log)) | Out-Null; "
        f"\"==== RUN $(Get-Date -Format o) ====\" | Out-File -FilePath $log -Append -Encoding utf8; "
        f"& '{str(script_path).replace("'", "''")}'{arg_string} *>> $log; "
        f"$rc=$LASTEXITCODE; if($null -eq $rc){{ $rc=0 }}; "
        f"\"EXIT_CODE=$rc\" | Out-File -FilePath $log -Append -Encoding utf8; "
        f"exit $rc"
    )
    parts = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        command,
    ]
    return subprocess.list2cmdline(parts)


@dataclass
class TaskSpec:
    name: str
    task_run: str
    log_path: str
    schedule: str
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


def task_exists(name: str) -> bool:
    return run(["schtasks", "/Query", "/TN", name]).returncode == 0


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
        "log_path": spec.log_path,
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


def task_names_from_selector(selector: str) -> list[str]:
    mapping = {
        "guard": [GUARD_TASK],
        "public": [PUBLIC_TASK],
        "full": [FULL_TASK],
        "all": [GUARD_TASK, PUBLIC_TASK, FULL_TASK],
    }
    return mapping[selector]


def build_specs(
    repo_root: Path,
    log_dir: Path,
    guard_minutes: int,
    public_minutes: int,
    with_full_daily: bool,
    full_time: str,
) -> list[TaskSpec]:
    infra = repo_root / r"tools\infra\cloudflare"
    setup = infra / "setup_tunnel_forever.ps1"
    public_probe = infra / "public_health_probe.ps1"
    ensure_path_exists(setup, kind="file")
    ensure_path_exists(public_probe, kind="file")
    ensure_path_exists(log_dir, kind="dir")

    specs = [
        TaskSpec(
            name=GUARD_TASK,
            task_run=build_pwsh_logged_task_run(setup, log_dir / "cloudflare_tunnel_guard.log", ["-GuardOnly"]),
            log_path=str(log_dir / "cloudflare_tunnel_guard.log"),
            schedule="minute",
            modifier=max(1, guard_minutes),
        ),
        TaskSpec(
            name=PUBLIC_TASK,
            task_run=build_pwsh_logged_task_run(public_probe, log_dir / "cloudflare_public_health.log"),
            log_path=str(log_dir / "cloudflare_public_health.log"),
            schedule="minute",
            modifier=max(1, public_minutes),
        ),
    ]
    if with_full_daily:
        specs.append(
            TaskSpec(
                name=FULL_TASK,
                task_run=build_pwsh_logged_task_run(setup, log_dir / "cloudflare_full_repair.log"),
                log_path=str(log_dir / "cloudflare_full_repair.log"),
                schedule="daily",
                start_time=full_time,
            )
        )
    return specs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Install/update/query Cloudflare tunnel scheduled tasks for HITECH-OS.")
    p.add_argument("command", choices=["install", "status", "run-now", "remove"])
    p.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    p.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    p.add_argument("--guard-minutes", type=int, default=5)
    p.add_argument("--public-minutes", type=int, default=5)
    p.add_argument("--with-full-daily", action="store_true")
    p.add_argument("--full-time", default="03:15")
    p.add_argument("--no-public", action="store_true")
    p.add_argument("--task", choices=["guard", "public", "full", "all"], default="all")
    p.add_argument("--run-after-install", action="store_true")
    p.add_argument("--json", action="store_true")
    return p.parse_args()


def main() -> int:
    if not is_windows():
        print("This script is for Windows only.", file=sys.stderr)
        return 2

    args = parse_args()
    require_admin()

    repo_root = Path(args.repo_root)
    log_dir = Path(args.log_dir)
    ensure_path_exists(repo_root, kind="dir")
    ensure_path_exists(log_dir, kind="dir")

    results: list[dict] = []

    if args.command == "install":
        specs = build_specs(
            repo_root=repo_root,
            log_dir=log_dir,
            guard_minutes=max(1, int(args.guard_minutes)),
            public_minutes=max(1, int(args.public_minutes)),
            with_full_daily=bool(args.with_full_daily),
            full_time=str(args.full_time),
        )
        if args.no_public:
            specs = [s for s in specs if s.name != PUBLIC_TASK]
        for spec in specs:
            results.append(create_or_update_task(spec))
        if args.run_after_install:
            for spec in specs:
                results.append({"run_now": run_now(spec.name)})
    elif args.command == "status":
        for name in task_names_from_selector(args.task):
            results.append(inspect_task(name))
    elif args.command == "run-now":
        for name in task_names_from_selector(args.task):
            results.append(run_now(name))
    elif args.command == "remove":
        for name in task_names_from_selector(args.task):
            results.append(delete_task(name))

    payload = {"ok": all(bool(item.get("ok", True)) for item in results), "results": results}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
