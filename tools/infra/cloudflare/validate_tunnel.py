from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse

from cloudflared_helpers import (
    DEFAULT_CLOUDFLARED_DIR,
    DEFAULT_CONFIG_PATH,
    DEFAULT_FORMS_HOSTNAME,
    DEFAULT_FORMS_ORIGIN_URL,
    DEFAULT_HOSTNAME,
    DEFAULT_LOG_DIR,
    DEFAULT_ORIGIN_PORT,
    DEFAULT_ORIGIN_URL,
    DEFAULT_TEMPLATE_HOSTNAME,
    DEFAULT_TEMPLATE_ORIGIN_URL,
    DEFAULT_TUNNEL_NAME,
    RunContext,
    TunnelSetupError,
    cloudflared,
    ensure_cloudflared_available,
    get_tunnel_connections_count,
    get_tunnel_uuid,
    hostname_bound_in_dns_output,
    list_dns_hostnames,
    origin_reachable,
    public_endpoint_status,
)
from ensure_config import compose_ingress_routes, inspect_config_file


def _origin_port(origin_url: str) -> int:
    parsed = urlparse(origin_url)
    if parsed.port is not None:
        return parsed.port
    return DEFAULT_ORIGIN_PORT


def _default_public_url(hostname: str) -> str:
    return f"https://{hostname}"


def _status_is_public_success(status_code: int | None) -> bool:
    return status_code is not None and 200 <= status_code < 400


def _parse_public_url_specs(specs: Sequence[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for raw in specs:
        candidate = raw.strip()
        if not candidate:
            continue
        if "=" not in candidate:
            raise TunnelSetupError(
                f"Invalid --extra-public-url '{raw}'. Expected format '<hostname>=<public_url>'."
            )
        hostname, public_url = candidate.split("=", 1)
        host_normalized = hostname.strip().lower()
        public_normalized = public_url.strip().rstrip("/")
        parsed = urlparse(public_normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise TunnelSetupError(
                f"Invalid public URL '{public_url}' for hostname '{hostname}'."
            )
        output[host_normalized] = public_normalized
    return output


def _check_dns_bindings(
    ctx: RunContext, tunnel_name: str, hostnames: Sequence[str]
) -> tuple[dict[str, bool], bool, list[str], list[str]]:
    hostnames_bound: dict[str, bool] = {hostname: False for hostname in hostnames}
    hostnames_seen: list[str] = []
    warnings: list[str] = []

    dns = cloudflared(ctx, ["tunnel", "route", "dns", "list", "--tunnel", tunnel_name], timeout=180)
    if dns.returncode == 0:
        hostnames_seen = list_dns_hostnames(dns.stdout)
        for hostname in hostnames:
            hostnames_bound[hostname] = hostname_bound_in_dns_output(dns.stdout, hostname)
        return hostnames_bound, True, hostnames_seen, warnings

    combined = f"{dns.stdout}\n{dns.stderr}".lower()
    unsupported = "expects the format" in combined or "unknown flag" in combined
    if not unsupported:
        warnings.append(
            f"Unable to list DNS routes (stderr: {dns.stderr.strip() or dns.stdout.strip() or 'n/a'})."
        )
        return hostnames_bound, False, hostnames_seen, warnings

    for hostname in hostnames:
        fallback = cloudflared(ctx, ["tunnel", "route", "dns", tunnel_name, hostname], timeout=180)
        fallback_text = f"{fallback.stdout}\n{fallback.stderr}".lower()
        hostnames_bound[hostname] = fallback.returncode == 0 and (
            "already configured" in fallback_text
            or "already exists" in fallback_text
            or "created" in fallback_text
            or "added" in fallback_text
            or hostname in fallback_text
        )
        if hostnames_bound[hostname]:
            hostnames_seen.append(hostname)
        else:
            warnings.append(
                f"Fallback DNS check failed for '{hostname}' (stderr: {fallback.stderr.strip() or fallback.stdout.strip() or 'n/a'})."
            )

    return hostnames_bound, False, hostnames_seen, warnings


def validate_tunnel_state(
    ctx: RunContext,
    *,
    tunnel_name: str,
    hostname: str,
    public_url: str,
    origin_url: str,
    config_path: Path,
    cloudflared_dir: Path,
    ingress_routes: Sequence[tuple[str, str]],
    public_url_by_host: dict[str, str],
) -> tuple[dict[str, Any], bool]:
    suggested_fixes: list[str] = []
    tunnel_uuid = ""
    ingress_ok = False
    service_installed = False
    service_running = False
    connections_count = 0
    origin_ok = False
    tunnel_connected = False
    public_ok = False

    ensure_cloudflared_available(ctx)
    tunnel_uuid = get_tunnel_uuid(ctx, tunnel_name)

    all_hostnames = [route_hostname for route_hostname, _ in ingress_routes]
    hostnames_bound, list_supported, hostnames_seen, dns_warnings = _check_dns_bindings(
        ctx, tunnel_name, all_hostnames
    )
    if dns_warnings:
        suggested_fixes.extend(dns_warnings)

    for route_hostname, is_bound in hostnames_bound.items():
        if not is_bound:
            suggested_fixes.append(
                f"Bind DNS route for '{route_hostname}': cloudflared tunnel route dns {tunnel_name} {route_hostname}"
            )

    credentials = cloudflared_dir / f"{tunnel_uuid}.json"
    config_check = inspect_config_file(
        config_path,
        tunnel_uuid=tunnel_uuid,
        credentials_file=credentials,
        ingress_routes=ingress_routes,
    )
    ingress_ok = bool(
        config_check["exists"]
        and config_check["tunnel_ok"]
        and config_check["credentials_ok"]
        and config_check["ingress_ok"]
        and config_check["all_routes_ok"]
    )
    if not ingress_ok:
        suggested_fixes.append(
            "Rebuild config.yml with ensure_config.py (tunnel UUID, credentials-file, ingress routes, fallback)."
        )

    from ensure_service import get_service_status

    service = get_service_status(ctx)
    service_installed = bool(service.get("installed", False))
    service_running = (
        str(service.get("status", "")).lower() == "running"
        or str(service.get("state", "")).lower() == "running"
    )
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

    public_hosts: dict[str, dict[str, Any]] = {}
    all_public_hosts_healthy = True
    for route_hostname in all_hostnames:
        route_public_url = public_url_by_host.get(route_hostname, _default_public_url(route_hostname))
        edge_reachable, route_public_status, route_public_error = public_endpoint_status(route_public_url)
        route_public_ok = bool(edge_reachable and _status_is_public_success(route_public_status))
        public_hosts[route_hostname] = {
            "public_url": route_public_url,
            "edge_reachable": edge_reachable,
            "status_code": route_public_status,
            "error": route_public_error,
            "healthy": route_public_ok,
        }
        if not route_public_ok:
            all_public_hosts_healthy = False
            if edge_reachable and route_public_status is not None:
                suggested_fixes.append(
                    f"Public endpoint '{route_hostname}' returned HTTP {route_public_status}. "
                    "If local origin and tunnel connection are healthy, consider service force-reinstall."
                )
            else:
                suggested_fixes.append(
                    f"Public endpoint '{route_public_url}' is not reachable. Check DNS and Cloudflare edge status."
                )

    public_ok = all_public_hosts_healthy

    primary_hostname_bound = bool(hostnames_bound.get(hostname.lower(), False))
    primary_public = public_hosts.get(hostname.lower(), {})
    primary_public_status = primary_public.get("status_code")
    primary_public_error = primary_public.get("error")
    primary_edge_reachable = bool(primary_public.get("edge_reachable", False))

    service_path_name = str(service.get("path_name", "") or "")
    service_start_name = str(service.get("start_name", "") or "")

    payload = {
        "tunnel_name": tunnel_name,
        "tunnel_uuid": tunnel_uuid,
        "public_url": public_url,
        "ingress_routes": [
            {"hostname": route_hostname, "origin_url": route_origin}
            for route_hostname, route_origin in ingress_routes
        ],
        "hostname_bound": primary_hostname_bound,
        "hostnames_bound": hostnames_bound,
        "all_hostnames_bound": all(hostnames_bound.values()),
        "dns_list_supported": list_supported,
        "hostnames_seen": hostnames_seen,
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
        "public_hosts": public_hosts,
        "public_edge_reachable": primary_edge_reachable,
        "public_status_code": primary_public_status,
        "public_error": primary_public_error,
        "public_ok": public_ok,
        "all_public_hosts_healthy": all_public_hosts_healthy,
        "local_origin_healthy": origin_ok,
        "public_hostname_healthy": all_public_hosts_healthy,
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
        payload["all_hostnames_bound"]
        and ingress_ok
        and service_installed
        and service_running
        and tunnel_connected
        and origin_ok
        and all_public_hosts_healthy
    )
    return payload, critical_ok


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Cloudflare tunnel setup health.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    parser.add_argument("--public-url", default=None)
    parser.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
    parser.add_argument(
        "--extra-route",
        action="append",
        default=[
            f"{DEFAULT_FORMS_HOSTNAME}={DEFAULT_FORMS_ORIGIN_URL}",
            f"{DEFAULT_TEMPLATE_HOSTNAME}={DEFAULT_TEMPLATE_ORIGIN_URL}",
        ],
        help="Additional route format: <hostname>=<origin_url>. Can be repeated.",
    )
    parser.add_argument(
        "--extra-public-url",
        action="append",
        default=[
            f"{DEFAULT_FORMS_HOSTNAME}=https://{DEFAULT_FORMS_HOSTNAME}",
            f"{DEFAULT_TEMPLATE_HOSTNAME}=https://{DEFAULT_TEMPLATE_HOSTNAME}",
        ],
        help="Additional public URL format: <hostname>=<public_url>. Can be repeated.",
    )
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
        ingress_routes = compose_ingress_routes(args.hostname, args.origin_url, args.extra_route)
        primary_public_url = args.public_url or _default_public_url(args.hostname)
        extra_public_urls = _parse_public_url_specs(args.extra_public_url)
        public_url_by_host = {args.hostname.lower(): primary_public_url}
        for route_hostname, _ in ingress_routes[1:]:
            public_url_by_host[route_hostname] = extra_public_urls.get(
                route_hostname, _default_public_url(route_hostname)
            )

        payload, critical_ok = validate_tunnel_state(
            ctx,
            tunnel_name=args.tunnel_name,
            hostname=args.hostname,
            public_url=primary_public_url,
            origin_url=args.origin_url,
            config_path=Path(args.config_path),
            cloudflared_dir=Path(args.cloudflared_dir),
            ingress_routes=ingress_routes,
            public_url_by_host=public_url_by_host,
        )
    except TunnelSetupError as err:
        payload = {
            "tunnel_name": args.tunnel_name,
            "tunnel_uuid": "",
            "public_url": args.public_url or _default_public_url(args.hostname),
            "hostname_bound": False,
            "hostnames_bound": {},
            "all_hostnames_bound": False,
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
            "all_public_hosts_healthy": False,
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
