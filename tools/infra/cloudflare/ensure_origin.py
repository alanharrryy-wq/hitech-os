from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from cloudflared_helpers import (
    DEFAULT_LOG_DIR,
    DEFAULT_ORIGIN_PORT,
    DEFAULT_ORIGIN_URL,
    DEFAULT_REPO_ROOT,
    RunContext,
    TunnelSetupError,
    ensure_directory,
    origin_reachable,
    read_json,
    run_logged,
    write_json,
)


def _ps_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _port_from_origin(origin_url: str) -> int:
    parsed = urlparse(origin_url)
    if parsed.port is not None:
        return parsed.port
    candidate = origin_url.rsplit(":", 1)[-1].strip("/")
    try:
        return int(candidate)
    except ValueError:
        return DEFAULT_ORIGIN_PORT


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _resolve_node_executable() -> str:
    node_from_path = shutil.which("node")
    if node_from_path:
        return node_from_path

    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "nodejs" / "node.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "nodejs" / "node.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise TunnelSetupError(
        "Node.js executable was not found. Install Node.js system-wide so origin auto-start works under SYSTEM tasks."
    )


def _launch_next_process(
    repo_root: Path,
    app_relative_path: str,
    port: int,
    runtime_log_path: Path,
) -> int:
    ensure_directory(runtime_log_path.parent)
    runtime_err_path = runtime_log_path.with_suffix(".err.log")
    node_exe = _resolve_node_executable()
    app_dir = repo_root / app_relative_path
    next_cli = app_dir / "node_modules" / "next" / "dist" / "bin" / "next"
    if not next_cli.exists():
        raise TunnelSetupError(
            f"Cannot launch origin because Next CLI is missing at '{next_cli}'. "
            "Run dependency install/build first."
        )
    cmd = [node_exe, str(next_cli), "start", "-p", str(port)]
    creationflags = 0
    if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        creationflags |= subprocess.CREATE_NEW_PROCESS_GROUP
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        creationflags |= subprocess.CREATE_NO_WINDOW
    try:
        with runtime_log_path.open("a", encoding="utf-8") as out_log, runtime_err_path.open(
            "a", encoding="utf-8"
        ) as err_log:
            proc = subprocess.Popen(
                cmd,
                cwd=str(app_dir),
                stdout=out_log,
                stderr=err_log,
                creationflags=creationflags,
                close_fds=True,
            )
    except OSError as err:
        raise TunnelSetupError(f"Failed to spawn Next process: {err}") from err
    return int(proc.pid)


def ensure_next_origin(
    ctx: RunContext,
    *,
    repo_root: Path,
    app_relative_path: str,
    app_display_name: str,
    app_build_command: str,
    origin_url: str,
    state_path: Path,
    runtime_log_path: Path,
    wait_seconds: int = 90,
    launch_cooldown_seconds: int = 120,
) -> dict[str, Any]:
    port = _port_from_origin(origin_url)
    reachable, status_code, origin_error = origin_reachable(origin_url)
    if reachable:
        payload = {
            "changed": False,
            "origin_reachable": True,
            "origin_status_code": status_code,
            "origin_error": origin_error,
            "port": port,
            "app": app_display_name,
            "app_relative_path": app_relative_path,
        }
        ctx.action("ensure_origin", "ok", payload)
        return payload

    build_id = repo_root / app_relative_path / ".next" / "BUILD_ID"
    if not build_id.exists():
        build = run_logged(
            ctx,
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"Set-Location -LiteralPath {_ps_single_quote(str(repo_root))}; {app_build_command}",
            ],
            timeout=1800,
            action_name=f"{app_display_name.lower()}_build",
        )
        if build.returncode != 0:
            raise TunnelSetupError(
                f"{app_display_name} build failed. stderr: {build.stderr.strip() or build.stdout.strip() or 'n/a'}"
            )

    state = read_json(state_path, default={})
    last_launch_epoch = float(state.get("last_launch_epoch", 0) or 0)
    existing_pid = int(state.get("pid", 0) or 0)
    now = time.time()
    port_open = _is_port_open(port)
    existing_pid_alive = existing_pid > 0 and _pid_alive(existing_pid)
    should_launch = not port_open

    launched = False
    pid = existing_pid
    if should_launch:
        if existing_pid > 0 and existing_pid_alive:
            kill_old = run_logged(
                ctx,
                ["taskkill", "/PID", str(existing_pid), "/F"],
                timeout=30,
                action_name=f"{app_display_name.lower()}_kill_stale_pid",
            )
            if kill_old.returncode != 0:
                ctx.action(
                    f"{app_display_name.lower()}_kill_stale_pid",
                    "warning",
                    {"pid": existing_pid, "stderr": kill_old.stderr.strip() or kill_old.stdout.strip() or "n/a"},
                )
            time.sleep(1)

        if existing_pid_alive and now - last_launch_epoch < launch_cooldown_seconds:
            ctx.action(
                f"{app_display_name.lower()}_launch_cooldown",
                "warning",
                {
                    "existing_pid": existing_pid,
                    "last_launch_epoch": last_launch_epoch,
                    "seconds_since_last_launch": now - last_launch_epoch,
                    "launch_cooldown_seconds": launch_cooldown_seconds,
                },
            )

        try:
            pid = _launch_next_process(repo_root, app_relative_path, port, runtime_log_path)
            launched = True
            write_json(
                state_path,
                {
                    "pid": pid,
                    "last_launch_epoch": now,
                    "last_launch_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                    "port": port,
                    "origin_url": origin_url,
                    "app": app_display_name,
                    "app_relative_path": app_relative_path,
                },
            )
        except Exception as err:  # noqa: BLE001
            raise TunnelSetupError(f"Failed to launch {app_display_name} origin: {err}") from err

    deadline = time.time() + max(wait_seconds, 1)
    final_reachable = False
    final_status = None
    final_error = None
    while time.time() < deadline:
        if _is_port_open(port):
            final_reachable, final_status, final_error = origin_reachable(origin_url)
            if final_reachable:
                break
        time.sleep(1.0)
    else:
        final_reachable, final_status, final_error = origin_reachable(origin_url)

    if not final_reachable:
        payload = {
            "changed": launched,
            "origin_reachable": False,
            "origin_status_code": final_status,
            "origin_error": final_error,
            "pid": pid,
            "port": port,
            "runtime_log_path": str(runtime_log_path),
            "state_path": str(state_path),
            "app": app_display_name,
            "app_relative_path": app_relative_path,
        }
        ctx.action("ensure_origin", "error", payload)
        raise TunnelSetupError(
            f"{app_display_name} origin is still unreachable at {origin_url}. "
            f"Inspect runtime log: {runtime_log_path}"
        )

    payload = {
        "changed": launched,
        "origin_reachable": True,
        "origin_status_code": final_status,
        "origin_error": final_error,
        "pid": pid,
        "port": port,
        "runtime_log_path": str(runtime_log_path),
        "state_path": str(state_path),
        "app": app_display_name,
        "app_relative_path": app_relative_path,
    }
    ctx.action("ensure_origin", "ok", payload)
    return payload


def ensure_keystone_origin(
    ctx: RunContext,
    *,
    repo_root: Path,
    origin_url: str,
    state_path: Path,
    runtime_log_path: Path,
    wait_seconds: int = 90,
    launch_cooldown_seconds: int = 120,
) -> dict[str, Any]:
    return ensure_next_origin(
        ctx,
        repo_root=repo_root,
        app_relative_path="apps/keystone",
        app_display_name="Keystone",
        app_build_command="pnpm -C apps/keystone build",
        origin_url=origin_url,
        state_path=state_path,
        runtime_log_path=runtime_log_path,
        wait_seconds=wait_seconds,
        launch_cooldown_seconds=launch_cooldown_seconds,
    )


def ensure_forms_origin(
    ctx: RunContext,
    *,
    repo_root: Path,
    origin_url: str,
    state_path: Path,
    runtime_log_path: Path,
    wait_seconds: int = 90,
    launch_cooldown_seconds: int = 120,
) -> dict[str, Any]:
    return ensure_next_origin(
        ctx,
        repo_root=repo_root,
        app_relative_path="apps/external_interaction_forms",
        app_display_name="ExternalInteractionForms",
        app_build_command="pnpm -C apps/external_interaction_forms build",
        origin_url=origin_url,
        state_path=state_path,
        runtime_log_path=runtime_log_path,
        wait_seconds=wait_seconds,
        launch_cooldown_seconds=launch_cooldown_seconds,
    )


def ensure_template_origin(
    ctx: RunContext,
    *,
    repo_root: Path,
    origin_url: str,
    state_path: Path,
    runtime_log_path: Path,
    wait_seconds: int = 90,
    launch_cooldown_seconds: int = 120,
) -> dict[str, Any]:
    return ensure_next_origin(
        ctx,
        repo_root=repo_root,
        app_relative_path="apps/external_interaction_template",
        app_display_name="ExternalInteractionTemplate",
        app_build_command="pnpm -C apps/external_interaction_template build",
        origin_url=origin_url,
        state_path=state_path,
        runtime_log_path=runtime_log_path,
        wait_seconds=wait_seconds,
        launch_cooldown_seconds=launch_cooldown_seconds,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure Keystone origin is running and reachable.")
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--wait-seconds", type=int, default=90)
    parser.add_argument("--launch-cooldown-seconds", type=int, default=120)
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    log_dir = Path(args.log_dir)
    ensure_directory(log_dir)
    ctx = RunContext(log_dir=log_dir, run_id=args.run_id, enable_console=True)
    state_path = log_dir / "keystone_origin_state.json"
    runtime_log_path = log_dir / "keystone_origin_runtime.log"
    try:
        payload = ensure_keystone_origin(
            ctx,
            repo_root=Path(args.repo_root),
            origin_url=args.origin_url,
            state_path=state_path,
            runtime_log_path=runtime_log_path,
            wait_seconds=args.wait_seconds,
            launch_cooldown_seconds=args.launch_cooldown_seconds,
        )
        payload["ok"] = True
    except TunnelSetupError as err:
        payload = {"ok": False, "error": str(err)}
        print(f"ERROR: {err}")
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return 2

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
