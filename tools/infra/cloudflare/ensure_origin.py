from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_LOG_DIR,
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
    if ":" not in origin_url:
        return 3000
    candidate = origin_url.rsplit(":", 1)[-1].strip("/")
    try:
        return int(candidate)
    except ValueError:
        return 3000


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


def _launch_keystone_process(repo_root: Path, port: int, runtime_log_path: Path) -> int:
    ensure_directory(runtime_log_path.parent)
    runtime_err_path = runtime_log_path.with_suffix(".err.log")
    startup_cmd = (
        f"Set-Location -LiteralPath {_ps_single_quote(str(repo_root))}; "
        f"pnpm --filter @hitech/keystone exec next start -p {port}"
    )
    ps_command = (
        f"$argList = @('-NoProfile','-ExecutionPolicy','Bypass','-Command',{_ps_single_quote(startup_cmd)}); "
        f"$p = Start-Process -FilePath 'pwsh' -ArgumentList $argList "
        f"-WorkingDirectory {_ps_single_quote(str(repo_root))} "
        f"-WindowStyle Hidden "
        f"-RedirectStandardOutput {_ps_single_quote(str(runtime_log_path))} "
        f"-RedirectStandardError {_ps_single_quote(str(runtime_err_path))} "
        "-PassThru; "
        "if ($null -eq $p) { exit 9001 }; "
        "Write-Output $p.Id"
    )
    launched = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if launched.returncode != 0:
        raise TunnelSetupError(
            f"Failed to spawn Keystone process. stderr: {launched.stderr.strip() or launched.stdout.strip() or 'n/a'}"
        )
    pid_text = (launched.stdout or "").strip().splitlines()
    if not pid_text:
        raise TunnelSetupError("Keystone process spawn returned no PID.")
    try:
        return int(pid_text[-1].strip())
    except ValueError as err:
        raise TunnelSetupError(f"Unexpected PID output while starting Keystone: {launched.stdout!r}") from err


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
    port = _port_from_origin(origin_url)
    reachable, status_code, origin_error = origin_reachable(origin_url)
    if reachable:
        payload = {
            "changed": False,
            "origin_reachable": True,
            "origin_status_code": status_code,
            "origin_error": origin_error,
            "port": port,
        }
        ctx.action("ensure_origin", "ok", payload)
        return payload

    build_id = repo_root / "apps" / "keystone" / ".next" / "BUILD_ID"
    if not build_id.exists():
        build = run_logged(
            ctx,
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"Set-Location -LiteralPath {_ps_single_quote(str(repo_root))}; pnpm --filter @hitech/keystone build",
            ],
            timeout=1800,
            action_name="keystone_build",
        )
        if build.returncode != 0:
            raise TunnelSetupError(
                f"Keystone build failed. stderr: {build.stderr.strip() or build.stdout.strip() or 'n/a'}"
            )

    state = read_json(state_path, default={})
    last_launch_epoch = float(state.get("last_launch_epoch", 0) or 0)
    existing_pid = int(state.get("pid", 0) or 0)
    now = time.time()
    should_launch = True
    if existing_pid > 0 and _pid_alive(existing_pid):
        # Existing process still alive; likely warming up.
        should_launch = False
    if now - last_launch_epoch < launch_cooldown_seconds:
        should_launch = False

    launched = False
    pid = existing_pid
    if should_launch:
        try:
            pid = _launch_keystone_process(repo_root, port, runtime_log_path)
            launched = True
            write_json(
                state_path,
                {
                    "pid": pid,
                    "last_launch_epoch": now,
                    "last_launch_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                    "port": port,
                    "origin_url": origin_url,
                },
            )
        except Exception as err:  # noqa: BLE001
            raise TunnelSetupError(f"Failed to launch Keystone origin: {err}") from err

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
        }
        ctx.action("ensure_origin", "error", payload)
        raise TunnelSetupError(
            f"Keystone origin is still unreachable at {origin_url}. "
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
    }
    ctx.action("ensure_origin", "ok", payload)
    return payload


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
