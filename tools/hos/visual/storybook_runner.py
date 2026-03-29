#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
import os
import signal
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.exec import run_command
from tools.hos._core.repo_root import find_repo_root
from tools.hos.visual.storybook_detect import detect_storybook_workspaces


@dataclass
class StorybookProcess:
    process: subprocess.Popen[str]
    workspace: str
    port: int
    command: tuple[str, ...]


def _wait_for_http(url: str, timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.0) as response:
                if 200 <= response.status < 500:
                    return True
        except urllib.error.URLError:
            time.sleep(0.6)
    return False


def _candidate_commands(package_name: str, port: int) -> list[list[str]]:
    return [
        ["pnpm", "--filter", package_name, "exec", "storybook", "dev", "--ci", "-p", str(port)],
        ["pnpm", "--filter", package_name, "run", "storybook", "--", "--ci", "-p", str(port)],
    ]


def start_storybook(
    repo_root: Path,
    workspace_name: str,
    package_name: str,
    port: int,
    timeout_seconds: float = 60.0,
) -> StorybookProcess:
    for command in _candidate_commands(package_name=package_name, port=port):
        proc = subprocess.Popen(
            command,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=dict(os.environ),
        )
        url = f"http://127.0.0.1:{port}/"
        if _wait_for_http(url=url, timeout_seconds=timeout_seconds):
            return StorybookProcess(
                process=proc,
                workspace=workspace_name,
                port=port,
                command=tuple(command),
            )
        stop_storybook(proc)

    raise RuntimeError(f"failed to start storybook for workspace={workspace_name}")


def stop_storybook(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=10)
    except Exception:  # noqa: BLE001
        try:
            process.kill()
        except Exception:  # noqa: BLE001
            return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start/stop Storybook for visual tooling.")
    parser.add_argument("--port", type=int, default=6007, help="Fixed Storybook port.")
    parser.add_argument("--workspace", default="", help="Workspace path override (optional).")
    parser.add_argument("--package-name", default="", help="Package name override (optional).")
    parser.add_argument("--timeout", type=float, default=60.0, help="Startup timeout in seconds.")
    parser.add_argument("--check-only", action="store_true", help="Only detect, do not start process.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    matches = detect_storybook_workspaces(repo_root=repo_root)
    if not matches:
        print("[storybook_runner] no storybook workspace detected.")
        return 1

    if args.workspace and args.package_name:
        workspace = args.workspace
        package = args.package_name
    else:
        first = matches[0]
        workspace = first.workspace_path
        package = first.package_name

    print(f"[storybook_runner] selected workspace={workspace} package={package} port={args.port}")
    if args.check_only:
        return 0

    sb = start_storybook(
        repo_root=repo_root,
        workspace_name=workspace,
        package_name=package,
        port=args.port,
        timeout_seconds=args.timeout,
    )
    print(f"[storybook_runner] started pid={sb.process.pid} command={' '.join(sb.command)}")
    try:
        while True:
            if sb.process.poll() is not None:
                print(f"[storybook_runner] exited rc={sb.process.returncode}")
                return sb.process.returncode or 0
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("[storybook_runner] stopping...")
        stop_storybook(sb.process)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
