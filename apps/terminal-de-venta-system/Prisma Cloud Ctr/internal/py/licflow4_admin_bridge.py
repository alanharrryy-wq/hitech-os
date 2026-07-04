from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cloud_saas_api

SOURCE = "prisma-cloud-ctr-licflow4-admin-bridge"
SCHEMA_VERSION = "1.0"
INTERNAL_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = INTERNAL_ROOT / "config" / "cloud_saas.json"

BRIDGE_ROUTES = {
    "status": "/api/licflow4/bridge/status",
    "activate": "/api/licflow4/bridge/activate",
    "refresh": "/api/licflow4/bridge/refresh",
    "revoke": "/api/licflow4/bridge/revoke",
}

LICFLOW3_ENDPOINT_KEYS = {
    "activate": "licenseActivate",
    "refresh": "licenseRefresh",
    "revoke": "licenseRevoke",
}

AUDIT_EVENTS: list[dict[str, Any]] = []


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _load_config() -> dict[str, Any]:
    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _config_value(path: list[str], fallback: Any) -> Any:
    value: Any = _load_config()
    for part in path:
        if not isinstance(value, dict):
            return fallback
        value = value.get(part)
    return value if value not in (None, "") else fallback


def _cloud_base() -> str:
    return str(_config_value(["apiBaseUrl"], "https://app.hitechrts.com")).rstrip("/")


def _tenant_slug() -> str:
    return str(_config_value(["tenantSlug"], "prisma-original-customer"))


def _endpoint(action: str) -> str:
    key = LICFLOW3_ENDPOINT_KEYS[action]
    return str(_config_value(["endpoints", key], ""))


def _parts(path: list[str], fallback: list[str]) -> str:
    value = _config_value(path, fallback)
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return str(value)


def _admin_token_candidate() -> Path | None:
    root = Path(str(_config_value(["adminTokenSearch", "root"], "F:/descargasf")))
    folder_glob = str(_config_value(["adminTokenSearch", "folderGlob"], "prcloud*"))
    secret_dir = _parts(["adminTokenSearch", "secretFolderNameParts"], ["SECRET", "_LOCAL", "_ONLY"])
    token_file = _parts(["adminTokenSearch", "tokenFileNameParts"], ["ADMIN", "_TOKEN.txt"])
    candidates: list[Path] = []
    try:
        if root.exists():
            for folder in root.glob(folder_glob):
                candidate = folder / secret_dir / token_file
                if candidate.exists() and candidate.is_file():
                    candidates.append(candidate)
    except Exception:
        return None
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _admin_token_present() -> bool:
    return bool(_admin_token_candidate())


def _read_admin_token_for_bridge() -> str | None:
    candidate = _admin_token_candidate()
    if not candidate:
        return None
    try:
        token = candidate.read_text(encoding="utf-8").strip()
        return token or None
    except Exception:
        return None


def _fingerprint(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            low = str(key).lower()
            if any(token in low for token in ["token", "secret", "authorization", "cookie", "password"]):
                out[key] = "<redacted>"
            elif low in {"licensekey", "license_key"}:
                out[key] = {"fingerprint": _fingerprint(item)}
            else:
                out[key] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _safe_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return {"textSample": text[:900]}


def _request_id(action: str, payload: dict[str, Any]) -> str:
    base = json.dumps({
        "action": action,
        "license": _fingerprint(payload.get("licenseKey")),
        "device": _fingerprint(payload.get("deviceId")),
        "tenant": payload.get("tenantId") or payload.get("tenantSlug"),
        "time": _now(),
    }, sort_keys=True)
    return f"lf4-{hashlib.sha256(base.encode('utf-8')).hexdigest()[:18]}"


def _audit(action: str, payload: dict[str, Any], result: dict[str, Any]) -> None:
    event = {
        "timestamp": _now(),
        "source": SOURCE,
        "action": action,
        "dryRun": bool(payload.get("dryRun")),
        "tenantId": payload.get("tenantId") or payload.get("tenantSlug") or _tenant_slug(),
        "deviceIdFingerprint": _fingerprint(payload.get("deviceId")),
        "licenseKeyFingerprint": _fingerprint(payload.get("licenseKey")),
        "operatorNote": str(payload.get("operatorNote") or "")[:500] or None,
        "reason": str(payload.get("reason") or "")[:500] or None,
        "resultCode": result.get("code"),
        "upstreamStatus": result.get("status"),
        "requestId": result.get("requestId"),
        "secretsExposed": False,
    }
    AUDIT_EVENTS.append(event)
    del AUDIT_EVENTS[:-50]


def audit_summary() -> dict[str, Any]:
    return {
        "count": len(AUDIT_EVENTS),
        "latest": AUDIT_EVENTS[-10:],
        "secretsExposed": False,
    }


def bridge_status() -> dict[str, Any]:
    config = _load_config()
    licflow3 = config.get("licflow3") if isinstance(config.get("licflow3"), dict) else {}
    endpoints = config.get("endpoints") if isinstance(config.get("endpoints"), dict) else {}
    return {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "bridgeAvailable": True,
        "adminTokenPresent": _admin_token_present(),
        "cloudBase": _cloud_base(),
        "worker": licflow3.get("worker") or "prisma-cloud-semilla",
        "d1": licflow3.get("d1") or "prisma_cloud_semilla",
        "routes": {
            "activate": endpoints.get("licenseActivate") or "/api/licenses/activate",
            "refresh": endpoints.get("licenseRefresh") or "/api/licenses/refresh",
            "revoke": endpoints.get("licenseRevoke") or "/api/licenses/revoke",
        },
        "bridgeRoutes": BRIDGE_ROUTES,
        "mutatingActionsRequireConfirmation": True,
        "revokeRequiresPhrase": "REVOKE_LICENSE",
        "secretsExposed": False,
        "audit": audit_summary(),
    }


def _validation_error(code: str, detail: str, http_status: int = 409) -> dict[str, Any]:
    return {
        "ok": False,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "code": code,
        "detail": detail,
        "adminTokenPresent": _admin_token_present(),
        "secretsExposed": False,
        "_httpStatus": http_status,
    }


def _validate_payload(action: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    if payload.get("confirmAdminLicenseAction") is not True:
        return _validation_error("ADMIN_ACTION_CONFIRMATION_REQUIRED", "confirmAdminLicenseAction must be true.")
    if action == "revoke" and payload.get("confirmRevoke") != "REVOKE_LICENSE":
        return _validation_error("REVOKE_CONFIRMATION_REQUIRED", "confirmRevoke must equal REVOKE_LICENSE.")
    required = ["licenseKey", "deviceId", "tenantId"]
    if action == "revoke":
        required.append("reason")
    missing = [key for key in required if not str(payload.get(key) or "").strip()]
    if missing:
        return _validation_error("INVALID_ADMIN_ACTION_PAYLOAD", f"Missing required field(s): {', '.join(missing)}.")
    return None


def _outbound_payload(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = {
        "licenseKey": str(payload.get("licenseKey") or "").strip(),
        "deviceId": str(payload.get("deviceId") or "").strip(),
        "tenantId": str(payload.get("tenantId") or "").strip(),
        "tenantSlug": str(payload.get("tenantId") or "").strip() or _tenant_slug(),
        "source": SOURCE,
        "operatorNote": str(payload.get("operatorNote") or "")[:1000],
    }
    if action == "revoke":
        body["reason"] = str(payload.get("reason") or "")[:1000]
    return body


def perform_action(action: str, payload: dict[str, Any]) -> dict[str, Any]:
    if action not in LICFLOW3_ENDPOINT_KEYS:
        return _validation_error("UNKNOWN_BRIDGE_ACTION", action, http_status=404)
    payload = payload if isinstance(payload, dict) else {}
    validation = _validate_payload(action, payload)
    if validation:
        _audit(action, payload, validation)
        return validation
    request_id = _request_id(action, payload)
    if payload.get("dryRun") is True:
        result = {
            "ok": True,
            "schemaVersion": SCHEMA_VERSION,
            "source": SOURCE,
            "code": "DRY_RUN_READY",
            "action": action,
            "dryRun": True,
            "actionAllowed": False,
            "adminTokenPresent": _admin_token_present(),
            "requestId": request_id,
            "sanitizedPayload": _redact(_outbound_payload(action, payload)),
            "secretsExposed": False,
        }
        _audit(action, payload, result)
        return result
    token = _read_admin_token_for_bridge()
    if not token:
        result = _validation_error("ADMIN_TOKEN_NOT_CONFIGURED", "Admin token is not configured for server-side bridge use.")
        result["requestId"] = request_id
        _audit(action, payload, result)
        return result
    endpoint = _endpoint(action)
    if not endpoint:
        result = _validation_error("LICFLOW3_ENDPOINT_NOT_CONFIGURED", action)
        result["requestId"] = request_id
        _audit(action, payload, result)
        return result
    url = _cloud_base() + endpoint
    body = json.dumps(_outbound_payload(action, payload), ensure_ascii=True).encode("utf-8")
    started = time.perf_counter()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "PRISMA-Cloud-Ctr-LICFLOW4/1.0",
        "X-Prisma-Admin-Token": token,
    }
    try:
        req = urllib.request.Request(url, data=body, method="POST", headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read(1_000_000).decode("utf-8", errors="replace")
            result = {
                "ok": 200 <= resp.status < 300,
                "schemaVersion": SCHEMA_VERSION,
                "source": SOURCE,
                "code": "UPSTREAM_OK" if 200 <= resp.status < 300 else "UPSTREAM_REJECTED",
                "action": action,
                "dryRun": False,
                "status": resp.status,
                "latencyMs": int((time.perf_counter() - started) * 1000),
                "requestId": request_id,
                "data": _redact(_safe_json(text)),
                "secretsExposed": False,
            }
    except urllib.error.HTTPError as exc:
        text = exc.read(200_000).decode("utf-8", errors="replace")
        result = {
            "ok": False,
            "schemaVersion": SCHEMA_VERSION,
            "source": SOURCE,
            "code": "UPSTREAM_ADMIN_TOKEN_REQUIRED" if exc.code == 401 else "UPSTREAM_REJECTED",
            "action": action,
            "dryRun": False,
            "status": exc.code,
            "latencyMs": int((time.perf_counter() - started) * 1000),
            "requestId": request_id,
            "data": _redact(_safe_json(text)) if text else None,
            "secretsExposed": False,
            "_httpStatus": 502 if exc.code >= 500 else 409,
        }
    except Exception as exc:
        result = {
            "ok": False,
            "schemaVersion": SCHEMA_VERSION,
            "source": SOURCE,
            "code": "UPSTREAM_CALL_FAILED",
            "action": action,
            "dryRun": False,
            "status": None,
            "latencyMs": int((time.perf_counter() - started) * 1000),
            "requestId": request_id,
            "error": str(exc)[:500],
            "secretsExposed": False,
            "_httpStatus": 502,
        }
    finally:
        token = ""
    _audit(action, payload, result)
    return result


def bridge_payload(path_text: str, method: str = "GET", body: dict[str, Any] | None = None, local_request: bool = False) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(path_text)
    path = parsed.path.rstrip("/") or BRIDGE_ROUTES["status"]
    method = method.upper()
    if path == BRIDGE_ROUTES["status"] and method == "GET":
        return bridge_status()
    action = next((key for key, route in BRIDGE_ROUTES.items() if key != "status" and route == path), None)
    if not action:
        return _validation_error("UNKNOWN_BRIDGE_ROUTE", path, http_status=404)
    if method != "POST":
        return _validation_error("METHOD_NOT_ALLOWED", f"{path} requires POST.", http_status=405)
    if not local_request:
        return _validation_error("LOCAL_OPERATOR_REQUIRED", "LICFLOW4 Admin Bridge is local operator only.", http_status=403)
    return perform_action(action, body or {})


def diagnostics_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "status": bridge_status(),
        "routes": BRIDGE_ROUTES,
        "auditSummary": audit_summary(),
        "secretsExposed": False,
    }
