from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_LOG_DIR,
    DEFAULT_TUNNEL_NAME,
    RunContext,
    TunnelSetupError,
    cloudflared,
    ensure_cloudflared_available,
    is_windows_admin,
    read_json,
    run_logged,
    run_python_elevated,
    service_status_snapshot,
    write_json,
)


SERVICE_NAME = "cloudflared"


def get_service_status(ctx: RunContext) -> dict[str, Any]:
    status = service_status_snapshot()
    status.setdefault("service_name", SERVICE_NAME)
    status.setdefault("installed", False)
    status.setdefault("status", "Unknown")
    status.setdefault("start_mode", "Unknown")
    status.setdefault("state", "Unknown")
    status.setdefault("path_name", "")
    ctx.action("service_status", "ok", status)
    return status


def _status_is_running(status: dict[str, Any]) -> bool:
    return str(status.get("status", "")).lower() == "running" or str(status.get("state", "")).lower() == "running"


def _status_is_auto(status: dict[str, Any]) -> bool:
    return str(status.get("start_mode", "")).lower() in {"auto", "automatic"}


def _status_has_tunnel_command(status: dict[str, Any], tunnel_name: str, config_path: Path) -> bool:
    path_name = str(status.get("path_name", "") or "").lower()
    if not path_name:
        return False
    return (
        ("tunnel run" in path_name)
        and (tunnel_name.lower() in path_name)
        and ("--config" in path_name)
        and (str(config_path).lower() in path_name)
    )


def _status_is_transitional(status: dict[str, Any]) -> bool:
    text = f"{status.get('status', '')} {status.get('state', '')}".lower().replace(" ", "")
    return any(
        marker in text
        for marker in ("stoppending", "startpending", "pausepending", "continuepending")
    )


def _recover_transitional_service_state(ctx: RunContext) -> None:
    kill = run_logged(
        ctx,
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='cloudflared.exe'\" | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
        ],
        timeout=90,
        action_name="service_kill_cloudflared_processes",
    )
    if kill.returncode != 0:
        ctx.action(
            "service_kill_cloudflared_processes",
            "warning",
            {"stderr": kill.stderr.strip() or kill.stdout.strip() or "n/a"},
        )
    time.sleep(2)


def _apply_service_changes_local(
    ctx: RunContext,
    *,
    tunnel_name: str,
    config_path: Path,
    status_before: dict[str, Any],
) -> dict[str, Any]:
    if not config_path.exists():
        raise TunnelSetupError(
            f"Cannot install service without config file '{config_path}'. Run ensure_config first."
        )

    changed = False
    installed = bool(status_before.get("installed", False))
    cloudflared_exe = ensure_cloudflared_available(ctx)

    if installed and _status_is_transitional(status_before):
        _recover_transitional_service_state(ctx)
        changed = True
        status_before = get_service_status(ctx)
    if not installed:
        install = cloudflared(ctx, ["service", "install"], timeout=240)
        combined = f"{install.stdout}\n{install.stderr}".lower()
        if install.returncode != 0 and "already" not in combined:
            raise TunnelSetupError(
                f"cloudflared service install failed. stderr: {install.stderr.strip() or install.stdout.strip() or 'n/a'}"
            )
        changed = True
        time.sleep(2)
        recheck = get_service_status(ctx)
        if not bool(recheck.get("installed", False)):
            raise TunnelSetupError(
                "cloudflared service install reported success but service was not registered. "
                "Run setup again with elevated permissions."
            )
        status_before = recheck

    if not _status_has_tunnel_command(status_before, tunnel_name, config_path):
        desired_image_path = f'"{cloudflared_exe}" --config "{config_path}" tunnel run {tunnel_name}'
        set_path = run_logged(
            ctx,
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "$desired = "
                    + "'" + desired_image_path.replace("'", "''") + "'; "
                    "Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\cloudflared' "
                    "-Name ImagePath -Value $desired -ErrorAction Stop"
                ),
            ],
            timeout=90,
            action_name="service_set_image_path",
        )
        if set_path.returncode != 0:
            raise TunnelSetupError(
                "Failed to set cloudflared service ImagePath for tunnel run mode. "
                f"stderr: {set_path.stderr.strip() or set_path.stdout.strip() or 'n/a'}"
            )
        changed = True

    if not _status_is_auto(status_before):
        set_auto = run_logged(
            ctx,
            ["sc.exe", "config", SERVICE_NAME, "start=", "auto"],
            timeout=60,
            action_name="service_set_auto",
        )
        if set_auto.returncode != 0:
            raise TunnelSetupError(
                f"Failed to set {SERVICE_NAME} startup type to Automatic. stderr: {set_auto.stderr.strip() or 'n/a'}"
            )
        changed = True

    if changed:
        start_cmd = f"Restart-Service -Name '{SERVICE_NAME}' -Force -ErrorAction Stop"
    elif not _status_is_running(status_before):
        start_cmd = f"Start-Service -Name '{SERVICE_NAME}' -ErrorAction Stop"
    else:
        start_cmd = ""

    if start_cmd:
        start = run_logged(
            ctx,
            ["powershell", "-NoProfile", "-Command", start_cmd],
            timeout=120,
            action_name="service_start",
        )
        if start.returncode != 0:
            raise TunnelSetupError(
                f"Failed to start {SERVICE_NAME}. stderr: {start.stderr.strip() or start.stdout.strip() or 'n/a'}"
            )
        changed = True
        time.sleep(1)

    status_after = get_service_status(ctx)
    if (
        not bool(status_after.get("installed", False))
        or not _status_is_auto(status_after)
        or not _status_is_running(status_after)
        or not _status_has_tunnel_command(status_after, tunnel_name, config_path)
    ):
        raise TunnelSetupError(
            f"{SERVICE_NAME} is not in desired state after apply. status={status_after}"
        )
    payload = {"changed": changed, **status_after, "tunnel_name": tunnel_name, "config_path": str(config_path)}
    ctx.action("ensure_service", "ok", payload)
    return payload


def ensure_cloudflared_service(
    ctx: RunContext,
    *,
    tunnel_name: str,
    config_path: Path,
    allow_elevation: bool = True,
) -> dict[str, Any]:
    status_before = get_service_status(ctx)
    needs_change = (
        not bool(status_before.get("installed", False))
        or not _status_is_auto(status_before)
        or not _status_is_running(status_before)
        or not _status_has_tunnel_command(status_before, tunnel_name, config_path)
    )
    if not needs_change:
        payload = {"changed": False, **status_before, "tunnel_name": tunnel_name, "config_path": str(config_path)}
        ctx.action("ensure_service", "ok", payload)
        return payload

    if not is_windows_admin():
        if not allow_elevation:
            raise TunnelSetupError(
                "Administrator rights are required to install or modify cloudflared service."
            )
        elevated = run_python_elevated(
            ctx,
            Path(__file__).resolve(),
            [
                "--apply",
                "--tunnel-name",
                tunnel_name,
                "--config-path",
                str(config_path),
                "--log-dir",
                str(ctx.log_dir),
                "--run-id",
                ctx.run_id,
                "--no-elevate",
            ],
            timeout=900,
        )
        if elevated.returncode != 0:
            raise TunnelSetupError(
                f"Elevated service apply failed with exit code {elevated.returncode}. "
                "Approve UAC prompt and re-run."
            )
        status_after = get_service_status(ctx)
        if (
            not bool(status_after.get("installed", False))
            or not _status_is_auto(status_after)
            or not _status_is_running(status_after)
            or not _status_has_tunnel_command(status_after, tunnel_name, config_path)
        ):
            raise TunnelSetupError(f"Service state invalid after elevated apply: {status_after}")
        payload = {"changed": True, **status_after, "tunnel_name": tunnel_name, "config_path": str(config_path)}
        ctx.action("ensure_service", "ok", payload)
        return payload

    return _apply_service_changes_local(
        ctx,
        tunnel_name=tunnel_name,
        config_path=config_path,
        status_before=status_before,
    )


def restart_cloudflared_service(
    ctx: RunContext,
    *,
    reason: str,
    cooldown_state_path: Path,
    cooldown_seconds: int = 120,
    allow_elevation: bool = True,
) -> dict[str, Any]:
    now = time.time()
    state = read_json(cooldown_state_path, default={})
    last_restart_epoch = float(state.get("last_restart_epoch", 0) or 0)
    seconds_since_last = now - last_restart_epoch
    if seconds_since_last < cooldown_seconds:
        payload = {
            "restarted": False,
            "cooldown_active": True,
            "cooldown_seconds": cooldown_seconds,
            "seconds_since_last": round(seconds_since_last, 2),
            "reason": reason,
        }
        ctx.action("service_restart", "skipped", payload)
        return payload

    if not is_windows_admin():
        if not allow_elevation:
            raise TunnelSetupError("Administrator rights are required to restart cloudflared service.")
        elevated = run_python_elevated(
            ctx,
            Path(__file__).resolve(),
            [
                "--restart",
                "--reason",
                reason,
                "--cooldown-state",
                str(cooldown_state_path),
                "--cooldown-seconds",
                str(cooldown_seconds),
                "--log-dir",
                str(ctx.log_dir),
                "--run-id",
                ctx.run_id,
                "--no-elevate",
            ],
            timeout=600,
        )
        if elevated.returncode != 0:
            raise TunnelSetupError(
                f"Elevated restart failed with exit code {elevated.returncode}. Approve UAC prompt and re-run."
            )
        status = get_service_status(ctx)
        payload = {"restarted": True, "cooldown_active": False, "reason": reason, **status}
        ctx.action("service_restart", "ok", payload)
        return payload

    restart = run_logged(
        ctx,
        ["powershell", "-NoProfile", "-Command", f"Restart-Service -Name '{SERVICE_NAME}' -Force -ErrorAction Stop"],
        timeout=180,
        action_name="service_restart",
    )
    if restart.returncode != 0:
        raise TunnelSetupError(
            f"Failed to restart {SERVICE_NAME}. stderr: {restart.stderr.strip() or restart.stdout.strip() or 'n/a'}"
        )
    write_json(
        cooldown_state_path,
        {
            "last_restart_epoch": now,
            "last_restart_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "reason": reason,
        },
    )
    time.sleep(1)
    status = get_service_status(ctx)
    if not _status_is_running(status):
        raise TunnelSetupError(f"{SERVICE_NAME} failed to return to running state after restart.")
    payload = {"restarted": True, "cooldown_active": False, "reason": reason, **status}
    ctx.action("service_restart", "ok", payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure cloudflared Windows service.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--reason", default="manual")
    parser.add_argument("--cooldown-state", default=str(Path(DEFAULT_LOG_DIR) / "guard_state.json"))
    parser.add_argument("--cooldown-seconds", type=int, default=120)
    parser.add_argument("--no-elevate", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    ctx = RunContext(log_dir=Path(args.log_dir), run_id=args.run_id, enable_console=True)
    try:
        if args.restart:
            payload = restart_cloudflared_service(
                ctx,
                reason=args.reason,
                cooldown_state_path=Path(args.cooldown_state),
                cooldown_seconds=args.cooldown_seconds,
                allow_elevation=not args.no_elevate,
            )
            payload["ok"] = True
        elif args.apply:
            payload = ensure_cloudflared_service(
                ctx,
                tunnel_name=args.tunnel_name,
                config_path=Path(args.config_path),
                allow_elevation=not args.no_elevate,
            )
            payload["ok"] = True
        else:
            payload = {"ok": True, **get_service_status(ctx)}
    except TunnelSetupError as err:
        ctx.action("ensure_service", "error", {"error": str(err)})
        payload = {"ok": False, "error": str(err)}
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"ERROR: {err}")
        return 2

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
