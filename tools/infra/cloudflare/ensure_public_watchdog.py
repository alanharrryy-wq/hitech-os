from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_FORMS_HOSTNAME,
    DEFAULT_FORMS_ORIGIN_URL,
    DEFAULT_HOSTNAME,
    DEFAULT_ORIGIN_URL,
    DEFAULT_LOG_DIR,
    DEFAULT_REPO_ROOT,
    DEFAULT_TEMPLATE_HOSTNAME,
    DEFAULT_TEMPLATE_ORIGIN_URL,
    RunContext,
    TunnelSetupError,
    atomic_write_text,
    is_windows_admin,
    run_logged,
    run_python_elevated,
    write_json,
)


PUBLIC_HEALTH_TASK_NAME = "HITECH-Cloudflared-PublicHealth"
PUBLIC_HEALTH_RUNNER_REL = Path("tools") / "_local" / "cloudflare" / "public_health_probe_runner.ps1"
PUBLIC_HEALTH_CONFIG_REL = Path("tools") / "_local" / "cloudflare" / "public_health_probe_runner.config.json"


def _public_health_probe_script(repo_root: Path) -> Path:
    return repo_root / "tools" / "infra" / "cloudflare" / "public_health_probe.ps1"


def _public_health_runner_paths(repo_root: Path) -> tuple[Path, Path]:
    return repo_root / PUBLIC_HEALTH_RUNNER_REL, repo_root / PUBLIC_HEALTH_CONFIG_REL


def _expected_runner_config(repo_root: Path) -> dict[str, Any]:
    return {
        "repo_root": str(repo_root),
        "tunnel_name": "engine",
        "hostname": DEFAULT_HOSTNAME,
        "origin_url": DEFAULT_ORIGIN_URL,
        "forms_hostname": DEFAULT_FORMS_HOSTNAME,
        "forms_origin_url": DEFAULT_FORMS_ORIGIN_URL,
        "template_hostname": DEFAULT_TEMPLATE_HOSTNAME,
        "template_origin_url": DEFAULT_TEMPLATE_ORIGIN_URL,
        "log_dir": str(repo_root / "logs" / "cloudflare"),
        "failure_threshold": 2,
        "probe_script": str(_public_health_probe_script(repo_root)),
    }


def _render_runner_script(config_path: Path) -> str:
    return (
        "[CmdletBinding()]\n"
        "param()\n\n"
        "Set-StrictMode -Version Latest\n"
        '$ErrorActionPreference = "Stop"\n\n'
        f'$configPath = "{config_path}"\n'
        "if (-not (Test-Path -LiteralPath $configPath)) {\n"
        '  throw "Missing public health runner config at $configPath"\n'
        "}\n\n"
        "$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json -ErrorAction Stop\n"
        "$probeScript = [string]$config.probe_script\n"
        "if ([string]::IsNullOrWhiteSpace($probeScript)) {\n"
        '  throw "probe_script is missing in public health runner config."\n'
        "}\n"
        "if (-not (Test-Path -LiteralPath $probeScript)) {\n"
        '  throw "Probe script not found: $probeScript"\n'
        "}\n\n"
        "& $probeScript `\n"
        "  -RepoRoot ([string]$config.repo_root) `\n"
        "  -TunnelName ([string]$config.tunnel_name) `\n"
        "  -Hostname ([string]$config.hostname) `\n"
        "  -OriginUrl ([string]$config.origin_url) `\n"
        "  -FormsHostname ([string]$config.forms_hostname) `\n"
        "  -FormsOriginUrl ([string]$config.forms_origin_url) `\n"
        "  -TemplateHostname ([string]$config.template_hostname) `\n"
        "  -TemplateOriginUrl ([string]$config.template_origin_url) `\n"
        "  -LogDir ([string]$config.log_dir) `\n"
        "  -FailureThreshold ([int]$config.failure_threshold)\n"
        "exit $LASTEXITCODE\n"
    )


def _ensure_runner_assets(ctx: RunContext, repo_root: Path) -> dict[str, Any]:
    runner_path, config_path = _public_health_runner_paths(repo_root)
    expected_config = _expected_runner_config(repo_root)

    existing_config: dict[str, Any] = {}
    if config_path.exists():
        try:
            existing_config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing_config = {}
    config_changed = existing_config != expected_config
    if config_changed:
        write_json(config_path, expected_config)

    expected_runner = _render_runner_script(config_path)
    existing_runner = ""
    if runner_path.exists():
        existing_runner = runner_path.read_text(encoding="utf-8")
    runner_changed = existing_runner != expected_runner
    if runner_changed:
        atomic_write_text(runner_path, expected_runner)

    payload = {
        "changed": config_changed or runner_changed,
        "config_changed": config_changed,
        "runner_changed": runner_changed,
        "runner_path": str(runner_path),
        "config_path": str(config_path),
    }
    ctx.action("public_watchdog_runner_assets", "ok", payload)
    return payload


def _inspect_runner_assets(repo_root: Path) -> dict[str, Any]:
    runner_path, config_path = _public_health_runner_paths(repo_root)
    expected_config = _expected_runner_config(repo_root)
    expected_runner = _render_runner_script(config_path)

    config_exists = config_path.exists()
    runner_exists = runner_path.exists()
    config_parse_error = ""
    config_data: dict[str, Any] = {}
    if config_exists:
        try:
            config_data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            config_parse_error = str(err)
    config_mismatch_keys = sorted(
        key for key, expected_value in expected_config.items() if config_data.get(key) != expected_value
    )
    config_ok = config_exists and not config_parse_error and not config_mismatch_keys

    runner_content = ""
    if runner_exists:
        runner_content = runner_path.read_text(encoding="utf-8")
    runner_ok = runner_exists and runner_content == expected_runner

    return {
        "runner_path": str(runner_path),
        "config_path": str(config_path),
        "runner_exists": runner_exists,
        "config_exists": config_exists,
        "runner_ok": runner_ok,
        "config_ok": config_ok,
        "config_parse_error": config_parse_error,
        "config_mismatch_keys": config_mismatch_keys,
    }


def _desired_exec(repo_root: Path) -> tuple[str, str, str]:
    script, _ = _public_health_runner_paths(repo_root)
    command = "pwsh"
    args = f'-NoProfile -ExecutionPolicy Bypass -File "{script}"'
    task_run = f"{command} {args}"
    return command, args, task_run


def _xml_text(node: ET.Element | None) -> str:
    return (node.text or "").strip() if node is not None else ""


def inspect_public_health_task(ctx: RunContext, task_name: str, repo_root: Path) -> dict[str, Any]:
    command_expected, args_expected, task_run_expected = _desired_exec(repo_root)
    runner_assets = _inspect_runner_assets(repo_root)
    runner_and_config_ok = bool(runner_assets["runner_ok"] and runner_assets["config_ok"])
    query_xml = run_logged(
        ctx,
        ["schtasks", "/Query", "/TN", task_name, "/XML"],
        timeout=60,
        action_name="public_watchdog_query_xml",
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
                "runner_ok": runner_assets["runner_ok"],
                "config_ok": runner_assets["config_ok"],
                "next_run_time": "",
                "status_text": "AccessDenied",
                "task_run_expected": task_run_expected,
                "inspection_limited": True,
                **runner_assets,
            }
            ctx.action("public_watchdog_status", "ok", payload)
            return payload
        payload = {
            "installed": False,
            "task_name": task_name,
            "command_ok": False,
            "schedule_ok": False,
            "enabled": False,
            "runner_ok": runner_assets["runner_ok"],
            "config_ok": runner_assets["config_ok"],
            "next_run_time": "",
            "status_text": "NotInstalled",
            "task_run_expected": task_run_expected,
            **runner_assets,
        }
        ctx.action("public_watchdog_status", "ok", payload)
        return payload

    try:
        root = ET.fromstring(query_xml.stdout)
    except ET.ParseError as err:
        raise TunnelSetupError(f"Unable to parse scheduled task XML for '{task_name}': {err}") from err

    command = _xml_text(root.find(".//{*}Exec/{*}Command"))
    arguments = _xml_text(root.find(".//{*}Exec/{*}Arguments"))
    interval = _xml_text(root.find(".//{*}Repetition/{*}Interval"))
    enabled_text = _xml_text(root.find(".//{*}Settings/{*}Enabled"))
    enabled = True if not enabled_text else enabled_text.lower() in {"true", "1"}
    command_ok = (
        command.lower() == command_expected.lower()
        and " ".join(arguments.split()).lower() == " ".join(args_expected.split()).lower()
    )
    schedule_ok = interval.upper() == "PT5M"

    query_verbose = run_logged(
        ctx,
        ["schtasks", "/Query", "/TN", task_name, "/V", "/FO", "LIST"],
        timeout=60,
        action_name="public_watchdog_query_verbose",
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
        "command_ok": command_ok and runner_and_config_ok,
        "schedule_ok": schedule_ok,
        "enabled": enabled,
        "interval": interval,
        "next_run_time": next_run_time,
        "status_text": status_text,
        "runner_ok": runner_assets["runner_ok"],
        "config_ok": runner_assets["config_ok"],
        **runner_assets,
    }
    ctx.action("public_watchdog_status", "ok", payload)
    return payload


def _apply_public_health_task_local(ctx: RunContext, task_name: str, repo_root: Path) -> dict[str, Any]:
    runner_assets = _ensure_runner_assets(ctx, repo_root)
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
        action_name="public_watchdog_create_or_update",
    )
    if create.returncode != 0:
        raise TunnelSetupError(
            f"Failed to create/update scheduled task '{task_name}'. stderr: {create.stderr.strip() or 'n/a'}"
        )

    enable = run_logged(
        ctx,
        ["schtasks", "/Change", "/TN", task_name, "/ENABLE"],
        timeout=60,
        action_name="public_watchdog_enable",
    )
    if enable.returncode != 0:
        raise TunnelSetupError(
            f"Failed to enable task '{task_name}'. stderr: {enable.stderr.strip() or 'n/a'}"
        )

    inspected = inspect_public_health_task(ctx, task_name, repo_root)
    if (
        not inspected["installed"]
        or not inspected["command_ok"]
        or not inspected["schedule_ok"]
        or not inspected["enabled"]
        or not inspected["config_ok"]
        or not inspected["runner_ok"]
    ):
        raise TunnelSetupError(f"Task '{task_name}' failed validation after update: {inspected}")
    inspected["changed"] = True
    inspected["runner_assets_changed"] = runner_assets["changed"]
    ctx.action("ensure_public_watchdog", "ok", inspected)
    return inspected


def ensure_public_health_task(
    ctx: RunContext,
    *,
    task_name: str,
    repo_root: Path,
    allow_elevation: bool = True,
) -> dict[str, Any]:
    runner_assets = _ensure_runner_assets(ctx, repo_root)
    current = inspect_public_health_task(ctx, task_name, repo_root)
    needs_change = (
        not current["installed"]
        or not current["command_ok"]
        or not current["schedule_ok"]
        or not current["enabled"]
        or not current["config_ok"]
        or not current["runner_ok"]
    )
    if not needs_change:
        payload = {"changed": runner_assets["changed"], "runner_assets_changed": runner_assets["changed"], **current}
        ctx.action("ensure_public_watchdog", "ok", payload)
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
                f"Elevated public-health watchdog apply failed with exit code {elevated.returncode}. "
                "Approve UAC prompt and re-run."
            )
        refreshed = inspect_public_health_task(ctx, task_name, repo_root)
        if (
            not refreshed["installed"]
            or not refreshed["command_ok"]
            or not refreshed["schedule_ok"]
            or not refreshed["enabled"]
            or not refreshed["config_ok"]
            or not refreshed["runner_ok"]
        ):
            raise TunnelSetupError(f"Public-health watchdog invalid after elevated apply: {refreshed}")
        payload = {"changed": True, "runner_assets_changed": runner_assets["changed"], **refreshed}
        ctx.action("ensure_public_watchdog", "ok", payload)
        return payload

    return _apply_public_health_task_local(ctx, task_name, repo_root)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure scheduled task for public endpoint health alerts.")
    parser.add_argument("--task-name", default=PUBLIC_HEALTH_TASK_NAME)
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
            payload = ensure_public_health_task(
                ctx,
                task_name=args.task_name,
                repo_root=repo_root,
                allow_elevation=not args.no_elevate,
            )
            payload["ok"] = True
        else:
            payload = {"ok": True, **inspect_public_health_task(ctx, args.task_name, repo_root)}
    except TunnelSetupError as err:
        ctx.action("ensure_public_watchdog", "error", {"error": str(err)})
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
