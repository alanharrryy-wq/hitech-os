from __future__ import annotations

import argparse
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_CLOUDFLARED_DIR,
    DEFAULT_CONFIG_PATH,
    DEFAULT_FORMS_HOSTNAME,
    DEFAULT_FORMS_ORIGIN_URL,
    DEFAULT_HOSTNAME,
    DEFAULT_LOG_DIR,
    DEFAULT_ORIGIN_URL,
    DEFAULT_REPO_ROOT,
    DEFAULT_TEMPLATE_HOSTNAME,
    DEFAULT_TEMPLATE_ORIGIN_URL,
    DEFAULT_TUNNEL_NAME,
    RunContext,
    TunnelSetupError,
    cloudflared,
    ensure_cloudflared_available,
    get_tunnel_connections_count,
    get_tunnel_uuid,
    run_logged,
    write_json,
)
from ensure_config import compose_ingress_routes, ensure_tunnel_config
from ensure_origin import ensure_forms_origin, ensure_keystone_origin, ensure_template_origin
from ensure_service import ensure_cloudflared_service, get_service_status, restart_cloudflared_service
from ensure_watchdog import WATCHDOG_TASK_NAME, ensure_watchdog_task, inspect_watchdog_task
from ensure_public_watchdog import (
    PUBLIC_HEALTH_TASK_NAME,
    ensure_public_health_task,
    inspect_public_health_task,
)
from fix_dns import ensure_dns_binding
from validate_tunnel import validate_tunnel_state


def _default_report_path(repo_root: Path) -> Path:
    return repo_root / "tools" / "infra" / "cloudflare" / "FINAL_REPORT.txt"


def _public_url(hostname: str) -> str:
    return f"https://{hostname}"


def _build_report_text(
    *,
    run_id: str,
    generated_at: str,
    tunnel_name: str,
    tunnel_uuid: str,
    hostname: str,
    dns_status: bool,
    dns_status_by_hostname: dict[str, bool],
    ingress_ok: bool,
    service_status: dict[str, Any],
    watchdog_status: dict[str, Any],
    public_watchdog_status: dict[str, Any],
    forms_origin_result: dict[str, Any],
    template_origin_result: dict[str, Any],
    validation_payload: dict[str, Any],
    validation_path: Path,
    setup_log_path: Path,
    actions_log_path: Path,
    summary_status: str,
) -> str:
    hostname_lines = "\n".join(
        f"  - {route_hostname}: {'BOUND' if route_bound else 'MISSING'}"
        for route_hostname, route_bound in dns_status_by_hostname.items()
    )
    public_host_lines = "\n".join(
        (
            f"  - {route_hostname}: healthy={details.get('healthy', False)} "
            f"status={details.get('status_code')} url={details.get('public_url')}"
        )
        for route_hostname, details in (validation_payload.get("public_hosts", {}) or {}).items()
    )
    return (
        "HITECH Cloudflare Tunnel Forever Report\n"
        "======================================\n"
        f"Generated At: {generated_at}\n"
        f"Run ID: {run_id}\n"
        f"Summary Status: {summary_status}\n"
        "\n"
        f"Tunnel Name: {tunnel_name}\n"
        f"Tunnel UUID: {tunnel_uuid}\n"
        f"Primary Hostname: {hostname}\n"
        f"Public URL: {validation_payload.get('public_url', _public_url(hostname))}\n"
        f"Hostname Route Bound: {dns_status}\n"
        "Route Bindings:\n"
        f"{hostname_lines}\n"
        f"Ingress OK: {ingress_ok}\n"
        f"Tunnel Connected: {validation_payload.get('tunnel_connected', False)}\n"
        f"Origin Healthy: {validation_payload.get('local_origin_healthy', False)}\n"
        f"Forms Origin Healthy: {forms_origin_result.get('origin_reachable', False)}\n"
        f"Template Origin Healthy: {template_origin_result.get('origin_reachable', False)}\n"
        f"All Public Hostnames Healthy (2xx/3xx): {validation_payload.get('public_hostname_healthy', False)}\n"
        f"Public Status Code: {validation_payload.get('public_status_code', 'n/a')}\n"
        "Public Host Checks:\n"
        f"{public_host_lines}\n"
        "\n"
        f"Service Installed: {service_status.get('installed', False)}\n"
        f"Service Running: {str(service_status.get('status', '')).lower() == 'running' or str(service_status.get('state', '')).lower() == 'running'}\n"
        f"Service Start Mode: {service_status.get('start_mode', 'Unknown')}\n"
        f"Service Account: {service_status.get('start_name', 'Unknown')}\n"
        f"Service ImagePath: {service_status.get('path_name', '')}\n"
        "\n"
        f"Watchdog Task: {watchdog_status.get('task_name', WATCHDOG_TASK_NAME)}\n"
        f"Watchdog Installed: {watchdog_status.get('installed', False)}\n"
        f"Watchdog Command OK: {watchdog_status.get('command_ok', False)}\n"
        f"Watchdog Schedule OK (PT5M): {watchdog_status.get('schedule_ok', False)}\n"
        f"Watchdog Enabled: {watchdog_status.get('enabled', False)}\n"
        "\n"
        f"Public Health Task: {public_watchdog_status.get('task_name', PUBLIC_HEALTH_TASK_NAME)}\n"
        f"Public Health Task Installed: {public_watchdog_status.get('installed', False)}\n"
        f"Public Health Command OK: {public_watchdog_status.get('command_ok', False)}\n"
        f"Public Health Schedule OK (PT5M): {public_watchdog_status.get('schedule_ok', False)}\n"
        f"Public Health Enabled: {public_watchdog_status.get('enabled', False)}\n"
        "\n"
        "Log Paths\n"
        "---------\n"
        f"setup_log: {setup_log_path}\n"
        f"actions_log: {actions_log_path}\n"
        f"validate_json: {validation_path}\n"
        "\n"
        "Required checks have been executed by setup_tunnel_forever.ps1.\n"
    )


def run_guard_only(
    ctx: RunContext,
    *,
    repo_root: Path,
    tunnel_name: str,
    origin_url: str,
    forms_origin_url: str,
    template_origin_url: str,
    cooldown_state_path: Path,
    cooldown_seconds: int,
) -> dict[str, Any]:
    ensure_cloudflared_available(ctx)
    get_tunnel_uuid(ctx, tunnel_name)
    origin_status: dict[str, Any] = {}
    try:
        origin_status = ensure_keystone_origin(
            ctx,
            repo_root=repo_root,
            origin_url=origin_url,
            state_path=ctx.log_dir / "keystone_origin_state.json",
            runtime_log_path=ctx.log_dir / "keystone_origin_runtime.log",
            wait_seconds=45,
            launch_cooldown_seconds=120,
        )
    except TunnelSetupError as err:
        origin_status = {"origin_reachable": False, "error": str(err)}

    origin_healthy = bool(origin_status.get("origin_reachable", False))
    if not origin_healthy:
        try:
            origin_status = ensure_keystone_origin(
                ctx,
                repo_root=repo_root,
                origin_url=origin_url,
                state_path=ctx.log_dir / "keystone_origin_state.json",
                runtime_log_path=ctx.log_dir / "keystone_origin_runtime.log",
                wait_seconds=60,
                launch_cooldown_seconds=0,
            )
        except TunnelSetupError as err:
            origin_status = {
                "origin_reachable": False,
                "error": str(err),
                "forced_relaunch_attempted": True,
            }
    origin_healthy = bool(origin_status.get("origin_reachable", False))

    forms_origin_status: dict[str, Any] = {}
    try:
        forms_origin_status = ensure_forms_origin(
            ctx,
            repo_root=repo_root,
            origin_url=forms_origin_url,
            state_path=ctx.log_dir / "forms_origin_state.json",
            runtime_log_path=ctx.log_dir / "forms_origin_runtime.log",
            wait_seconds=45,
            launch_cooldown_seconds=120,
        )
    except TunnelSetupError as err:
        forms_origin_status = {"origin_reachable": False, "error": str(err)}
    forms_origin_healthy = bool(forms_origin_status.get("origin_reachable", False))
    if not forms_origin_healthy:
        try:
            forms_origin_status = ensure_forms_origin(
                ctx,
                repo_root=repo_root,
                origin_url=forms_origin_url,
                state_path=ctx.log_dir / "forms_origin_state.json",
                runtime_log_path=ctx.log_dir / "forms_origin_runtime.log",
                wait_seconds=60,
                launch_cooldown_seconds=0,
            )
        except TunnelSetupError as err:
            forms_origin_status = {
                "origin_reachable": False,
                "error": str(err),
                "forced_relaunch_attempted": True,
            }
    forms_origin_healthy = bool(forms_origin_status.get("origin_reachable", False))

    template_origin_status: dict[str, Any] = {}
    try:
        template_origin_status = ensure_template_origin(
            ctx,
            repo_root=repo_root,
            origin_url=template_origin_url,
            state_path=ctx.log_dir / "template_origin_state.json",
            runtime_log_path=ctx.log_dir / "template_origin_runtime.log",
            wait_seconds=45,
            launch_cooldown_seconds=120,
        )
    except TunnelSetupError as err:
        template_origin_status = {"origin_reachable": False, "error": str(err)}
    template_origin_healthy = bool(template_origin_status.get("origin_reachable", False))
    if not template_origin_healthy:
        try:
            template_origin_status = ensure_template_origin(
                ctx,
                repo_root=repo_root,
                origin_url=template_origin_url,
                state_path=ctx.log_dir / "template_origin_state.json",
                runtime_log_path=ctx.log_dir / "template_origin_runtime.log",
                wait_seconds=60,
                launch_cooldown_seconds=0,
            )
        except TunnelSetupError as err:
            template_origin_status = {
                "origin_reachable": False,
                "error": str(err),
                "forced_relaunch_attempted": True,
            }
    template_origin_healthy = bool(template_origin_status.get("origin_reachable", False))

    try:
        connections_count = get_tunnel_connections_count(ctx, tunnel_name)
        connection_error = ""
    except TunnelSetupError as err:
        connections_count = 0
        connection_error = str(err)

    healthy = connections_count > 0 and origin_healthy and forms_origin_healthy and template_origin_healthy
    if healthy:
        payload = {
            "guard_ok": True,
            "connections_count": connections_count,
            "origin_healthy": origin_healthy,
            "forms_origin_healthy": forms_origin_healthy,
            "template_origin_healthy": template_origin_healthy,
            "restarted": False,
            "reason": "",
            "origin": origin_status,
            "forms_origin": forms_origin_status,
            "template_origin": template_origin_status,
        }
        ctx.action("guard_check", "ok", payload)
        return payload

    if connections_count <= 0:
        reason = "guard: no active tunnel connections"
        if connection_error:
            reason = f"{reason}; info_error={connection_error}"
        restart_result = restart_cloudflared_service(
            ctx,
            reason=reason,
            cooldown_state_path=cooldown_state_path,
            cooldown_seconds=cooldown_seconds,
            allow_elevation=True,
        )
    else:
        restart_result = {
            "restarted": False,
            "cooldown_active": False,
            "reason": "guard: origin unreachable while tunnel connected",
        }
    try:
        after_count = get_tunnel_connections_count(ctx, tunnel_name)
    except TunnelSetupError:
        after_count = 0
    final_origin_healthy = bool(origin_status.get("origin_reachable", False))
    final_forms_origin_healthy = bool(forms_origin_status.get("origin_reachable", False))
    final_template_origin_healthy = bool(template_origin_status.get("origin_reachable", False))
    payload = {
        "guard_ok": after_count > 0 and final_origin_healthy and final_forms_origin_healthy and final_template_origin_healthy,
        "connections_count_before": connections_count,
        "connections_count_after": after_count,
        "origin_healthy": final_origin_healthy,
        "forms_origin_healthy": final_forms_origin_healthy,
        "template_origin_healthy": final_template_origin_healthy,
        "origin": origin_status,
        "forms_origin": forms_origin_status,
        "template_origin": template_origin_status,
        **restart_result,
    }
    status = "ok" if payload["guard_ok"] else "error"
    ctx.action("guard_check", status, payload)
    return payload


def run_full_setup(
    ctx: RunContext,
    *,
    repo_root: Path,
    tunnel_name: str,
    hostname: str,
    forms_hostname: str,
    template_hostname: str,
    origin_url: str,
    forms_origin_url: str,
    template_origin_url: str,
    config_path: Path,
    cloudflared_dir: Path,
    validate_json_out: Path,
    final_report_path: Path,
    cooldown_state_path: Path,
    cooldown_seconds: int,
) -> dict[str, Any]:
    ensure_cloudflared_available(ctx)
    tunnel_uuid = get_tunnel_uuid(ctx, tunnel_name)
    ingress_routes = compose_ingress_routes(
        hostname,
        origin_url,
        [
            (forms_hostname, forms_origin_url),
            (template_hostname, template_origin_url),
        ],
    )
    dns_results: dict[str, dict[str, Any]] = {}
    for route_hostname, _ in ingress_routes:
        dns_results[route_hostname] = ensure_dns_binding(ctx, tunnel_name, route_hostname)

    config_result = ensure_tunnel_config(
        ctx,
        tunnel_name=tunnel_name,
        hostname=hostname,
        origin_url=origin_url,
        config_path=config_path,
        cloudflared_dir=cloudflared_dir,
        ingress_routes=ingress_routes,
    )
    service_result = ensure_cloudflared_service(
        ctx,
        tunnel_name=tunnel_name,
        config_path=config_path,
        allow_elevation=True,
    )
    if config_result.get("changed", False):
        restart_result = restart_cloudflared_service(
            ctx,
            reason="config_changed_reload_cloudflared",
            cooldown_state_path=cooldown_state_path,
            cooldown_seconds=0,
            allow_elevation=True,
        )
        service_result["restarted_after_config_change"] = restart_result.get("restarted", False)
        service_result["restart_reason"] = "config_changed_reload_cloudflared"
        service_result["status"] = restart_result.get("status", service_result.get("status"))
        service_result["state"] = restart_result.get("state", service_result.get("state"))
    watchdog_result = ensure_watchdog_task(
        ctx,
        task_name=WATCHDOG_TASK_NAME,
        repo_root=repo_root,
        allow_elevation=True,
    )
    public_watchdog_result = ensure_public_health_task(
        ctx,
        task_name=PUBLIC_HEALTH_TASK_NAME,
        repo_root=repo_root,
        allow_elevation=True,
    )
    origin_result = ensure_keystone_origin(
        ctx,
        repo_root=repo_root,
        origin_url=origin_url,
        state_path=ctx.log_dir / "keystone_origin_state.json",
        runtime_log_path=ctx.log_dir / "keystone_origin_runtime.log",
        wait_seconds=120,
        launch_cooldown_seconds=120,
    )
    forms_origin_result = ensure_forms_origin(
        ctx,
        repo_root=repo_root,
        origin_url=forms_origin_url,
        state_path=ctx.log_dir / "forms_origin_state.json",
        runtime_log_path=ctx.log_dir / "forms_origin_runtime.log",
        wait_seconds=120,
        launch_cooldown_seconds=120,
    )
    template_origin_result = ensure_template_origin(
        ctx,
        repo_root=repo_root,
        origin_url=template_origin_url,
        state_path=ctx.log_dir / "template_origin_state.json",
        runtime_log_path=ctx.log_dir / "template_origin_runtime.log",
        wait_seconds=120,
        launch_cooldown_seconds=120,
    )

    public_url = _public_url(hostname)
    public_url_by_host = {
        hostname.lower(): _public_url(hostname),
        forms_hostname.lower(): _public_url(forms_hostname),
        template_hostname.lower(): _public_url(template_hostname),
    }
    validation_payload, critical_ok = validate_tunnel_state(
        ctx,
        tunnel_name=tunnel_name,
        hostname=hostname,
        public_url=public_url,
        origin_url=origin_url,
        config_path=config_path,
        cloudflared_dir=cloudflared_dir,
        ingress_routes=ingress_routes,
        public_url_by_host=public_url_by_host,
    )
    primary_public_host = (
        validation_payload.get("public_hosts", {}).get(hostname.lower(), {}) or {}
    )
    primary_public_healthy = bool(primary_public_host.get("healthy", False))
    force_reinstall_applied = False
    likely_service_mode_drift = bool(
        validation_payload.get("hostname_bound", False)
        and validation_payload.get("ingress_ok", False)
        and validation_payload.get("service_installed", False)
        and validation_payload.get("service_running", False)
        and validation_payload.get("tunnel_connected", False)
        and validation_payload.get("local_origin_healthy", False)
        and not primary_public_healthy
    )
    if not critical_ok and likely_service_mode_drift:
        ctx.action(
            "service_mode_drift_detected",
            "warning",
            {
                "public_status_code": validation_payload.get("public_status_code"),
                "service_path_name": validation_payload.get("service_path_name"),
            },
        )
        service_result = ensure_cloudflared_service(
            ctx,
            tunnel_name=tunnel_name,
            config_path=config_path,
            allow_elevation=True,
            force_reinstall=True,
        )
        force_reinstall_applied = True
        validation_payload, critical_ok = validate_tunnel_state(
            ctx,
            tunnel_name=tunnel_name,
            hostname=hostname,
            public_url=public_url,
            origin_url=origin_url,
            config_path=config_path,
            cloudflared_dir=cloudflared_dir,
            ingress_routes=ingress_routes,
            public_url_by_host=public_url_by_host,
        )
    validation_payload["service_force_reinstall_applied"] = force_reinstall_applied
    write_json(validate_json_out, validation_payload)

    dns_list_after = cloudflared(ctx, ["tunnel", "route", "dns", "list", "--tunnel", tunnel_name], timeout=180)
    if dns_list_after.returncode != 0:
        combined = f"{dns_list_after.stdout}\n{dns_list_after.stderr}".lower()
        if "expects the format" in combined or "unknown flag" in combined:
            dns_list_after = cloudflared(ctx, ["tunnel", "route", "dns", tunnel_name, hostname], timeout=180)
    service_snapshot = get_service_status(ctx)
    watchdog_snapshot = inspect_watchdog_task(ctx, WATCHDOG_TASK_NAME, repo_root)
    public_watchdog_snapshot = inspect_public_health_task(ctx, PUBLIC_HEALTH_TASK_NAME, repo_root)

    run_logged(
        ctx,
        ["powershell", "-NoProfile", "-Command", "Get-Service cloudflared | Format-List *"],
        timeout=60,
        action_name="service_get_service_cmd",
    )

    report_text = _build_report_text(
        run_id=ctx.run_id,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        tunnel_name=tunnel_name,
        tunnel_uuid=tunnel_uuid,
        hostname=hostname,
        dns_status=bool(dns_results.get(hostname, {}).get("hostname_bound", False)),
        dns_status_by_hostname={
            route_hostname: bool(route_payload.get("hostname_bound", False))
            for route_hostname, route_payload in dns_results.items()
        },
        ingress_ok=bool(validation_payload.get("ingress_ok", False)),
        service_status=service_snapshot,
        watchdog_status=watchdog_snapshot,
        public_watchdog_status=public_watchdog_snapshot,
        forms_origin_result=forms_origin_result,
        template_origin_result=template_origin_result,
        validation_payload=validation_payload,
        validation_path=validate_json_out,
        setup_log_path=ctx.setup_log_path,
        actions_log_path=ctx.actions_log_path,
        summary_status="PASS" if critical_ok else "FAIL",
    )
    final_report_path.write_text(report_text, encoding="utf-8")
    ctx.action(
        "final_report",
        "ok",
        {"path": str(final_report_path), "summary_status": "PASS" if critical_ok else "FAIL"},
    )

    # Keep guard state file deterministic and ready.
    if not cooldown_state_path.exists():
        write_json(cooldown_state_path, {"last_restart_epoch": 0, "reason": "init"})

    summary = {
        "critical_ok": critical_ok,
        "tunnel_uuid": tunnel_uuid,
        "dns_results": dns_results,
        "config_result": config_result,
        "service_result": service_result,
        "watchdog_result": watchdog_result,
        "public_watchdog_result": public_watchdog_result,
        "origin_result": origin_result,
        "forms_origin_result": forms_origin_result,
        "template_origin_result": template_origin_result,
        "validation": validation_payload,
        "service_force_reinstall_applied": force_reinstall_applied,
        "dns_list_stdout": dns_list_after.stdout,
        "service_snapshot": service_snapshot,
        "watchdog_snapshot": watchdog_snapshot,
        "public_watchdog_snapshot": public_watchdog_snapshot,
        "validate_json_out": str(validate_json_out),
        "final_report_path": str(final_report_path),
    }
    return summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Industrial Cloudflare tunnel forever setup and guard.")
    parser.add_argument("--repo-root", default=str(DEFAULT_REPO_ROOT))
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    parser.add_argument("--forms-hostname", default=DEFAULT_FORMS_HOSTNAME)
    parser.add_argument("--template-hostname", default=DEFAULT_TEMPLATE_HOSTNAME)
    parser.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
    parser.add_argument("--forms-origin-url", default=DEFAULT_FORMS_ORIGIN_URL)
    parser.add_argument("--template-origin-url", default=DEFAULT_TEMPLATE_ORIGIN_URL)
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--cloudflared-dir", default=str(DEFAULT_CLOUDFLARED_DIR))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--validate-json-out", default=None)
    parser.add_argument("--final-report", default=None)
    parser.add_argument("--guard-only", action="store_true")
    parser.add_argument("--cooldown-seconds", type=int, default=120)
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    repo_root = Path(args.repo_root)
    if not repo_root.exists():
        print(f"ERROR: repo root does not exist: {repo_root}")
        return 2

    ctx = RunContext(log_dir=Path(args.log_dir), run_id=args.run_id, enable_console=True)
    validate_json_out = Path(args.validate_json_out) if args.validate_json_out else Path(args.log_dir) / f"validate_{ctx.run_id}.json"
    final_report = Path(args.final_report) if args.final_report else _default_report_path(repo_root)
    cooldown_state = Path(args.log_dir) / "guard_state.json"

    try:
        if args.guard_only:
            payload = run_guard_only(
                ctx,
                repo_root=repo_root,
                tunnel_name=args.tunnel_name,
                origin_url=args.origin_url,
                forms_origin_url=args.forms_origin_url,
                template_origin_url=args.template_origin_url,
                cooldown_state_path=cooldown_state,
                cooldown_seconds=args.cooldown_seconds,
            )
            print(json.dumps(payload, indent=2))
            return 0 if payload.get("guard_ok", False) else 2

        summary = run_full_setup(
            ctx,
            repo_root=repo_root,
            tunnel_name=args.tunnel_name,
            hostname=args.hostname,
            forms_hostname=args.forms_hostname,
            template_hostname=args.template_hostname,
            origin_url=args.origin_url,
            forms_origin_url=args.forms_origin_url,
            template_origin_url=args.template_origin_url,
            config_path=Path(args.config_path),
            cloudflared_dir=Path(args.cloudflared_dir),
            validate_json_out=validate_json_out,
            final_report_path=final_report,
            cooldown_state_path=cooldown_state,
            cooldown_seconds=args.cooldown_seconds,
        )
        if not summary["critical_ok"]:
            print(json.dumps(summary, indent=2))
            return 2
        print(json.dumps(summary, indent=2))
        return 0
    except TunnelSetupError as err:
        ctx.action("tunnel_forever", "error", {"error": str(err)})
        error_payload = {"ok": False, "error": str(err)}
        print(json.dumps(error_payload, indent=2))
        return 2
    except Exception as err:  # noqa: BLE001
        ctx.action("tunnel_forever", "error", {"error": str(err), "traceback": traceback.format_exc()[-4000:]})
        error_payload = {"ok": False, "error": str(err)}
        print(json.dumps(error_payload, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
