from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_LOG_DIR,
    DEFAULT_REPO_ROOT,
    RunContext,
    TunnelSetupError,
    is_windows_admin,
    run_logged,
    run_python_elevated,
)


WATCHDOG_TASK_NAME = "HITECH-Cloudflared-TunnelGuard"


def _desired_exec(repo_root: Path) -> tuple[str, str, str]:
    script = repo_root / "tools" / "infra" / "cloudflare" / "setup_tunnel_forever.ps1"
    command = "pwsh"
    args = f'-NoProfile -ExecutionPolicy Bypass -File "{script}" -GuardOnly'
    task_run = f"{command} {args}"
    return command, args, task_run


def _xml_text(node: ET.Element | None) -> str:
    return (node.text or "").strip() if node is not None else ""


def inspect_watchdog_task(ctx: RunContext, task_name: str, repo_root: Path) -> dict[str, Any]:
    command_expected, args_expected, task_run_expected = _desired_exec(repo_root)
    query_xml = run_logged(
        ctx,
        ["schtasks", "/Query", "/TN", task_name, "/XML"],
        timeout=60,
        action_name="watchdog_query_xml",
    )
    if query_xml.returncode != 0:
        combined = f"{query_xml.stdout}\n{query_xml.stderr}".lower()
        access_denied = "access denied" in combined or "acceso denegado" in combined
        if access_denied:
            payload = {
                "installed": True,
                "task_name": task_name,
                "command_ok": True,
                "schedule_ok": True,
                "enabled": True,
                "next_run_time": "",
                "status_text": "AccessDenied",
                "task_run_expected": task_run_expected,
                "inspection_limited": True,
            }
            ctx.action("watchdog_status", "ok", payload)
            return payload
        payload = {
            "installed": False,
            "task_name": task_name,
            "command_ok": False,
            "schedule_ok": False,
            "enabled": False,
            "next_run_time": "",
            "status_text": "NotInstalled",
            "task_run_expected": task_run_expected,
        }
        ctx.action("watchdog_status", "ok", payload)
        return payload

    try:
        root = ET.fromstring(query_xml.stdout)
    except ET.ParseError as err:
        raise TunnelSetupError(f"Unable to parse scheduled task XML for '{task_name}': {err}") from err

    command = _xml_text(root.find(".//{*}Exec/{*}Command"))
    arguments = _xml_text(root.find(".//{*}Exec/{*}Arguments"))
    # Repetition interval can hang under TimeTrigger/CalendarTrigger, so resolve from
    # any Repetition node instead of only ".//Trigger/...".
    interval = _xml_text(root.find(".//{*}Repetition/{*}Interval"))
    enabled_text = _xml_text(root.find(".//{*}Settings/{*}Enabled"))
    # If Settings/Enabled is omitted, Windows treats task as enabled by default.
    enabled = True if not enabled_text else enabled_text.lower() in {"true", "1"}
    command_ok = command.lower() == command_expected.lower() and args_expected.lower() in arguments.lower()
    schedule_ok = interval.upper() == "PT5M"

    query_verbose = run_logged(
        ctx,
        ["schtasks", "/Query", "/TN", task_name, "/V", "/FO", "LIST"],
        timeout=60,
        action_name="watchdog_query_verbose",
    )
    next_run_time = ""
    status_text = ""
    task_to_run = f"{command} {arguments}".strip()
    if query_verbose.returncode == 0:
        for line in query_verbose.stdout.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key_clean = key.strip().lower()
            value_clean = value.strip()
            if "next run" in key_clean:
                next_run_time = value_clean
            if key_clean == "status":
                status_text = value_clean
            if "task to run" in key_clean:
                task_to_run = value_clean

    payload = {
        "installed": True,
        "task_name": task_name,
        "command": command,
        "arguments": arguments,
        "task_to_run": task_to_run,
        "task_run_expected": task_run_expected,
        "command_ok": command_ok,
        "schedule_ok": schedule_ok,
        "enabled": enabled,
        "interval": interval,
        "next_run_time": next_run_time,
        "status_text": status_text,
    }
    ctx.action("watchdog_status", "ok", payload)
    return payload


def _apply_watchdog_local(ctx: RunContext, task_name: str, repo_root: Path) -> dict[str, Any]:
    _, _, task_run = _desired_exec(repo_root)
    create = run_logged(
        ctx,
        [
            "schtasks",
            "/Create",
            "/TN",
            task_name,
            "/SC",
            "MINUTE",
            "/MO",
            "5",
            "/TR",
            task_run,
            "/RU",
            "SYSTEM",
            "/RL",
            "HIGHEST",
            "/F",
        ],
        timeout=120,
        action_name="watchdog_create_or_update",
    )
    if create.returncode != 0:
        raise TunnelSetupError(
            f"Failed to create/update scheduled task '{task_name}'. stderr: {create.stderr.strip() or 'n/a'}"
        )

    enable = run_logged(
        ctx,
        ["schtasks", "/Change", "/TN", task_name, "/ENABLE"],
        timeout=60,
        action_name="watchdog_enable",
    )
    if enable.returncode != 0:
        raise TunnelSetupError(
            f"Failed to enable task '{task_name}'. stderr: {enable.stderr.strip() or 'n/a'}"
        )

    inspected = inspect_watchdog_task(ctx, task_name, repo_root)
    if not inspected["installed"] or not inspected["command_ok"] or not inspected["schedule_ok"] or not inspected["enabled"]:
        raise TunnelSetupError(f"Task '{task_name}' failed validation after update: {inspected}")
    inspected["changed"] = True
    ctx.action("ensure_watchdog", "ok", inspected)
    return inspected


def ensure_watchdog_task(
    ctx: RunContext,
    *,
    task_name: str,
    repo_root: Path,
    allow_elevation: bool = True,
) -> dict[str, Any]:
    current = inspect_watchdog_task(ctx, task_name, repo_root)
    needs_change = (
        not current["installed"]
        or not current["command_ok"]
        or not current["schedule_ok"]
        or not current["enabled"]
    )
    if not needs_change:
        payload = {"changed": False, **current}
        ctx.action("ensure_watchdog", "ok", payload)
        return payload

    if not is_windows_admin():
        if not allow_elevation:
            raise TunnelSetupError("Administrator rights are required to create/update SYSTEM scheduled task.")
        elevated = run_python_elevated(
            ctx,
            Path(__file__).resolve(),
            [
                "--apply",
                "--task-name",
                task_name,
                "--repo-root",
                str(repo_root),
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
                f"Elevated watchdog apply failed with exit code {elevated.returncode}. "
                "Approve UAC prompt and re-run."
            )
        refreshed = inspect_watchdog_task(ctx, task_name, repo_root)
        if not refreshed["installed"] or not refreshed["command_ok"] or not refreshed["schedule_ok"] or not refreshed["enabled"]:
            raise TunnelSetupError(f"Watchdog invalid after elevated apply: {refreshed}")
        payload = {"changed": True, **refreshed}
        ctx.action("ensure_watchdog", "ok", payload)
        return payload

    return _apply_watchdog_local(ctx, task_name, repo_root)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure watchdog scheduled task for tunnel self-heal.")
    parser.add_argument("--task-name", default=WATCHDOG_TASK_NAME)
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--no-elevate", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    ctx = RunContext(log_dir=Path(args.log_dir), run_id=args.run_id, enable_console=True)
    repo_root = Path(args.repo_root)
    try:
        if args.apply:
            payload = ensure_watchdog_task(
                ctx,
                task_name=args.task_name,
                repo_root=repo_root,
                allow_elevation=not args.no_elevate,
            )
            payload["ok"] = True
        else:
            payload = {"ok": True, **inspect_watchdog_task(ctx, args.task_name, repo_root)}
    except TunnelSetupError as err:
        ctx.action("ensure_watchdog", "error", {"error": str(err)})
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
