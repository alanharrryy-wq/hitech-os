from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRIDGE_NAME = "prisma-control-center-blackbox-bridge"
DEFAULT_BLACKBOX_ROOT = Path(r"F:\\Black-box")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "blackbox_bridge.json"


def blackbox_root(value: str | Path | None = None) -> Path:
    if value:
        return Path(value).expanduser().resolve()

    env_value = os.environ.get("PRISMA_BLACKBOX_ROOT", "").strip()
    if env_value:
        return Path(env_value).expanduser().resolve()

    config = _read_json(_config_path(), {})
    if isinstance(config, dict) and config.get("blackBoxRoot"):
        return Path(str(config["blackBoxRoot"])).expanduser().resolve()

    return DEFAULT_BLACKBOX_ROOT.resolve()


def ensure_dirs(root: Path) -> None:
    for rel in [
        "runtime",
        "reports",
        "logs",
        "evidence",
        "incidents/active",
        "incidents/resolved",
        "incidents/timeline",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def status_of(payload: dict[str, Any]) -> str:
    return str(
        payload.get("overallStatus")
        or payload.get("status")
        or payload.get("state")
        or "UNKNOWN"
    ).upper()


def severity_of(status: str) -> str:
    if status in {"FAIL", "BLOCKED", "ERROR"}:
        return "FAIL"
    if status in {"DEGRADED", "WARN", "WARNING", "UNKNOWN", "EMPTY"}:
        return "WARN"
    return "PASS"


def bad_services(payload: dict[str, Any]) -> list[dict[str, Any]]:
    services = payload.get("services", []) or []
    out = []
    for service in services:
        service_status = str(service.get("status", "")).upper()
        if service_status != "PASS":
            out.append(
                {
                    "id": service.get("id"),
                    "name": service.get("name"),
                    "port": service.get("port"),
                    "status": service.get("status"),
                    "criticality": service.get("criticality"),
                    "blocked": service.get("blocked"),
                }
            )
    return out


def fingerprint(payload: dict[str, Any]) -> str:
    cloudflare = payload.get("cloudflare", {}) or {}
    service_bits = [
        f"{item.get('id')}:{item.get('port')}:{item.get('status')}"
        for item in bad_services(payload)
    ]
    raw = "|".join(
        [
            "control-center",
            status_of(payload),
            str(cloudflare.get("status", "")),
            ",".join(sorted(service_bits)),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def active_incident_dirs(root: Path) -> list[Path]:
    active_root = root / "incidents" / "active"
    if not active_root.exists():
        return []
    return [
        item for item in active_root.iterdir()
        if item.is_dir() and item.name.startswith("INC_CC_")
    ]


def resolve_active_incidents(root: Path, payload: dict[str, Any]) -> list[str]:
    resolved = []
    for incident_dir in active_incident_dirs(root):
        incident = _read_json(incident_dir / "incident.json", {})
        incident.update(
            {
                "state": "RESOLVED",
                "resolvedAt": _now(),
                "resolvedBy": BRIDGE_NAME,
                "lastPayloadRunId": payload.get("runId"),
            }
        )

        resolved_dir = root / "incidents" / "resolved" / incident_dir.name
        if resolved_dir.exists():
            shutil.rmtree(resolved_dir)

        resolved_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(incident_dir), str(resolved_dir))
        _write_json(resolved_dir / "incident.json", incident)
        resolved.append(incident_dir.name)

    return resolved


def open_or_update_incident(root: Path, payload: dict[str, Any], report_paths: dict[str, str]) -> str:
    fp = fingerprint(payload)
    incident_id = "INC_CC_" + fp
    incident_dir = root / "incidents" / "active" / incident_id
    old_incident = _read_json(incident_dir / "incident.json", {})

    incident = {
        "schemaVersion": "1.0",
        "id": incident_id,
        "source": "prisma-control-center",
        "bridge": BRIDGE_NAME,
        "state": "ACTIVE",
        "severity": severity_of(status_of(payload)),
        "status": status_of(payload),
        "fingerprint": fp,
        "createdAt": old_incident.get("createdAt") or _now(),
        "updatedAt": _now(),
        "runId": payload.get("runId"),
        "healthScore": payload.get("healthScore"),
        "recommendedNextAction": payload.get("recommendedNextAction"),
        "badServices": bad_services(payload),
        "cloudflareStatus": (payload.get("cloudflare", {}) or {}).get("status"),
        "reportPaths": report_paths,
    }

    _write_json(incident_dir / "incident.json", incident)
    _write_json(incident_dir / "evidence" / "control_center_health.json", payload)

    return incident_id


def emit_control_center_report(
    payload: dict[str, Any],
    report_paths: dict[str, str] | None = None,
    blackbox_root_value: str | Path | None = None,
) -> dict[str, Any]:
    root = blackbox_root(blackbox_root_value)
    ensure_dirs(root)

    report_paths = report_paths or {}
    status = status_of(payload)
    severity = severity_of(status)

    event = {
        "schemaVersion": "1.0",
        "time": _now(),
        "source": "prisma-control-center",
        "bridge": BRIDGE_NAME,
        "eventType": "health_report",
        "runId": payload.get("runId"),
        "status": status,
        "severity": severity,
        "healthScore": payload.get("healthScore"),
        "badServices": bad_services(payload),
        "cloudflareStatus": (payload.get("cloudflare", {}) or {}).get("status"),
        "reportPaths": report_paths,
    }

    _append_jsonl(root / "runtime" / "prisma_black_box_events.jsonl", event)
    _append_jsonl(root / "incidents" / "timeline" / "control_center.timeline.jsonl", event)
    _write_json(root / "runtime" / "control_center_latest.json", payload)

    result = {
        "ok": True,
        "blackBoxRoot": str(root),
        "status": status,
        "severity": severity,
        "activeIncident": None,
        "resolvedIncidents": [],
    }

    if severity == "PASS":
        result["resolvedIncidents"] = resolve_active_incidents(root, payload)
    else:
        result["activeIncident"] = open_or_update_incident(root, payload, report_paths)

    report_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _write_json(
        root / "reports" / f"prisma_control_center_bridge_{report_stamp}.json",
        {"event": event, "result": result},
    )
    _write_json(root / "runtime" / "control_center_bridge_latest.json", result)

    return result


def panel_incidents_payload(public: bool = False, blackbox_root_value: str | Path | None = None) -> dict[str, Any]:
    root = blackbox_root(blackbox_root_value)
    ensure_dirs(root)

    incidents = []
    for incident_dir in active_incident_dirs(root):
        incident = _read_json(incident_dir / "incident.json", {})
        if not incident:
            continue

        if public:
            incident = {
                key: incident.get(key)
                for key in [
                    "id",
                    "source",
                    "state",
                    "severity",
                    "status",
                    "createdAt",
                    "updatedAt",
                    "healthScore",
                    "recommendedNextAction",
                    "badServices",
                    "cloudflareStatus",
                ]
            }

        incidents.append(incident)

    incidents.sort(key=lambda item: str(item.get("updatedAt", "")), reverse=True)

    latest = _read_json(root / "runtime" / "control_center_bridge_latest.json", {})
    if public and isinstance(latest, dict):
        latest.pop("blackBoxRoot", None)
        latest.pop("eventPath", None)

    return {
        "schemaVersion": "1.0",
        "source": BRIDGE_NAME,
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "blackBoxRoot": "<redacted>" if public else str(root),
        "activeCount": len(incidents),
        "activeIncidents": incidents,
        "latestBridge": latest,
    }
