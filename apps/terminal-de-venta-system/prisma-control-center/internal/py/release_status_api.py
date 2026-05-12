
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from blackbox_bridge import blackbox_root, ensure_dirs
except Exception:
    blackbox_root = None
    ensure_dirs = None

SOURCE = "prisma-release-status-api"
VERSION = "crystal-ops-release-1.0"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _control_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _blackbox_root() -> Path:
    if blackbox_root is None:
        return Path(r"F:\Black-box").resolve()
    root = blackbox_root()
    if ensure_dirs is not None:
        ensure_dirs(root)
    return root


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _tail_jsonl(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            out.append({"raw": line[:500]})
    return out


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            low = str(k).lower()
            if any(t in low for t in ["path", "root", "log", "command", "cmd", "pid", "process", "token", "secret", "stdout", "stderr", "backup"]):
                out[k] = "<redacted>"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(value, str) and (":\\" in value or ":/" in value):
        return "<redacted>"
    return value


def _exists(path: Path, public: bool = False) -> dict[str, Any]:
    return {
        "path": "<redacted>" if public else str(path),
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() and path.is_file() else None,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if path.exists() else None,
    }


def _incident_count(root: Path, state: str) -> int:
    folder = root / "incidents" / state
    if not folder.exists():
        return 0
    return len([p for p in folder.iterdir() if p.is_dir() and p.name.startswith("INC_CC_")])


def _features(control_root: Path) -> dict[str, bool]:
    web = control_root / "internal" / "web"
    py = control_root / "internal" / "py"
    panel_text = (py / "panel_3150.py").read_text(encoding="utf-8", errors="replace") if (py / "panel_3150.py").exists() else ""
    app_text = (web / "app.js").read_text(encoding="utf-8", errors="replace") if (web / "app.js").exists() else ""
    return {
        "iter1CrystalShell": "PRISMA Crystal Ops Console" in (web / "index.html").read_text(encoding="utf-8", errors="replace") if (web / "index.html").exists() else False,
        "iter2DataCore": "deriveModel" in app_text and "PRISMA Data Core brief" in app_text,
        "iter3BlackboxCommand": "blackbox_command_payload" in panel_text and (py / "blackbox_command_api.py").exists(),
        "iter4OpsActions": "ops_command_payload" in panel_text and (py / "ops_command_api.py").exists(),
        "iter5ReleasePolish": "release_status_payload" in panel_text and (py / "release_status_api.py").exists(),
    }


def release_status_payload(path_text: str, public: bool = False) -> dict[str, Any]:
    _ = urlparse(path_text)
    control_root = _control_root()
    blackbox = _blackbox_root()
    web = control_root / "internal" / "web"
    py = control_root / "internal" / "py"
    latest_health = _read_json(blackbox / "runtime" / "control_center_latest.json", {})
    latest_bridge = _read_json(blackbox / "runtime" / "control_center_bridge_latest.json", {})
    features = _features(control_root)
    checks = {
        "controlRoot": _exists(control_root, public),
        "blackboxRoot": _exists(blackbox, public),
        "panel": _exists(py / "panel_3150.py", public),
        "index": _exists(web / "index.html", public),
        "app": _exists(web / "app.js", public),
        "releaseCss": _exists(web / "release_polish.css", public),
        "releaseJs": _exists(web / "release_console.js", public),
        "latestHealth": _exists(blackbox / "runtime" / "control_center_latest.json", public),
        "latestBridge": _exists(blackbox / "runtime" / "control_center_bridge_latest.json", public),
        "events": _exists(blackbox / "runtime" / "prisma_black_box_events.jsonl", public),
        "timeline": _exists(blackbox / "incidents" / "timeline" / "control_center.timeline.jsonl", public),
    }
    blockers = []
    if not all(features.values()):
        blockers.append("No todas las iteraciones estan detectadas en archivos.")
    if not latest_bridge.get("ok"):
        blockers.append("Latest bridge no reporta ok=true.")
    if latest_health.get("overallStatus") not in ["PASS", "DEGRADED", "WARN"]:
        blockers.append("Latest health no esta en un estado esperado.")
    status = "READY_WITH_WARNINGS" if blockers else "READY"
    payload = {
        "schemaVersion": "1.0",
        "source": SOURCE,
        "version": VERSION,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "status": status,
        "blockers": blockers,
        "features": features,
        "health": {
            "overallStatus": latest_health.get("overallStatus") if isinstance(latest_health, dict) else None,
            "healthScore": latest_health.get("healthScore") if isinstance(latest_health, dict) else None,
            "runId": latest_health.get("runId") if isinstance(latest_health, dict) else None,
            "recommendedNextAction": latest_health.get("recommendedNextAction") if isinstance(latest_health, dict) else None,
        },
        "bridge": latest_bridge,
        "counts": {
            "activeIncidents": _incident_count(blackbox, "active"),
            "resolvedIncidents": _incident_count(blackbox, "resolved"),
            "timelineTail": len(_tail_jsonl(blackbox / "incidents" / "timeline" / "control_center.timeline.jsonl", 30)),
            "eventTail": len(_tail_jsonl(blackbox / "runtime" / "prisma_black_box_events.jsonl", 30)),
        },
        "checks": checks,
        "operator": {
            "localUrl": "http://127.0.0.1:3150",
            "healthApi": "/api/health",
            "incidentsApi": "/api/incidents",
            "blackboxApi": "/api/blackbox/summary",
            "opsApi": "/api/ops/cloudflare",
            "releaseApi": "/api/release/status",
            "latestReport": "/latest/health.html",
        },
    }
    return _redact(payload) if public else payload
