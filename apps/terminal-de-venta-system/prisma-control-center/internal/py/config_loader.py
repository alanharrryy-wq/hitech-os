from __future__ import annotations

import json
import os
import socket
from pathlib import Path
from typing import Any


PY_ROOT = Path(__file__).resolve().parent
INTERNAL_ROOT = PY_ROOT.parent
CONTROL_ROOT = INTERNAL_ROOT.parent
TERMINAL_ROOT = CONTROL_ROOT.parent
REPO_ROOT = TERMINAL_ROOT.parents[1]
CONFIG_ROOT = INTERNAL_ROOT / "config"
WEB_ROOT = INTERNAL_ROOT / "web"
TEMPLATES_ROOT = INTERNAL_ROOT / "templates"
LOG_ROOT = REPO_ROOT / "tools" / "_local" / "logs" / "prisma-control-center"
LATEST_ROOT = LOG_ROOT / "latest"
STATE_FILE = LOG_ROOT / "state.json"
CONTROL_CENTER_PORT = 3150


def ensure_log_dirs() -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    LATEST_ROOT.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=False)
        handle.write("\n")


def load_services_config() -> dict[str, Any]:
    return read_json(CONFIG_ROOT / "services.json")


def load_cloudflare_config() -> dict[str, Any]:
    return read_json(CONFIG_ROOT / "cloudflare.json")


def load_health_profiles() -> dict[str, Any]:
    return read_json(CONFIG_ROOT / "health_profiles.json")


def load_safety_policy() -> dict[str, Any]:
    return read_json(CONFIG_ROOT / "safety_policy.json")


def active_health_profile() -> dict[str, Any]:
    payload = load_health_profiles()
    name = payload.get("activeProfile", "standard")
    profile = payload.get("profiles", {}).get(name)
    if not isinstance(profile, dict):
        raise ValueError(f"Missing health profile: {name}")
    merged = dict(profile)
    merged["name"] = name
    return merged


def detect_lan_ip() -> str:
    candidates: list[str] = []
    try:
        hostname = socket.gethostname()
        candidates.extend(socket.gethostbyname_ex(hostname)[2])
    except OSError:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.2)
            sock.connect(("8.8.8.8", 80))
            candidates.append(sock.getsockname()[0])
    except OSError:
        pass
    for ip in candidates:
        if ip.startswith(("10.", "172.", "192.168.")):
            return ip
    return candidates[0] if candidates else "127.0.0.1"


def render_placeholders(value: Any, lan_ip: str | None = None) -> Any:
    if isinstance(value, str):
        return value.replace("{lanIp}", lan_ip or detect_lan_ip())
    if isinstance(value, list):
        return [render_placeholders(item, lan_ip) for item in value]
    if isinstance(value, dict):
        return {key: render_placeholders(item, lan_ip) for key, item in value.items()}
    return value


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"schemaVersion": "1.0", "managedProcesses": [], "lastGoodHealth": None}
    try:
        payload = read_json(STATE_FILE)
    except (OSError, json.JSONDecodeError):
        return {"schemaVersion": "1.0", "managedProcesses": [], "lastGoodHealth": None}
    if not isinstance(payload, dict):
        return {"schemaVersion": "1.0", "managedProcesses": [], "lastGoodHealth": None}
    payload.setdefault("managedProcesses", [])
    return payload


def save_state(payload: dict[str, Any]) -> None:
    ensure_log_dirs()
    write_json(STATE_FILE, payload)


def python_executable() -> str:
    return os.environ.get("PYTHON_EXE") or os.environ.get("PYTHON") or "python"


def absolute(path: str | Path) -> str:
    return str(Path(path).resolve())
