from __future__ import annotations

import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_TUNNEL_NAME = "engine"
DEFAULT_HOSTNAME = "engine.hitechrts.com"
DEFAULT_ORIGIN_URL = "http://localhost:3000"
DEFAULT_CLOUDFLARED_DIR = Path(r"C:\Users\alanh\.cloudflared")
DEFAULT_CONFIG_PATH = DEFAULT_CLOUDFLARED_DIR / "config.yml"
DEFAULT_LOG_DIR = DEFAULT_REPO_ROOT / "logs" / "cloudflare"


UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
HOSTNAME_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")


class TunnelSetupError(RuntimeError):
    """Raised when setup or validation cannot continue safely."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def timestamp_token() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    ensure_directory(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding, newline="\n")
    tmp.replace(path)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


@dataclass
class CommandResult:
    cmd: list[str]
    returncode: int
    stdout: str
    stderr: str
    started_utc: str
    ended_utc: str
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RunContext:
    def __init__(
        self,
        log_dir: Path,
        run_id: str | None = None,
        enable_console: bool = True,
    ) -> None:
        self.log_dir = ensure_directory(log_dir)
        self.run_id = run_id or timestamp_token()
        self.enable_console = enable_console
        self.setup_log_path = self.log_dir / f"setup_{self.run_id}.log"
        self.actions_log_path = self.log_dir / f"actions_{self.run_id}.jsonl"
        if not self.setup_log_path.exists():
            self.setup_log_path.write_text("", encoding="utf-8")
        if not self.actions_log_path.exists():
            self.actions_log_path.write_text("", encoding="utf-8")

    def log(self, message: str, level: str = "INFO") -> None:
        line = f"{utc_now_iso()} [{level}] {message}"
        with self.setup_log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        if self.enable_console:
            print(line, flush=True)

    def action(self, action: str, status: str, details: dict[str, Any] | None = None) -> None:
        payload = {
            "ts_utc": utc_now_iso(),
            "action": action,
            "status": status,
            "details": details or {},
        }
        with self.actions_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        compact_details = json.dumps(payload["details"], sort_keys=True)
        with self.setup_log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{payload['ts_utc']} [{status}] {action} {compact_details}\n")
        if self.enable_console:
            print(f"{payload['ts_utc']} [{status}] {action}", flush=True)


def run_cmd(
    cmd: Sequence[str],
    *,
    timeout: int = 120,
    env: dict[str, str] | None = None,
) -> CommandResult:
    start_epoch = time.time()
    started_utc = utc_now_iso()
    completed = subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        check=False,
    )
    ended_utc = utc_now_iso()
    duration_ms = int((time.time() - start_epoch) * 1000)
    return CommandResult(
        cmd=list(cmd),
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        started_utc=started_utc,
        ended_utc=ended_utc,
        duration_ms=duration_ms,
    )


def run_logged(
    ctx: RunContext,
    cmd: Sequence[str],
    *,
    timeout: int = 120,
    action_name: str | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    result = run_cmd(cmd, timeout=timeout, env=env)
    action = action_name or "command"
    status = "ok" if result.returncode == 0 else "error"
    ctx.action(
        action,
        status,
        {
            "cmd": result.cmd,
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
            "duration_ms": result.duration_ms,
        },
    )
    return result


def ensure_cloudflared_available(ctx: RunContext) -> str:
    exe = shutil.which("cloudflared")
    if not exe:
        message = "cloudflared not found in PATH. Install cloudflared and re-run setup."
        ctx.action("cloudflared_check", "error", {"message": message})
        raise TunnelSetupError(message)
    ctx.action("cloudflared_check", "ok", {"path": exe})
    return exe


def cloudflared(ctx: RunContext, args: Sequence[str], *, timeout: int = 120) -> CommandResult:
    ensure_cloudflared_available(ctx)
    cmd = ["cloudflared", *args]
    return run_logged(ctx, cmd, timeout=timeout, action_name="cloudflared")


def parse_tunnel_uuid_from_list_output(output: str, tunnel_name: str) -> str | None:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in lines:
        if tunnel_name.lower() not in line.lower():
            continue
        uuid_match = UUID_RE.search(line)
        if uuid_match:
            return uuid_match.group(0).lower()
    return None


def get_tunnel_uuid(ctx: RunContext, tunnel_name: str) -> str:
    json_result = cloudflared(ctx, ["tunnel", "list", "--output", "json"], timeout=180)
    if json_result.returncode == 0:
        try:
            data = json.loads(json_result.stdout)
            for item in data:
                if str(item.get("name", "")).strip().lower() == tunnel_name.lower():
                    uuid = str(item.get("id", "")).strip().lower()
                    if UUID_RE.fullmatch(uuid):
                        ctx.action("tunnel_uuid_lookup", "ok", {"tunnel_name": tunnel_name, "tunnel_uuid": uuid})
                        return uuid
        except json.JSONDecodeError:
            pass

    text_result = cloudflared(ctx, ["tunnel", "list"], timeout=180)
    if text_result.returncode != 0:
        raise TunnelSetupError(
            f"Unable to list tunnels for '{tunnel_name}'. stderr: {text_result.stderr.strip() or 'n/a'}"
        )
    uuid = parse_tunnel_uuid_from_list_output(text_result.stdout, tunnel_name)
    if not uuid:
        raise TunnelSetupError(
            f"Tunnel '{tunnel_name}' was not found. Create/auth it first (cloudflared tunnel create {tunnel_name})."
        )
    ctx.action("tunnel_uuid_lookup", "ok", {"tunnel_name": tunnel_name, "tunnel_uuid": uuid})
    return uuid


def hostname_bound_in_dns_output(output: str, hostname: str) -> bool:
    return hostname.lower() in output.lower()


def list_dns_hostnames(output: str) -> list[str]:
    hostnames: list[str] = []
    for line in output.splitlines():
        for match in HOSTNAME_RE.findall(line):
            lowered = match.lower()
            if lowered not in hostnames:
                hostnames.append(lowered)
    return hostnames


def get_connections_count_from_info_json(payload: dict[str, Any]) -> int:
    if isinstance(payload.get("connections"), list):
        return len(payload["connections"])
    if isinstance(payload.get("connectors"), list):
        return len(payload["connectors"])
    if isinstance(payload.get("haConnections"), list):
        return len(payload["haConnections"])
    return 0


def parse_connections_count_from_text(output: str) -> int:
    patterns = [
        r"connections?\s*:\s*(\d+)",
        r"active\s+connections?\s*:\s*(\d+)",
        r"(\d+)\s+active\s+connections?",
    ]
    for pattern in patterns:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))

    lines = [line.strip().lower() for line in output.splitlines() if line.strip()]
    connector_lines = [line for line in lines if "connector" in line and ("colo" in line or "connected" in line)]
    if connector_lines:
        return len(connector_lines)

    tunnel_lines = [line for line in lines if "registered tunnel connection" in line]
    if tunnel_lines:
        return len(tunnel_lines)

    table_rows = []
    for raw in output.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if UUID_RE.match(stripped):
            table_rows.append(stripped)
    if table_rows:
        return len(table_rows)

    return 0


def get_tunnel_connections_count(ctx: RunContext, tunnel_name: str) -> int:
    info_json = cloudflared(ctx, ["tunnel", "info", tunnel_name, "--output", "json"], timeout=180)
    if info_json.returncode == 0:
        try:
            payload = json.loads(info_json.stdout)
            count = get_connections_count_from_info_json(payload)
            ctx.action("tunnel_connections", "ok", {"mode": "json", "connections_count": count})
            return count
        except json.JSONDecodeError:
            pass

    info_text = cloudflared(ctx, ["tunnel", "info", tunnel_name], timeout=180)
    if info_text.returncode != 0:
        raise TunnelSetupError(
            f"Unable to read tunnel info for '{tunnel_name}'. stderr: {info_text.stderr.strip() or 'n/a'}"
        )
    count = parse_connections_count_from_text(info_text.stdout)
    ctx.action("tunnel_connections", "ok", {"mode": "text", "connections_count": count})
    return count


def origin_reachable(url: str, timeout_seconds: int = 4) -> tuple[bool, int | None, str | None]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return True, int(response.status), None
    except urllib.error.HTTPError as err:
        # HTTP error means origin answered; still reachable.
        return True, int(err.code), str(err)
    except Exception as err:  # noqa: BLE001
        return False, None, str(err)


def is_windows_admin() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:  # noqa: BLE001
        return False


def _to_ps_single_quoted(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_python_elevated(
    ctx: RunContext,
    script_path: Path,
    script_args: Sequence[str],
    *,
    timeout: int = 600,
) -> CommandResult:
    python_exe = str(Path(sys.executable).resolve())
    arg_list = [str(script_path), *[str(item) for item in script_args]]
    arg_literal = ", ".join(_to_ps_single_quoted(item) for item in arg_list)
    command = (
        f"$argList = @({arg_literal}); "
        f"$p = Start-Process -FilePath {_to_ps_single_quoted(python_exe)} "
        f"-ArgumentList $argList -Verb RunAs -Wait -PassThru; "
        "if ($null -eq $p) { exit 9001 }; "
        "exit $p.ExitCode"
    )
    result = run_logged(
        ctx,
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        timeout=timeout,
        action_name="elevated_python",
    )
    return result


def service_status_snapshot() -> dict[str, Any]:
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "$svc = Get-Service -Name 'cloudflared' -ErrorAction SilentlyContinue; "
            "if ($null -eq $svc) { "
            "@{installed=$false; service_name='cloudflared'} | ConvertTo-Json -Compress "
            "} else { "
            "$c = Get-CimInstance Win32_Service -Filter \"Name='cloudflared'\"; "
            "@{installed=$true; service_name='cloudflared'; status=$svc.Status.ToString(); "
            "start_mode=$c.StartMode; state=$c.State; path_name=$c.PathName} | ConvertTo-Json -Compress }"
        ),
    ]
    result = run_cmd(cmd, timeout=60)
    if result.returncode != 0:
        return {
            "installed": False,
            "service_name": "cloudflared",
            "status": "Unknown",
            "start_mode": "Unknown",
            "state": "Unknown",
            "path_name": "",
        }
    try:
        payload = json.loads(result.stdout)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass
    return {
        "installed": False,
        "service_name": "cloudflared",
        "status": "Unknown",
        "start_mode": "Unknown",
        "state": "Unknown",
        "path_name": "",
    }

