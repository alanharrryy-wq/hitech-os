from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from cloudflared_helpers import (
    DEFAULT_CLOUDFLARED_DIR,
    DEFAULT_CONFIG_PATH,
    DEFAULT_HOSTNAME,
    DEFAULT_LOG_DIR,
    DEFAULT_ORIGIN_PORT,
    DEFAULT_ORIGIN_URL,
    DEFAULT_TUNNEL_NAME,
    RunContext,
    TunnelSetupError,
    cloudflared,
    ensure_cloudflared_available,
    get_tunnel_connections_count,
    get_tunnel_uuid,
    hostname_bound_in_dns_output,
    origin_reachable,
    public_endpoint_status,
)
from ensure_config import inspect_config_file
from ensure_service import get_service_status


def _origin_port(origin_url: str) -> int:
    parsed = urlparse(origin_url)
    if parsed.port is not None:
        return parsed.port
    return DEFAULT_ORIGIN_PORT


def _default_public_url(hostname: str) -> str:
    return f"https://{hostname}"


def _status_is_public_success(status_code: int | None) -> bool:
    return status_code is not None and 200 <= status_code < 400


def validate_tunnel_state(
    ctx: RunContext,
    *,
    tunnel_name: str,
    hostname: str,
    public_url: str,
    origin_url: str,
    config_path: Path,
    cloudflared_dir: Path,
) -> tuple[dict[str, Any], bool]:
    suggested_fixes: list[str] = []
    tunnel_uuid = ""
    hostname_bound = False
    ingress_ok = False
    service_installed = False
    service_running = False
    connections_count = 0
    origin_ok = False
    tunnel_connected = False
    edge_reachable = False
    public_ok = False
    public_status = None
    public_error = None

    ensure_cloudflared_available(ctx)
    tunnel_uuid = get_tunnel_uuid(ctx, tunnel_name)

    dns = cloudflared(ctx, ["tunnel", "route", "dns", "list", "--tunnel", tunnel_name], timeout=180)
    if dns.returncode == 0:
        hostname_bound = hostname_bound_in_dns_output(dns.stdout, hostname)
    else:
        combined = f"{dns.stdout}\n{dns.stderr}".lower()
        unsupported = "expects the format" in combined or "unknown flag" in combined
        if unsupported:
            dns_fallback = cloudflared(ctx, ["tunnel", "route", "dns", tunnel_name, hostname], timeout=180)
            fallback_text = f"{dns_fallback.stdout}\n{dns_fallback.stderr}".lower()
            hostname_bound = dns_fallback.returncode == 0 and (
                "already configured" in fallback_text
                or "created" in fallback_text
                or "added" in fallback_text
                or hostname in fallback_text
            )
    if not hostname_bound:
        suggested_fixes.append(
            f"Bind DNS route: cloudflared tunnel route dns list --tunnel {tunnel_name} "
            f"(or fallback: cloudflared tunnel route dns {tunnel_name} {hostname})"
        )

    credentials = cloudflared_dir / f"{tunnel_uuid}.json"
    config_check = inspect_config_file(
        config_path,
        tunnel_uuid=tunnel_uuid,
        credentials_file=credentials,
        hostname=hostname,
        origin_url=origin_url,
    )
    ingress_ok = bool(
        config_check["exists"]
        and config_check["tunnel_ok"]
        and config_check["credentials_ok"]
        and config_check["ingress_ok"]
    )
    if not ingress_ok:
        suggested_fixes.append("Rebuild config.yml with ensure_config.py (tunnel UUID, credentials-file, ingress).")

    service = get_service_status(ctx)
    service_installed = bool(service.get("installed", False))
    service_running = str(service.get("status", "")).lower() == "running" or str(service.get("state", "")).lower() == "running"
    if not service_installed:
        suggested_fixes.append("Install service: python ensure_service.py --apply")
    elif not service_running:
        suggested_fixes.append("Start service: powershell Start-Service cloudflared")

    try:
        connections_count = get_tunnel_connections_count(ctx, tunnel_name)
    except TunnelSetupError:
        connections_count = 0
    tunnel_connected = connections_count > 0
    if connections_count <= 0:
        suggested_fixes.append("No active tunnel connections detected. Restart cloudflared service.")

    origin_ok, origin_status, origin_error = origin_reachable(origin_url)
    if not origin_ok:
        suggested_fixes.append(
            f"Origin {origin_url} is unreachable. Confirm local app is running on port {_origin_port(origin_url)}."
        )

    edge_reachable, public_status, public_error = public_endpoint_status(public_url)
    public_ok = bool(edge_reachable and _status_is_public_success(public_status))
    if not public_ok:
        if edge_reachable and public_status is not None:
            suggested_fixes.append(
                f"Public endpoint returned HTTP {public_status}. "
                "If local origin and tunnel connection are healthy, force-reinstall service to remove runtime drift: "
                "python F:\\repos\\hitech-os\\tools\\infra\\cloudflare\\ensure_service.py --apply --force-reinstall"
            )
        else:
            suggested_fixes.append(
                f"Public endpoint {public_url} not reachable. Check DNS and Cloudflare edge reachability."
            )

    service_path_name = str(service.get("path_name", "") or "")
    service_start_name = str(service.get("start_name", "") or "")

    payload = {
        "tunnel_name": tunnel_name,
        "tunnel_uuid": tunnel_uuid,
        "public_url": public_url,
        "hostname_bound": hostname_bound,
        "ingress_ok": ingress_ok,
        "service_installed": service_installed,
        "service_running": service_running,
        "service_path_name": service_path_name,
        "service_start_name": service_start_name,
        "connections_count": int(connections_count),
        "tunnel_connected": tunnel_connected,
        "origin_reachable": origin_ok,
        "origin_status_code": origin_status,
        "origin_error": origin_error,
        "public_edge_reachable": edge_reachable,
        "public_status_code": public_status,
        "public_error": public_error,
        "public_ok": public_ok,
        "local_origin_healthy": origin_ok,
        "public_hostname_healthy": public_ok,
        "suggested_fixes": suggested_fixes,
        "config_path": str(config_path),
        "cloudflared_dir": str(cloudflared_dir),
        "log_paths": {
            "setup_log": str(ctx.setup_log_path),
            "actions_log": str(ctx.actions_log_path),
        },
    }
    ctx.action("validate_tunnel", "ok", payload)
    critical_ok = bool(
        hostname_bound
        and ingress_ok
        and service_installed
        and service_running
        and tunnel_connected
        and origin_ok
        and public_ok
    )
    return payload, critical_ok


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Cloudflare tunnel setup health.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    parser.add_argument("--public-url", default=None)
    parser.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--cloudflared-dir", default=str(DEFAULT_CLOUDFLARED_DIR))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json-out", default=None)
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    ctx = RunContext(log_dir=Path(args.log_dir), run_id=args.run_id, enable_console=True)
    try:
        public_url = args.public_url or _default_public_url(args.hostname)
        payload, critical_ok = validate_tunnel_state(
            ctx,
            tunnel_name=args.tunnel_name,
            hostname=args.hostname,
            public_url=public_url,
            origin_url=args.origin_url,
            config_path=Path(args.config_path),
            cloudflared_dir=Path(args.cloudflared_dir),
        )
    except TunnelSetupError as err:
        payload = {
            "tunnel_name": args.tunnel_name,
            "tunnel_uuid": "",
            "public_url": args.public_url or _default_public_url(args.hostname),
            "hostname_bound": False,
            "ingress_ok": False,
            "service_installed": False,
            "service_running": False,
            "connections_count": 0,
            "origin_reachable": False,
            "tunnel_connected": False,
            "public_edge_reachable": False,
            "public_status_code": None,
            "public_error": None,
            "public_ok": False,
            "local_origin_healthy": False,
            "public_hostname_healthy": False,
            "suggested_fixes": [str(err)],
            "error": str(err),
        }
        critical_ok = False
        ctx.action("validate_tunnel", "error", {"error": str(err)})

    output = json.dumps(payload, indent=2) + "\n"
    if args.json_out:
        Path(args.json_out).write_text(output, encoding="utf-8")
    print(output.strip())
    return 0 if critical_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
