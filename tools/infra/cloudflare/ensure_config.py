from __future__ import annotations

import argparse
import json
import re
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
    atomic_write_text,
    ensure_directory,
    get_tunnel_uuid,
)


def build_desired_config(tunnel_uuid: str, credentials_file: Path, hostname: str, origin_url: str) -> str:
    return (
        f"tunnel: {tunnel_uuid}\n"
        f"credentials-file: {credentials_file}\n"
        "\n"
        "ingress:\n"
        f"  - hostname: {hostname}\n"
        f"    service: {origin_url}\n"
        "  - service: http_status:404\n"
    )


def inspect_config_text(
    raw_text: str,
    *,
    tunnel_uuid: str,
    credentials_file: Path,
    hostname: str,
    origin_url: str,
) -> dict[str, bool]:
    tunnel_ok = bool(re.search(rf"(?mi)^\s*tunnel:\s*{re.escape(tunnel_uuid)}\s*$", raw_text))
    cred_ok = bool(
        re.search(
            rf"(?mi)^\s*credentials-file:\s*{re.escape(str(credentials_file))}\s*$",
            raw_text,
        )
    )
    hostname_service_ok = bool(
        re.search(
            rf"(?ms)-\s*hostname:\s*{re.escape(hostname)}\s*[\r\n]+\s*service:\s*{re.escape(origin_url)}\s*",
            raw_text,
        )
    )
    fallback_ok = bool(re.search(r"(?mi)^\s*-\s*service:\s*http_status:404\s*$", raw_text))
    ingress_ok = hostname_service_ok and fallback_ok
    return {
        "tunnel_ok": tunnel_ok,
        "credentials_ok": cred_ok,
        "hostname_service_ok": hostname_service_ok,
        "fallback_ok": fallback_ok,
        "ingress_ok": ingress_ok,
    }


def inspect_config_file(
    config_path: Path,
    *,
    tunnel_uuid: str,
    credentials_file: Path,
    hostname: str,
    origin_url: str,
) -> dict[str, Any]:
    if not config_path.exists():
        return {
            "exists": False,
            "tunnel_ok": False,
            "credentials_ok": False,
            "hostname_service_ok": False,
            "fallback_ok": False,
            "ingress_ok": False,
        }
    text = config_path.read_text(encoding="utf-8")
    return {"exists": True, **inspect_config_text(text, tunnel_uuid=tunnel_uuid, credentials_file=credentials_file, hostname=hostname, origin_url=origin_url)}


def ensure_tunnel_config(
    ctx: RunContext,
    *,
    tunnel_name: str,
    hostname: str,
    origin_url: str,
    config_path: Path,
    cloudflared_dir: Path,
) -> dict[str, Any]:
    tunnel_uuid = get_tunnel_uuid(ctx, tunnel_name)
    ensure_directory(cloudflared_dir)
    credentials_file = cloudflared_dir / f"{tunnel_uuid}.json"
    if not credentials_file.exists():
        raise TunnelSetupError(
            f"Missing credentials file '{credentials_file}'. "
            f"Expected from tunnel '{tunnel_name}' ({tunnel_uuid})."
        )

    current = inspect_config_file(
        config_path,
        tunnel_uuid=tunnel_uuid,
        credentials_file=credentials_file,
        hostname=hostname,
        origin_url=origin_url,
    )
    is_ok = bool(current["exists"] and current["tunnel_ok"] and current["credentials_ok"] and current["ingress_ok"])
    changed = False
    if not is_ok:
        desired = build_desired_config(tunnel_uuid, credentials_file, hostname, origin_url)
        atomic_write_text(config_path, desired)
        changed = True
        current = inspect_config_file(
            config_path,
            tunnel_uuid=tunnel_uuid,
            credentials_file=credentials_file,
            hostname=hostname,
            origin_url=origin_url,
        )

    ingress_ok = bool(current["ingress_ok"] and current["tunnel_ok"] and current["credentials_ok"])
    if not ingress_ok:
        raise TunnelSetupError(f"Config validation failed after update: {config_path}")

    payload = {
        "changed": changed,
        "config_path": str(config_path),
        "cloudflared_dir": str(cloudflared_dir),
        "tunnel_uuid": tunnel_uuid,
        "credentials_file": str(credentials_file),
        "ingress_ok": ingress_ok,
    }
    ctx.action("ensure_config", "ok", payload)
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure cloudflared config.yml for hitech tunnel.")
    parser.add_argument("--tunnel-name", default=DEFAULT_TUNNEL_NAME)
    parser.add_argument("--hostname", default=DEFAULT_HOSTNAME)
    parser.add_argument("--origin-url", default=DEFAULT_ORIGIN_URL)
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
        tunnel_uuid = get_tunnel_uuid(ctx, args.tunnel_name)
        credentials_file = cloudflared_dir / f"{tunnel_uuid}.json"
        if args.inspect_only:
            payload = inspect_config_file(
                config_path,
                tunnel_uuid=tunnel_uuid,
                credentials_file=credentials_file,
                hostname=args.hostname,
                origin_url=args.origin_url,
            )
            payload.update(
                {
                    "ok": bool(payload["exists"] and payload["tunnel_ok"] and payload["credentials_ok"] and payload["ingress_ok"]),
                    "tunnel_uuid": tunnel_uuid,
                    "config_path": str(config_path),
                    "credentials_file": str(credentials_file),
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

