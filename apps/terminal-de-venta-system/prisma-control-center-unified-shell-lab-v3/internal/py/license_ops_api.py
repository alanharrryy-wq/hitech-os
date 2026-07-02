from __future__ import annotations

import json
import os
import sqlite3
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE = "prisma-license-ops-lab-adapter"
SCHEMA_VERSION = "1.0"
LAB_ROOT = Path(__file__).resolve().parents[2]
TERMINAL_ROOT = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _programdata_root() -> Path:
    return Path(os.environ.get("ProgramData") or r"C:\ProgramData")


def _canonical_config_root() -> Path:
    return _programdata_root() / "PRISMA" / "Commerce" / "Config"


def _canonical_runtime_config() -> Path:
    return _canonical_config_root() / "runtime.json"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _path_status(path: Path, public: bool = False) -> dict[str, Any]:
    try:
        exists = path.exists()
        stat = path.stat() if exists else None
        return {
            "path": "<redacted>" if public else str(path),
            "name": path.name,
            "exists": exists,
            "isFile": path.is_file() if exists else False,
            "isDir": path.is_dir() if exists else False,
            "size": stat.st_size if stat and path.is_file() else None,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds") if stat else None,
        }
    except Exception as exc:
        return {"path": "<redacted>" if public else str(path), "exists": False, "error": str(exc)}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            low = str(key).lower()
            if any(token in low for token in ["token", "secret", "signature", "password", "cookie"]):
                out[key] = "<redacted>"
            elif any(token in low for token in ["path", "root", "command", "stdout", "stderr", "log"]):
                out[key] = "<redacted>"
            else:
                out[key] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and (":\\" in value or ":/" in value):
        return "<redacted>"
    return value


def _read_runtime_bundle(public: bool = False) -> dict[str, Any]:
    env_runtime = os.environ.get("PRISMA_RUNTIME_CONFIG")
    runtime_path = Path(env_runtime) if env_runtime else _canonical_runtime_config()
    runtime = _read_json(runtime_path)
    paths = runtime.get("paths", {}) if isinstance(runtime, dict) else {}
    config_root = Path(str(runtime.get("configRoot") or runtime_path.parent)) if isinstance(runtime, dict) else runtime_path.parent
    license_file = Path(str(paths.get("licenseFile") or (runtime.get("license") or {}).get("file") or config_root / "license.json")) if isinstance(runtime, dict) else config_root / "license.json"
    identity_file = Path(str(paths.get("deviceIdentityFile") or runtime.get("deviceIdentityFile") or config_root / "device-identity.json")) if isinstance(runtime, dict) else config_root / "device-identity.json"
    current_release = config_root / "current-release.json"
    identity = _read_json(identity_file)
    license_doc = _read_json(license_file)
    envelope = license_doc if isinstance(license_doc, dict) and isinstance(license_doc.get("payload"), dict) else None
    license_payload = envelope.get("payload") if envelope else license_doc
    assignment = license_payload.get("assignment") if isinstance(license_payload, dict) else None
    if not isinstance(assignment, dict):
        assignment = {}
    license_summary = None
    if isinstance(license_payload, dict):
        authorized_devices = license_payload.get("authorizedDevices")
        if not isinstance(authorized_devices, list):
            authorized_devices = []
        license_summary = {
            "licenseId": license_payload.get("licenseId") or license_payload.get("id"),
            "plan": license_payload.get("plan"),
            "status": license_payload.get("status") or license_payload.get("state"),
            "validUntil": license_payload.get("validUntil") or license_payload.get("expiresAt"),
            "assignment": {
                "clientId": assignment.get("clientId") or license_payload.get("clientId"),
                "businessId": assignment.get("businessId") or license_payload.get("businessId"),
                "storeId": assignment.get("storeId") or assignment.get("branchId") or license_payload.get("storeId"),
                "terminalId": assignment.get("terminalId") or license_payload.get("terminalId"),
                "deviceId": assignment.get("deviceId") or assignment.get("tabletId") or license_payload.get("deviceId"),
            },
            "authorizedDeviceCount": len(authorized_devices),
            "authorizedDevices": [
                {
                    "role": item.get("role"),
                    "deviceId": item.get("deviceId"),
                    "storeId": item.get("storeId"),
                    "terminalId": item.get("terminalId"),
                }
                for item in authorized_devices
                if isinstance(item, dict)
            ],
            "signedEnvelope": bool(envelope),
            "keyId": envelope.get("keyId") if envelope else None,
            "alg": envelope.get("alg") if envelope else None,
            "signaturePresent": bool((envelope or license_doc).get("signature") if isinstance((envelope or license_doc), dict) else False),
        }
    bundle = {
        "runtimeConfig": _path_status(runtime_path, public),
        "programDataConfigRoot": _path_status(_canonical_config_root(), public),
        "configRoot": _path_status(config_root, public),
        "licenseFile": _path_status(license_file, public),
        "deviceIdentityFile": _path_status(identity_file, public),
        "currentRelease": _path_status(current_release, public),
        "runtime": {
            "runtimeMode": runtime.get("runtimeMode") if isinstance(runtime, dict) else None,
            "runtimeProfile": runtime.get("runtimeProfile") if isinstance(runtime, dict) else None,
            "vertical": runtime.get("vertical") if isinstance(runtime, dict) else None,
            "role": runtime.get("role") if isinstance(runtime, dict) else None,
            "clientId": runtime.get("clientId") if isinstance(runtime, dict) else None,
            "businessId": runtime.get("businessId") if isinstance(runtime, dict) else None,
            "storeId": runtime.get("storeId") if isinstance(runtime, dict) else None,
            "terminalId": runtime.get("terminalId") if isinstance(runtime, dict) else None,
            "deviceId": runtime.get("deviceId") if isinstance(runtime, dict) else None,
        },
        "identity": identity,
        "license": license_summary,
        "provenance": {
            "runtimeConfig": "PRISMA_RUNTIME_CONFIG" if env_runtime else "ProgramData canonical",
            "adapter": "Copied/adapted from Control Center 3150 license ops; actions are read-only in lab 3160.",
            "sourceControlCenter": "read-only",
        },
    }
    return _redact(bundle) if public else bundle


def _status_from_latest(payload: dict[str, Any]) -> str:
    runtime = payload.get("runtime", {})
    summary = runtime.get("runtime") if isinstance(runtime, dict) else {}
    mode = summary.get("runtimeMode") if isinstance(summary, dict) else None
    identity_loaded = bool(runtime.get("deviceIdentityFile", {}).get("exists")) if isinstance(runtime, dict) else False
    license_loaded = bool(runtime.get("licenseFile", {}).get("exists")) if isinstance(runtime, dict) else False
    runtime_loaded = bool(runtime.get("runtimeConfig", {}).get("exists")) if isinstance(runtime, dict) else False
    if (mode == "customer" or mode == "release") and identity_loaded and not license_loaded:
        return "LICENSE_CUSTOMER_PENDING"
    if runtime_loaded and identity_loaded and license_loaded:
        return "RUNTIME_READY"
    if runtime_loaded and mode == "dev" and not license_loaded:
        return "DEV_LICENSE_MISSING"
    if not runtime_loaded:
        return "RUNTIME_PENDING"
    return "REVIEW"


def _actions_payload(public: bool = False) -> dict[str, Any]:
    actions = [
        {"id": "detect-runtime", "label": "Detectar runtime", "enabled": True, "localOnly": True, "danger": False},
        {"id": "explorer", "label": "Monitor read-only", "enabled": True, "localOnly": True, "danger": False},
        {"id": "3150-actions", "label": "Acciones 3150 protegidas", "enabled": False, "localOnly": True, "danger": False, "reason": "El lab 3160 no levanta procesos ni ejecuta provisioning."},
    ]
    payload = {"ok": True, "schemaVersion": SCHEMA_VERSION, "source": SOURCE, "time": _now(), "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_READ_ONLY", "actions": actions}
    return _redact(payload) if public else payload


def _tablet_db_path() -> Path:
    explicit = os.environ.get("TABLET_DATABASE_PATH")
    if explicit:
        return Path(explicit)
    return TERMINAL_ROOT / "products" / "tablet" / "app" / "data" / "tablet-pos.db"


def _sqlite_rows(db_path: Path, query: str) -> dict[str, Any]:
    if not db_path.exists():
        return {"available": False, "path": str(db_path), "reason": "tablet database not found", "matches": [], "latestTickets": [], "outbox": []}
    needle = f"%{query}%"
    out: dict[str, Any] = {"available": True, "path": str(db_path), "matches": [], "latestTickets": [], "outbox": []}
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        tables = {row["name"] for row in conn.execute("select name from sqlite_master where type='table'")}
        if "Sale" in tables:
            rows = conn.execute(
                "select id, folio, businessId, terminalId, clientRequestId, status, createdAt, completedAt, totalCents from Sale where id like ? or folio like ? or clientRequestId like ? order by createdAt desc limit 8",
                (needle, needle, needle),
            ).fetchall()
            out["matches"] = [dict(row) for row in rows]
            latest = conn.execute("select id, folio, businessId, terminalId, clientRequestId, status, createdAt, totalCents from Sale order by createdAt desc limit 5").fetchall()
            out["latestTickets"] = [dict(row) for row in latest]
        if "OutboxEvent" in tables:
            rows = conn.execute(
                "select id, topic, aggregateId, businessId, terminalId, status, createdAt, lastError from OutboxEvent where id like ? or aggregateId like ? or topic like ? or idempotencyKey like ? order by createdAt desc limit 8",
                (needle, needle, needle, needle),
            ).fetchall()
            out["outbox"] = [dict(row) for row in rows]
    finally:
        conn.close()
    return out


def _scan_json_for_query(label: str, path: Path, query: str) -> dict[str, Any]:
    payload = _read_json(path)
    if payload is None:
        return {"source": label, "path": str(path), "exists": path.exists(), "matches": []}
    lowered = query.lower()
    matches: list[dict[str, Any]] = []

    def walk(value: Any, key_path: str) -> None:
        if len(matches) >= 20:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                walk(item, f"{key_path}.{key}" if key_path else str(key))
        elif isinstance(value, list):
            for index, item in enumerate(value[:40]):
                walk(item, f"{key_path}[{index}]")
        elif lowered in str(value).lower() or lowered in key_path.lower():
            matches.append({"field": key_path, "value": str(value)[:240]})

    walk(payload, "")
    return {"source": label, "path": str(path), "exists": True, "matches": matches}


def _explorer_payload(query: str, public: bool = False) -> dict[str, Any]:
    query = query.strip()
    runtime_bundle = _read_runtime_bundle(public=False)
    config_root = Path(str(runtime_bundle.get("configRoot", {}).get("path") or _canonical_config_root()))
    sources = []
    if query:
        sources.extend([
            _scan_json_for_query("runtime", Path(str(runtime_bundle.get("runtimeConfig", {}).get("path") or _canonical_runtime_config())), query),
            _scan_json_for_query("device_identity", Path(str(runtime_bundle.get("deviceIdentityFile", {}).get("path") or config_root / "device-identity.json")), query),
            _scan_json_for_query("license_summary", Path(str(runtime_bundle.get("licenseFile", {}).get("path") or config_root / "license.json")), query),
        ])
    db = _sqlite_rows(_tablet_db_path(), query) if query else {"available": _tablet_db_path().exists(), "path": str(_tablet_db_path()), "matches": [], "latestTickets": [], "outbox": []}
    payload = {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_READ_ONLY",
        "query": query,
        "runtime": runtime_bundle,
        "readOnly": True,
        "sources": sources,
        "tabletData": db,
    }
    return _redact(payload) if public else payload


def _latest_payload(public: bool = False) -> dict[str, Any]:
    payload = {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_READ_ONLY",
        "runtime": _read_runtime_bundle(public=public),
        "actions": _actions_payload(public=False)["actions"],
        "readOnly": True,
    }
    payload["status"] = _status_from_latest(payload)
    return _redact(payload) if public else payload


def license_ops_payload(path_text: str, public: bool = False) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(path_text)
    path = parsed.path.rstrip("/") or "/api/license-ops/latest"
    query = urllib.parse.parse_qs(parsed.query)
    if path == "/api/license-ops/actions":
        return _actions_payload(public=public)
    if path == "/api/license-ops/latest":
        return _latest_payload(public=public)
    if path == "/api/license-ops/explorer":
        return _explorer_payload((query.get("query") or query.get("q") or [""])[0], public=public)
    if path.startswith("/api/license-ops/run/"):
        action = path.rsplit("/", 1)[-1].strip().lower()
        if action == "detect-runtime":
            return _latest_payload(public=public)
        return {"ok": False, "schemaVersion": SCHEMA_VERSION, "source": SOURCE, "status": "DISABLED_IN_LAB", "action": action, "reason": "Lab 3160 integrates the 3150 license module in read-only mode and does not run process/provisioning actions."}
    return _latest_payload(public=public)
