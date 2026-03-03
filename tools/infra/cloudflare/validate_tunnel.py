from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_CLOUDFLARED_DIR,
    DEFAULT_CONFIG_PATH,
    DEFAULT_HOSTNAME,
    DEFAULT_LOG_DIR,
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
)
from ensure_config import inspect_config_file
from ensure_service import get_service_status


def validate_tunnel_state(
    ctx: RunContext,
    *,
    tunnel_name: str,
    hostname: str,
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
    if connections_count <= 0:
        suggested_fixes.append("No active tunnel connections detected. Restart cloudflared service.")

    origin_ok, origin_status, origin_error = origin_reachable(origin_url)
    if not origin_ok:
        suggested_fixes.append(f"Origin {origin_url} is unreachable. Confirm local app on port 3000.")

    payload = {
        "tunnel_name": tunnel_name,
        "tunnel_uuid": tunnel_uuid,
        "hostname_bound": hostname_bound,
        "ingress_ok": ingress_ok,
        "service_installed": service_installed,
        "service_running": service_running,
        "connections_count": int(connections_count),
        "origin_reachable": origin_ok,
        "origin_status_code": origin_status,
        "origin_error": origin_error,
        "suggested_fixes": suggested_fixes,
        "config_path": str(config_path),
        "cloudflared_dir": str(cloudflared_dir),
        "log_paths": {
            "setup_log": str(ctx.setup_log_path),
            "actions_log": str(ctx.actions_log_path),
        },
    }
    ctx.action("validate_tunnel", "ok", payload)
    critical_ok = bool(hostname_bound and ingress_ok and service_installed and service_running and origin_ok)
    return payload, critical_ok


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Cloudflare tunnel setup health.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
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
        payload, critical_ok = validate_tunnel_state(
            ctx,
            tunnel_name=args.tunnel_name,
            hostname=args.hostname,
            origin_url=args.origin_url,
            config_path=Path(args.config_path),
            cloudflared_dir=Path(args.cloudflared_dir),
        )
    except TunnelSetupError as err:
        payload = {
            "tunnel_name": args.tunnel_name,
            "tunnel_uuid": "",
            "hostname_bound": False,
            "ingress_ok": False,
            "service_installed": False,
            "service_running": False,
            "connections_count": 0,
            "origin_reachable": False,
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
