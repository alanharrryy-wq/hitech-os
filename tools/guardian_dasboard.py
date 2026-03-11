#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def _hide_console_window() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        return


def _is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.7):
            return True
    except OSError:
        return False


def _resolve_pythonw() -> str:
    current = Path(sys.executable)
    sibling = current.with_name("pythonw.exe")
    if sibling.exists():
        return str(sibling)
    in_path = shutil.which("pythonw")
    if in_path:
        return in_path
    return str(current)


def _build_dashboard_command(repo_root: Path, host: str, port: int, profile: str, open_browser: bool) -> list[str]:
    dashboard_script = repo_root / "tools" / "hos" / "git_sentinel" / "dashboard_app.py"
    python_bin = _resolve_pythonw()
    cmd = [
        python_bin,
        str(dashboard_script),
        "--host",
        host,
        "--port",
        str(port),
        "--profile",
        profile,
    ]
    if open_browser:
        cmd.append("--open-browser")
    return cmd


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardian Dashboard one-click launcher.")
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard host.")
    parser.add_argument("--port", type=int, default=8787, help="Dashboard port.")
    parser.add_argument("--profile", default="strict", choices=("safe", "strict", "aggressive"), help="Sentinel profile.")
    parser.add_argument("--foreground", action="store_true", help="Run in current process (debug mode).")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser.")
    parser.add_argument("--status", action="store_true", help="Print dashboard status and exit.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    host = str(args.host)
    port = int(args.port)

    if args.status:
        state = "running" if _is_port_open(host=host, port=port) else "stopped"
        print(f"guardian_dashboard status={state} host={host} port={port}")
        return 0

    if _is_port_open(host=host, port=port):
        if not args.no_browser:
            import webbrowser

            webbrowser.open(f"http://{host}:{port}/")
        return 0

    command = _build_dashboard_command(
        repo_root=repo_root,
        host=host,
        port=port,
        profile=str(args.profile),
        open_browser=not args.no_browser,
    )

    if args.foreground:
        return subprocess.call(command, cwd=str(repo_root))

    _hide_console_window()
    creation_flags = 0
    if os.name == "nt":
        creation_flags = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )

    subprocess.Popen(
        command,
        cwd=str(repo_root),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=creation_flags,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
