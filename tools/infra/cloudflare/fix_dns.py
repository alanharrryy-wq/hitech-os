from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from cloudflared_helpers import (
    DEFAULT_HOSTNAME,
    DEFAULT_LOG_DIR,
    DEFAULT_TUNNEL_NAME,
    RunContext,
    TunnelSetupError,
    cloudflared,
    hostname_bound_in_dns_output,
    list_dns_hostnames,
)


def _list_dns_if_supported(ctx: RunContext, tunnel_name: str) -> tuple[bool, Any]:
    attempted = cloudflared(ctx, ["tunnel", "route", "dns", "list", "--tunnel", tunnel_name], timeout=180)
    if attempted.returncode == 0:
        return True, attempted
    combined = f"{attempted.stdout}\n{attempted.stderr}".lower()
    unsupported_markers = [
        "expects the format",
        "unknown flag",
        "no help topic",
        "not enough arguments",
    ]
    unsupported = any(marker in combined for marker in unsupported_markers)
    if unsupported:
        return False, attempted
    raise TunnelSetupError(
        f"Failed to list DNS routes for tunnel '{tunnel_name}'. "
        f"stderr: {attempted.stderr.strip() or attempted.stdout.strip() or 'n/a'}"
    )


def ensure_dns_binding(ctx: RunContext, tunnel_name: str, hostname: str) -> dict[str, Any]:
    list_supported, list_before = _list_dns_if_supported(ctx, tunnel_name)
    if list_supported:
        bound_before = hostname_bound_in_dns_output(list_before.stdout, hostname)
        if bound_before:
            ctx.action(
                "dns_route",
                "ok",
                {
                    "tunnel_name": tunnel_name,
                    "hostname": hostname,
                    "changed": False,
                    "bound": True,
                    "list_supported": True,
                    "hostnames_seen": list_dns_hostnames(list_before.stdout),
                },
            )
            return {
                "changed": False,
                "hostname_bound": True,
                "list_supported": True,
                "hostnames_seen": list_dns_hostnames(list_before.stdout),
            }

        add_result = cloudflared(ctx, ["tunnel", "route", "dns", "add", tunnel_name, hostname], timeout=180)
        add_combined = f"{add_result.stdout}\n{add_result.stderr}".lower()
        add_ok = add_result.returncode == 0 or "already exists" in add_combined
        if not add_ok:
            raise TunnelSetupError(
                f"Unable to bind hostname '{hostname}' to tunnel '{tunnel_name}'. "
                f"stderr: {add_result.stderr.strip() or add_result.stdout.strip() or 'n/a'}"
            )

        list_after = cloudflared(ctx, ["tunnel", "route", "dns", "list", "--tunnel", tunnel_name], timeout=180)
        if list_after.returncode != 0:
            raise TunnelSetupError(
                f"Re-check failed for DNS routes on tunnel '{tunnel_name}'. "
                f"stderr: {list_after.stderr.strip() or list_after.stdout.strip() or 'n/a'}"
            )
        bound_after = hostname_bound_in_dns_output(list_after.stdout, hostname)
        if not bound_after:
            raise TunnelSetupError(
                f"Hostname '{hostname}' is still missing after route add. "
                "Resolve Cloudflare API permissions and run setup again."
            )

        result = {
            "changed": True,
            "hostname_bound": True,
            "list_supported": True,
            "hostnames_seen": list_dns_hostnames(list_after.stdout),
        }
        ctx.action(
            "dns_route",
            "ok",
            {"tunnel_name": tunnel_name, "hostname": hostname, **result},
        )
        return result

    # Fallback for cloudflared builds where `route dns list` is unavailable.
    fallback_ensure = None
    combined = ""
    for attempt in range(1, 4):
        candidate = cloudflared(ctx, ["tunnel", "route", "dns", tunnel_name, hostname], timeout=180)
        candidate_combined = f"{candidate.stdout}\n{candidate.stderr}".lower()
        if candidate.returncode == 0:
            fallback_ensure = candidate
            combined = candidate_combined
            break
        fallback_ensure = candidate
        combined = candidate_combined
        ctx.action(
            "dns_route_retry",
            "warning",
            {
                "attempt": attempt,
                "tunnel_name": tunnel_name,
                "hostname": hostname,
                "stderr": candidate.stderr.strip() or candidate.stdout.strip(),
            },
        )
        time.sleep(1.5 * attempt)

    if fallback_ensure is None or fallback_ensure.returncode != 0:
        raise TunnelSetupError(
            f"Unable to ensure hostname route '{hostname}'. "
            f"stderr: {fallback_ensure.stderr.strip() or fallback_ensure.stdout.strip() or 'n/a'}"
        )
    changed = "already configured" not in combined and "already exists" not in combined
    result = {
        "changed": changed,
        "hostname_bound": True,
        "list_supported": False,
        "hostnames_seen": [hostname.lower()],
    }
    ctx.action(
        "dns_route",
        "ok",
        {"tunnel_name": tunnel_name, "hostname": hostname, "fallback_mode": "route_dns_direct", **result},
    )
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure DNS route for Cloudflare tunnel hostname.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--json-out", default=None)
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    ctx = RunContext(log_dir=Path(args.log_dir), run_id=args.run_id, enable_console=True)
    try:
        payload = ensure_dns_binding(ctx, args.tunnel_name, args.hostname)
    except TunnelSetupError as err:
        ctx.action("dns_route", "error", {"error": str(err)})
        if args.json_out:
            Path(args.json_out).write_text(json.dumps({"ok": False, "error": str(err)}, indent=2) + "\n", encoding="utf-8")
        print(f"ERROR: {err}")
        return 2

    response = {"ok": True, **payload, "tunnel_name": args.tunnel_name, "hostname": args.hostname}
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(response, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(response, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
