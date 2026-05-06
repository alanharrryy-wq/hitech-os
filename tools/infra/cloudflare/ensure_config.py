from __future__ import annotations

import argparse
import json
import re
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
    DEFAULT_ORIGIN_URL,
    DEFAULT_TEMPLATE_HOSTNAME,
    DEFAULT_TEMPLATE_ORIGIN_URL,
    DEFAULT_TUNNEL_NAME,
    RunContext,
    TunnelSetupError,
    atomic_write_text,
    ensure_directory,
    get_tunnel_uuid,
)

IngressRoute = tuple[str, str]


def _normalize_hostname(hostname: str) -> str:
    normalized = hostname.strip().lower()
    if not normalized:
        raise TunnelSetupError("Ingress route hostname cannot be empty.")
    return normalized


def _normalize_origin_url(origin_url: str) -> str:
    normalized = origin_url.strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise TunnelSetupError(
            f"Invalid origin URL '{origin_url}'. Expected full URL, e.g. http://127.0.0.1:3100"
        )
    return normalized


def parse_extra_routes(extra_routes: Sequence[str]) -> list[IngressRoute]:
    parsed_routes: list[IngressRoute] = []
    for raw in extra_routes:
        candidate = raw.strip()
        if not candidate:
            continue
        if "=" not in candidate:
            raise TunnelSetupError(
                f"Invalid --extra-route '{raw}'. Expected format '<hostname>=<origin_url>'."
            )
        hostname_raw, origin_raw = candidate.split("=", 1)
        parsed_routes.append((_normalize_hostname(hostname_raw), _normalize_origin_url(origin_raw)))
    return parsed_routes


def compose_ingress_routes(
    hostname: str,
    origin_url: str,
    extra_routes: Sequence[str] | Sequence[IngressRoute] | None = None,
) -> list[IngressRoute]:
    primary_route: IngressRoute = (_normalize_hostname(hostname), _normalize_origin_url(origin_url))
    ingress_routes: list[IngressRoute] = [primary_route]

    extras: list[IngressRoute] = []
    if extra_routes:
        first = extra_routes[0] if len(extra_routes) > 0 else None
        if isinstance(first, tuple):
            extras = [(_normalize_hostname(item[0]), _normalize_origin_url(item[1])) for item in extra_routes]  # type: ignore[index]
        else:
            extras = parse_extra_routes(extra_routes)  # type: ignore[arg-type]

    by_hostname: dict[str, str] = {primary_route[0]: primary_route[1]}
    for extra_hostname, extra_origin in extras:
        existing = by_hostname.get(extra_hostname)
        if existing and existing != extra_origin:
            raise TunnelSetupError(
                f"Conflicting origins for hostname '{extra_hostname}': '{existing}' vs '{extra_origin}'."
            )
        if not existing:
            ingress_routes.append((extra_hostname, extra_origin))
            by_hostname[extra_hostname] = extra_origin

    return ingress_routes


def default_multi_app_ingress_routes() -> list[IngressRoute]:
    return compose_ingress_routes(
        DEFAULT_HOSTNAME,
        DEFAULT_ORIGIN_URL,
        [
            (DEFAULT_FORMS_HOSTNAME, DEFAULT_FORMS_ORIGIN_URL),
            (DEFAULT_TEMPLATE_HOSTNAME, DEFAULT_TEMPLATE_ORIGIN_URL),
        ],
    )


def build_desired_config(
    tunnel_uuid: str, credentials_file: Path, ingress_routes: Sequence[IngressRoute]
) -> str:
    lines = [
        f"tunnel: {tunnel_uuid}",
        f"credentials-file: {credentials_file}",
        "",
        "ingress:",
    ]
    for hostname, origin_url in ingress_routes:
        lines.append(f"  - hostname: {hostname}")
        lines.append(f"    service: {origin_url}")
    lines.append("  - service: http_status:404")
    return "\n".join(lines) + "\n"


def inspect_config_text(
    raw_text: str,
    *,
    tunnel_uuid: str,
    credentials_file: Path,
    ingress_routes: Sequence[IngressRoute],
) -> dict[str, Any]:
    tunnel_ok = bool(re.search(rf"(?mi)^\s*tunnel:\s*{re.escape(tunnel_uuid)}\s*$", raw_text))
    cred_ok = bool(
        re.search(
            rf"(?mi)^\s*credentials-file:\s*{re.escape(str(credentials_file))}\s*$",
            raw_text,
        )
    )

    route_checks: dict[str, bool] = {}
    route_positions: list[int] = []
    for hostname, origin_url in ingress_routes:
        route_key = f"{hostname}->{origin_url}"
        route_match = re.search(
            rf"(?ms)-\s*hostname:\s*{re.escape(hostname)}\s*[\r\n]+\s*service:\s*{re.escape(origin_url)}\s*",
            raw_text,
        )
        route_checks[route_key] = bool(route_match)
        if route_match:
            route_positions.append(route_match.start())

    all_routes_ok = all(route_checks.values()) if route_checks else False
    fallback_match = re.search(r"(?mi)^\s*-\s*service:\s*http_status:404\s*$", raw_text)
    fallback_ok = bool(fallback_match)
    fallback_after_routes_ok = bool(
        fallback_match and (not route_positions or fallback_match.start() > max(route_positions))
    )
    ingress_ok = all_routes_ok and fallback_ok and fallback_after_routes_ok

    primary_hostname, primary_origin = ingress_routes[0]
    primary_key = f"{primary_hostname}->{primary_origin}"
    hostname_service_ok = bool(route_checks.get(primary_key, False))
    missing_routes = [route for route, ok in route_checks.items() if not ok]

    return {
        "tunnel_ok": tunnel_ok,
        "credentials_ok": cred_ok,
        "hostname_service_ok": hostname_service_ok,
        "route_checks": route_checks,
        "all_routes_ok": all_routes_ok,
        "missing_routes": missing_routes,
        "fallback_ok": fallback_ok,
        "fallback_after_routes_ok": fallback_after_routes_ok,
        "ingress_ok": ingress_ok,
    }


def inspect_config_file(
    config_path: Path,
    *,
    tunnel_uuid: str,
    credentials_file: Path,
    ingress_routes: Sequence[IngressRoute],
) -> dict[str, Any]:
    if not config_path.exists():
        return {
            "exists": False,
            "tunnel_ok": False,
            "credentials_ok": False,
            "hostname_service_ok": False,
            "route_checks": {},
            "all_routes_ok": False,
            "missing_routes": [],
            "fallback_ok": False,
            "fallback_after_routes_ok": False,
            "ingress_ok": False,
        }
    text = config_path.read_text(encoding="utf-8")
    return {
        "exists": True,
        **inspect_config_text(
            text,
            tunnel_uuid=tunnel_uuid,
            credentials_file=credentials_file,
            ingress_routes=ingress_routes,
        ),
    }


def ensure_tunnel_config(
    ctx: RunContext,
    *,
    tunnel_name: str,
    hostname: str,
    origin_url: str,
    config_path: Path,
    cloudflared_dir: Path,
    ingress_routes: Sequence[IngressRoute] | None = None,
) -> dict[str, Any]:
    tunnel_uuid = get_tunnel_uuid(ctx, tunnel_name)
    ensure_directory(cloudflared_dir)
    credentials_file = cloudflared_dir / f"{tunnel_uuid}.json"
    if not credentials_file.exists():
        raise TunnelSetupError(
            f"Missing credentials file '{credentials_file}'. "
            f"Expected from tunnel '{tunnel_name}' ({tunnel_uuid})."
        )

    routes = list(ingress_routes) if ingress_routes else compose_ingress_routes(hostname, origin_url)
    current = inspect_config_file(
        config_path,
        tunnel_uuid=tunnel_uuid,
        credentials_file=credentials_file,
        ingress_routes=routes,
    )
    is_ok = bool(
        current["exists"]
        and current["tunnel_ok"]
        and current["credentials_ok"]
        and current["ingress_ok"]
        and current["all_routes_ok"]
    )
    changed = False
    if not is_ok:
        desired = build_desired_config(tunnel_uuid, credentials_file, routes)
        atomic_write_text(config_path, desired)
        changed = True
        current = inspect_config_file(
            config_path,
            tunnel_uuid=tunnel_uuid,
            credentials_file=credentials_file,
            ingress_routes=routes,
        )

    ingress_ok = bool(
        current["ingress_ok"]
        and current["all_routes_ok"]
        and current["tunnel_ok"]
        and current["credentials_ok"]
    )
    if not ingress_ok:
        raise TunnelSetupError(
            f"Config validation failed after update: {config_path}. Missing routes: {current['missing_routes']}"
        )

    payload = {
        "changed": changed,
        "config_path": str(config_path),
        "cloudflared_dir": str(cloudflared_dir),
        "tunnel_uuid": tunnel_uuid,
        "credentials_file": str(credentials_file),
        "ingress_ok": ingress_ok,
        "ingress_routes": [{"hostname": host, "origin_url": origin} for host, origin in routes],
    }
    ctx.action("ensure_config", "ok", payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure cloudflared config.yml for hitech tunnel.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    parser.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
    parser.add_argument(
        "--extra-route",
        action="append",
        default=[
            f"{DEFAULT_FORMS_HOSTNAME}={DEFAULT_FORMS_ORIGIN_URL}",
            f"{DEFAULT_TEMPLATE_HOSTNAME}={DEFAULT_TEMPLATE_ORIGIN_URL}",
        ],
        help="Additional ingress route format: <hostname>=<origin_url>. Can be repeated.",
    )
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--cloudflared-dir", default=str(DEFAULT_CLOUDFLARED_DIR))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--inspect-only", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    ctx = RunContext(log_dir=Path(args.log_dir), run_id=args.run_id, enable_console=True)

    config_path = Path(args.config_path)
    cloudflared_dir = Path(args.cloudflared_dir)
    try:
        ingress_routes = compose_ingress_routes(args.hostname, args.origin_url, args.extra_route)
        tunnel_uuid = get_tunnel_uuid(ctx, args.tunnel_name)
        credentials_file = cloudflared_dir / f"{tunnel_uuid}.json"
        if args.inspect_only:
            payload = inspect_config_file(
                config_path,
                tunnel_uuid=tunnel_uuid,
                credentials_file=credentials_file,
                ingress_routes=ingress_routes,
            )
            payload.update(
                {
                    "ok": bool(
                        payload["exists"]
                        and payload["tunnel_ok"]
                        and payload["credentials_ok"]
                        and payload["ingress_ok"]
                        and payload["all_routes_ok"]
                    ),
                    "tunnel_uuid": tunnel_uuid,
                    "config_path": str(config_path),
                    "credentials_file": str(credentials_file),
                    "ingress_routes": [
                        {"hostname": host, "origin_url": origin} for host, origin in ingress_routes
                    ],
                }
            )
        else:
            payload = ensure_tunnel_config(
                ctx,
                tunnel_name=args.tunnel_name,
                hostname=args.hostname,
                origin_url=args.origin_url,
                config_path=config_path,
                cloudflared_dir=cloudflared_dir,
                ingress_routes=ingress_routes,
            )
            payload["ok"] = True
    except TunnelSetupError as err:
        ctx.action("ensure_config", "error", {"error": str(err)})
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
