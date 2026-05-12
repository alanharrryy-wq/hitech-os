
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

try:
    from blackbox_bridge import blackbox_root, ensure_dirs
except Exception:
    blackbox_root = None
    ensure_dirs = None

BRIDGE_NAME = "prisma-blackbox-command-api"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _tail_jsonl(path: Path, limit: int = 80) -> list[dict[str, Any]]:
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
            out.append({"raw": line})
    return out


def _root() -> Path:
    if blackbox_root is None:
        return Path(r"F:\Black-box").resolve()
    root = blackbox_root()
    if ensure_dirs is not None:
        ensure_dirs(root)
    return root


def _incident_dirs(root: Path, state: str) -> list[Path]:
    base = root / "incidents" / state
    if not base.exists():
        return []
    return sorted([p for p in base.iterdir() if p.is_dir() and p.name.startswith("INC_CC_")], key=lambda p: p.stat().st_mtime, reverse=True)


def _incident_from_dir(path: Path, public: bool = False) -> dict[str, Any]:
    incident = _read_json(path / "incident.json", {})
    if not isinstance(incident, dict):
        incident = {}
    incident.setdefault("id", path.name)
    incident["folderName"] = path.name
    incident["evidenceFiles"] = _evidence_files(path, public=public)
    if public:
        incident = _redact(incident)
    return incident


def _evidence_files(incident_dir: Path, public: bool = False) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    candidates = [incident_dir / "evidence", incident_dir]
    for base in candidates:
        if not base.exists():
            continue
        for file in sorted(base.rglob("*")):
            if not file.is_file():
                continue
            try:
                out.append({
                    "name": file.name,
                    "relativePath": str(file.relative_to(incident_dir)).replace("\\", "/"),
                    "path": "<redacted>" if public else str(file),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(timespec="seconds"),
                    "kind": file.suffix.lower().lstrip(".") or "file",
                })
            except Exception:
                pass
    return out


def _safe_limit(qs: dict[str, list[str]], default: int = 80, maximum: int = 500) -> int:
    try:
        return max(1, min(maximum, int((qs.get("limit") or [default])[0])))
    except Exception:
        return default


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            low = str(k).lower()
            if any(token in low for token in ["path", "root", "log", "command", "cmd", "pid", "process", "token", "secret"]):
                out[k] = "<redacted>"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(value, str) and (":\\" in value or ":/" in value):
        return "<redacted>"
    return value


def _timeline(root: Path, limit: int, public: bool) -> list[dict[str, Any]]:
    events = _tail_jsonl(root / "incidents" / "timeline" / "control_center.timeline.jsonl", limit=limit)
    return _redact(events) if public else events


def _events(root: Path, limit: int, public: bool) -> list[dict[str, Any]]:
    events = _tail_jsonl(root / "runtime" / "prisma_black_box_events.jsonl", limit=limit)
    return _redact(events) if public else events


def _summary(root: Path, public: bool, limit: int = 80) -> dict[str, Any]:
    active = [_incident_from_dir(p, public=public) for p in _incident_dirs(root, "active")]
    resolved = [_incident_from_dir(p, public=public) for p in _incident_dirs(root, "resolved")[:20]]
    latest_bridge = _read_json(root / "runtime" / "control_center_bridge_latest.json", {})
    latest_health = _read_json(root / "runtime" / "control_center_latest.json", {})
    timeline = _timeline(root, limit=limit, public=public)
    events = _events(root, limit=limit, public=public)
    payload = {
        "schemaVersion": "1.0",
        "source": BRIDGE_NAME,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "blackBoxRoot": "<redacted>" if public else str(root),
        "counts": {
            "active": len(active),
            "resolvedRecent": len(resolved),
            "timelineTail": len(timeline),
            "eventTail": len(events),
        },
        "latestBridge": _redact(latest_bridge) if public else latest_bridge,
        "latestHealthSummary": _redact({
            "runId": latest_health.get("runId") if isinstance(latest_health, dict) else None,
            "overallStatus": latest_health.get("overallStatus") if isinstance(latest_health, dict) else None,
            "healthScore": latest_health.get("healthScore") if isinstance(latest_health, dict) else None,
            "recommendedNextAction": latest_health.get("recommendedNextAction") if isinstance(latest_health, dict) else None,
            "generatedAt": latest_health.get("generatedAt") if isinstance(latest_health, dict) else None,
        }) if public else {
            "runId": latest_health.get("runId") if isinstance(latest_health, dict) else None,
            "overallStatus": latest_health.get("overallStatus") if isinstance(latest_health, dict) else None,
            "healthScore": latest_health.get("healthScore") if isinstance(latest_health, dict) else None,
            "recommendedNextAction": latest_health.get("recommendedNextAction") if isinstance(latest_health, dict) else None,
            "generatedAt": latest_health.get("generatedAt") if isinstance(latest_health, dict) else None,
        },
        "activeIncidents": active,
        "resolvedRecent": resolved,
        "timelineTail": timeline,
        "eventTail": events,
    }
    return payload


def _evidence(root: Path, incident_id: str, public: bool) -> dict[str, Any]:
    clean = "".join(ch for ch in incident_id if ch.isalnum() or ch in "_-.")
    candidates = [root / "incidents" / "active" / clean, root / "incidents" / "resolved" / clean]
    for path in candidates:
        if path.exists() and path.is_dir():
            incident = _incident_from_dir(path, public=public)
            return {
                "schemaVersion": "1.0",
                "source": BRIDGE_NAME,
                "time": _now(),
                "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
                "found": True,
                "incident": incident,
            }
    return {
        "schemaVersion": "1.0",
        "source": BRIDGE_NAME,
        "time": _now(),
        "found": False,
        "id": clean,
    }


def blackbox_command_payload(path_text: str, public: bool = False) -> dict[str, Any]:
    root = _root()
    parsed = urlparse(path_text)
    qs = parse_qs(parsed.query)
    path = parsed.path.rstrip("/") or "/api/blackbox/summary"
    limit = _safe_limit(qs, default=80)

    if path == "/api/blackbox/timeline":
        return {"schemaVersion": "1.0", "source": BRIDGE_NAME, "time": _now(), "items": _timeline(root, limit=limit, public=public), "limit": limit}
    if path == "/api/blackbox/event-tail":
        return {"schemaVersion": "1.0", "source": BRIDGE_NAME, "time": _now(), "items": _events(root, limit=limit, public=public), "limit": limit}
    if path == "/api/blackbox/resolved":
        items = [_incident_from_dir(p, public=public) for p in _incident_dirs(root, "resolved")[:limit]]
        return {"schemaVersion": "1.0", "source": BRIDGE_NAME, "time": _now(), "items": items, "limit": limit}
    if path == "/api/blackbox/evidence":
        incident_id = (qs.get("id") or [""])[0]
        return _evidence(root, incident_id, public=public)
    return _summary(root, public=public, limit=limit)
