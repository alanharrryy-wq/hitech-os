from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE = "prisma-cloud-private-cockpit"
SCHEMA_VERSION = "1.0"
INTERNAL_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = INTERNAL_ROOT / "config" / "cloud_saas.json"
DEFAULT_BASE_URL = "https://app.hitechrts.com"
DEFAULT_TENANT = "prisma-original-customer"
_QUICK_CACHE: dict[str, Any] = {"expires": 0.0, "payload": None}
LICFLOW3_CONTRACT_ID = "LICFLOW3_CLOUDFLARE_HOSTED_LICENSING_SUPPORT_BRIDGE"
LICFLOW3_ENDPOINTS: dict[str, dict[str, Any]] = {
    "health": {"method": "GET", "path": "/health", "capability": "health", "mutatesCloud": False, "adminRequired": False, "safeSummaryCall": True, "classification": "REUSE"},
    "capabilities": {"method": "GET", "path": "/api/public/capabilities", "capability": "capabilities", "mutatesCloud": False, "adminRequired": False, "safeSummaryCall": True, "classification": "REUSE"},
    "tenantStatus": {"method": "GET", "path": "/api/public/tenants/prisma-original-customer/status", "capability": "tenant_status", "mutatesCloud": False, "adminRequired": False, "safeSummaryCall": True, "classification": "REUSE"},
    "clientContract": {"method": "GET", "path": "/api/client/contract?tenant=prisma-original-customer", "capability": "contract_fetch", "mutatesCloud": False, "adminRequired": False, "safeSummaryCall": True, "classification": "REUSE"},
    "licenseActivate": {"method": "POST", "path": "/api/licenses/activate", "capability": "activate", "mutatesCloud": True, "adminRequired": True, "safeSummaryCall": False, "classification": "CREATE"},
    "licenseRefresh": {"method": "POST", "path": "/api/licenses/refresh", "capability": "refresh", "mutatesCloud": True, "adminRequired": True, "safeSummaryCall": False, "classification": "CREATE"},
    "licenseRevoke": {"method": "POST", "path": "/api/licenses/revoke", "capability": "revoke", "mutatesCloud": True, "adminRequired": True, "safeSummaryCall": False, "classification": "CREATE"},
    "deviceRegister": {"method": "POST", "path": "/api/devices/register", "capability": "register_device", "mutatesCloud": True, "adminRequired": True, "safeSummaryCall": False, "classification": "EXTEND"},
    "integrationReceipt": {"method": "POST", "path": "/api/client/integration-receipt", "capability": "integration_receipt", "mutatesCloud": True, "adminRequired": True, "safeSummaryCall": False, "classification": "EXTEND"},
    "supportDiagnostics": {"method": "GET", "path": "/api/support/diagnostics?tenant=prisma-original-customer", "capability": "support_diagnostics", "mutatesCloud": False, "adminRequired": True, "safeSummaryCall": True, "classification": "CREATE"},
    "adminSelftest": {"method": "GET", "path": "/api/admin/selftest", "capability": "admin_selftest", "mutatesCloud": False, "adminRequired": True, "safeSummaryCall": True, "classification": "REUSE"},
    "commercialSummary": {"method": "GET", "path": "/api/admin/commercial-summary", "capability": "commercial_summary", "mutatesCloud": False, "adminRequired": True, "safeSummaryCall": True, "classification": "REUSE"},
    "tenantSnapshot": {"method": "GET", "path": "/api/admin/tenants/prisma-original-customer/snapshot", "capability": "tenant_snapshot", "mutatesCloud": False, "adminRequired": True, "safeSummaryCall": True, "classification": "REUSE"},
    "tenantNotes": {"method": "POST", "path": "/api/admin/tenants/prisma-original-customer/notes", "capability": "tenant_notes", "mutatesCloud": True, "adminRequired": True, "safeSummaryCall": False, "classification": "REUSE"},
}


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


def _endpoint(name: str) -> str:
    return str(_config_value(["endpoints", name], ""))


def _base_url() -> str:
    return str(_config_value(["apiBaseUrl"], DEFAULT_BASE_URL)).rstrip("/")


def _tenant_slug() -> str:
    return str(_config_value(["tenantSlug"], DEFAULT_TENANT))


def _secret_dir_name() -> str:
    parts = _config_value(["adminTokenSearch", "secretFolderNameParts"], ["SECRET", "_LOCAL_ONLY"])
    return "".join(str(part) for part in parts)


def _token_file_name() -> str:
    parts = _config_value(["adminTokenSearch", "tokenFileNameParts"], ["ADMIN", "_TOKEN.txt"])
    return "".join(str(part) for part in parts)


def _downloads_root() -> Path:
    return Path(str(_config_value(["adminTokenSearch", "root"], "F:/descargasf")))


def _folder_glob() -> str:
    return str(_config_value(["adminTokenSearch", "folderGlob"], "prcloud*"))


def _redact_text(value: str) -> str:
    text = value
    text = text.replace(_secret_dir_name(), "<local-secret-dir>")
    text = text.replace(_token_file_name(), "<local-admin-token-file>")
    text = text.replace("\\", "/")
    return text


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            low = str(key).lower()
            if low in {"token", "access_token", "refresh_token", "id_token"} or any(token in low for token in ["authorization", "secret", "cookie", "password"]):
                out[key] = "<redacted>"
            else:
                out[key] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return _redact_text(value)
    return value


def _safe_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return {"textSample": text[:900]}


def _admin_token_record() -> dict[str, Any]:
    root = _downloads_root()
    candidates: list[Path] = []
    if root.exists():
        for folder in root.glob(_folder_glob()):
            token_path = folder / _secret_dir_name() / _token_file_name()
            if token_path.exists() and token_path.is_file():
                candidates.append(token_path)
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        return {"available": False, "sourceName": None, "modified": None, "length": 0, "token": None}
    path = candidates[0]
    try:
        token = path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        token = path.read_text(errors="replace").strip()
    except Exception:
        token = ""
    if not token:
        return {"available": False, "sourceName": path.parent.parent.name, "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"), "length": 0, "token": None}
    return {
        "available": True,
        "sourceName": path.parent.parent.name,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        "length": len(token),
        "token": token,
    }


def admin_token_status() -> dict[str, Any]:
    record = _admin_token_record()
    return {key: value for key, value in record.items() if key != "token"}


def _headers(admin: bool, allow_admin: bool) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "PRISMA-Cloud-Private-Cockpit/1.0",
    }
    if admin and allow_admin:
        token = _admin_token_record().get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-Admin-Token"] = str(token)
            headers["X-PRISMA-Admin-Token"] = str(token)
    return headers


def _call(name: str, method: str = "GET", body: dict[str, Any] | None = None, admin: bool = False, allow_admin: bool = False, timeout: int = 18) -> dict[str, Any]:
    endpoint = _endpoint(name)
    if not endpoint:
        return {"ok": False, "name": name, "status": "CONFIG_MISSING", "error": "Endpoint not configured"}
    if admin and not allow_admin:
        return {"ok": False, "name": name, "status": "READ_ONLY", "skipped": True, "reason": "Admin calls are local-host only"}
    if admin and not _admin_token_record().get("token"):
        return {"ok": False, "name": name, "status": "TOKEN_MISSING", "skipped": True, "reason": "Local admin token file not found"}
    url = _base_url() + endpoint
    started = time.perf_counter()
    data = None
    headers = _headers(admin=admin, allow_admin=allow_admin)
    if body is not None:
        data = json.dumps(body, ensure_ascii=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(2_000_000)
            text = raw.decode("utf-8", errors="replace")
            return {
                "ok": 200 <= resp.status < 300,
                "name": name,
                "method": method.upper(),
                "url": endpoint,
                "statusCode": resp.status,
                "latencyMs": int((time.perf_counter() - started) * 1000),
                "contentType": resp.headers.get("Content-Type", ""),
                "data": _redact(_safe_json(text)),
            }
    except urllib.error.HTTPError as exc:
        text = exc.read(200_000).decode("utf-8", errors="replace")
        return {
            "ok": False,
            "name": name,
            "method": method.upper(),
            "url": endpoint,
            "statusCode": exc.code,
            "latencyMs": int((time.perf_counter() - started) * 1000),
            "error": _redact_text(text[:1200] or str(exc)),
            "data": _redact(_safe_json(text)) if text else None,
        }
    except Exception as exc:
        return {
            "ok": False,
            "name": name,
            "method": method.upper(),
            "url": endpoint,
            "statusCode": None,
            "latencyMs": int((time.perf_counter() - started) * 1000),
            "error": _redact_text(str(exc)),
        }


def _first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return value
    return {}


def _list_from_keys(payload: Any, keys: list[str]) -> list[Any]:
    if not isinstance(payload, dict):
        return []
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return value
    for value in payload.values():
        if isinstance(value, dict):
            found = _list_from_keys(value, keys)
            if found:
                return found
    return []


def _derive(summary: dict[str, Any]) -> dict[str, Any]:
    endpoints = summary.get("endpoints", {})
    health = _first_dict(endpoints.get("health", {}).get("data"))
    capabilities = _first_dict(endpoints.get("capabilities", {}).get("data"))
    status = _first_dict(endpoints.get("tenantStatus", {}).get("data"))
    snapshot = _first_dict(endpoints.get("tenantSnapshot", {}).get("data"))
    commercial = _first_dict(endpoints.get("commercialSummary", {}).get("data"))
    contract = _first_dict(endpoints.get("clientContract", {}).get("data"))
    support = _first_dict(endpoints.get("supportDiagnostics", {}).get("data"))
    licflow3 = _first_dict(summary.get("licflow3Contract"))
    caps = capabilities.get("capabilities") if isinstance(capabilities.get("capabilities"), dict) else {}
    license_payload = status.get("license") if isinstance(status.get("license"), dict) else {}
    return {
        "service": health.get("service") or capabilities.get("service") or "PRISMA Cloud Semilla",
        "version": health.get("version") or capabilities.get("version") or "-",
        "dbHealth": health.get("dbHealth") or health.get("db") or health.get("database") or None,
        "counts": health.get("counts") if isinstance(health.get("counts"), dict) else {},
        "capabilities": caps,
        "tenant": status.get("tenant") if isinstance(status.get("tenant"), dict) else {},
        "license": license_payload,
        "activationStatus": license_payload.get("activationStatus") or license_payload.get("status") or "REVIEW",
        "publicContract": status.get("publicContract") if isinstance(status.get("publicContract"), dict) else contract,
        "commercialSummary": commercial,
        "supportDiagnostics": support,
        "devices": _list_from_keys(snapshot, ["devices", "registeredDevices", "recentDevices"]),
        "notes": _list_from_keys(snapshot, ["notes", "tenantNotes", "recentNotes"]),
        "receipts": _list_from_keys(snapshot, ["receipts", "integrationReceipts", "recentReceipts"]),
        "events": _list_from_keys(snapshot, ["events", "auditEvents", "recentEvents", "audit", "clientEvents"]),
        "snapshot": snapshot,
        "licflow3ContractStatus": licflow3.get("claim") or "contract_incomplete",
        "hostedCloudEvidence": licflow3.get("hostedCloudEvidenceStatus") or "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
    }


def _licflow3_contract_status(endpoints: dict[str, Any] | None = None) -> dict[str, Any]:
    config = _load_config()
    configured_endpoints = config.get("endpoints") if isinstance(config.get("endpoints"), dict) else {}
    missing: list[str] = []
    mismatched: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for key, spec in LICFLOW3_ENDPOINTS.items():
        configured = str(configured_endpoints.get(key) or "")
        if not configured:
            missing.append(key)
        elif configured != spec["path"]:
            mismatched.append({"key": key, "expected": spec["path"], "actual": configured})
        row = dict(spec)
        row.update({"key": key, "configured": bool(configured), "configuredPath": configured or None})
        rows.append(row)
    base_url = _base_url()
    base_url_matches = base_url == DEFAULT_BASE_URL
    endpoint_payloads = endpoints or {}
    live_read_names = ["health", "capabilities", "tenantStatus", "clientContract"]
    live_ok = all(bool(endpoint_payloads.get(name, {}).get("ok")) for name in live_read_names)
    ok = base_url_matches and not missing and not mismatched
    return {
        "ok": ok,
        "schemaVersion": "1.0.0",
        "contractId": LICFLOW3_CONTRACT_ID,
        "baseUrl": DEFAULT_BASE_URL,
        "tenantSlug": _tenant_slug(),
        "configuredBaseUrl": base_url,
        "baseUrlMatches": base_url_matches,
        "missing": missing,
        "mismatched": mismatched,
        "endpoints": rows,
        "hostedCloudEvidenceStatus": "LIVE_EVIDENCE_PRESENT" if live_ok else "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
        "claim": "contract_ready" if ok else "contract_incomplete",
        "safety": {
            "cockpit": "127.0.0.1:3160",
            "noDeployByDefault": True,
            "noDnsMutationByDefault": True,
            "noTunnelMutationByDefault": True,
            "noSecretValuesInRepo": True,
            "noDbFilesInEvidence": True,
            "noMutatingEndpointAutocall": True,
            "tabletOfflineMustRemainValid": True,
            "licflow2RemainsCanonicalLocalActivation": True,
        },
    }


def summary_payload(allow_admin: bool = False) -> dict[str, Any]:
    token = admin_token_status() if allow_admin else {"available": False, "sourceName": None, "modified": None, "length": 0}
    admin_enabled = bool(allow_admin and token.get("available"))
    endpoints = {
        "health": _call("health"),
        "capabilities": _call("capabilities"),
        "tenantStatus": _call("tenantStatus"),
        "clientContract": _call("clientContract"),
        "adminSelftest": _call("adminSelftest", admin=True, allow_admin=admin_enabled),
        "commercialSummary": _call("commercialSummary", admin=True, allow_admin=admin_enabled),
        "tenantSnapshot": _call("tenantSnapshot", admin=True, allow_admin=admin_enabled),
        "supportDiagnostics": _call("supportDiagnostics", admin=True, allow_admin=admin_enabled),
    }
    payload = {
        "ok": any(item.get("ok") for item in endpoints.values()),
        "schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
        "generatedAt": _now(),
        "mode": "LOCAL_FULL" if admin_enabled else ("READ_ONLY_TOKEN_MISSING" if allow_admin else "READ_ONLY_PUBLIC_HOST"),
        "cloud": {"baseUrl": _base_url(), "tenantSlug": _tenant_slug()},
        "admin": {
            "localHostAllowed": bool(allow_admin),
            "tokenAvailable": bool(token.get("available")),
            "tokenSourceName": token.get("sourceName"),
            "tokenModified": token.get("modified"),
            "tokenLength": token.get("length"),
            "enabled": admin_enabled,
        },
        "endpoints": endpoints,
        "actions": [
            {"id": "create-note", "label": "Crear nota", "enabled": admin_enabled},
            {"id": "receipt-smoke", "label": "Receipt smoke", "enabled": admin_enabled},
            {"id": "device-register-smoke", "label": "Device smoke", "enabled": admin_enabled},
        ],
    }
    payload["licflow3Contract"] = _licflow3_contract_status(endpoints)
    payload["derived"] = _derive(payload)
    return _redact(payload)


def quick_status() -> dict[str, Any]:
    now = time.time()
    cached = _QUICK_CACHE.get("payload")
    if cached and float(_QUICK_CACHE.get("expires") or 0) > now:
        return dict(cached)
    health = _call("health", timeout=8)
    caps = _call("capabilities", timeout=8)
    ok = bool(health.get("ok") and caps.get("ok"))
    payload = {
        "ok": ok,
        "status": "CLOUD_LIVE" if ok else ("CLOUD_PARTIAL" if health.get("ok") or caps.get("ok") else "CLOUD_OFFLINE"),
        "healthStatusCode": health.get("statusCode"),
        "capabilitiesStatusCode": caps.get("statusCode"),
        "latencyMs": max(int(health.get("latencyMs") or 0), int(caps.get("latencyMs") or 0)),
        "service": _first_dict(health.get("data")).get("service") or "PRISMA Cloud Semilla",
        "version": _first_dict(health.get("data")).get("version") or _first_dict(caps.get("data")).get("version"),
    }
    _QUICK_CACHE["payload"] = payload
    _QUICK_CACHE["expires"] = now + 20
    return dict(payload)


def _note_payload(body: dict[str, Any] | None) -> dict[str, Any]:
    text = str((body or {}).get("text") or "").strip()
    if not text:
        text = f"Nota operatoria desde PRISMA Cloud Private Cockpit {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return {
        "tenantSlug": _tenant_slug(),
        "text": text[:2000],
        "source": "prisma-control-center-lab-3160",
        "operator": "local-private-cockpit",
        "createdAt": _now(),
    }


def _receipt_payload() -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return {
        "tenantSlug": _tenant_slug(),
        "receiptId": f"lab-3160-smoke-{stamp}",
        "source": "prisma-control-center-lab-3160",
        "kind": "integration-smoke",
        "ok": True,
        "createdAt": _now(),
        "payload": {
            "nonCustomerSmoke": True,
            "surface": "PRISMA Cloud Private Cockpit",
            "scope": "integration-receipt",
        },
    }


def _device_payload() -> dict[str, Any]:
    return {
        "tenantSlug": _tenant_slug(),
        "deviceId": "lab-3160-private-cockpit",
        "deviceName": "PRISMA Cloud Private Cockpit",
        "role": "operator-lab",
        "platform": "windows-local",
        "version": "cclabcloud1",
        "metadata": {
            "nonCustomerSmoke": True,
            "source": "prisma-control-center-unified-shell-lab-v3",
            "createdAt": _now(),
        },
    }


def cloud_saas_payload(path_text: str, method: str = "GET", body: dict[str, Any] | None = None, allow_admin: bool = False) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(path_text)
    path = parsed.path.rstrip("/") or "/api/cloud-saas/summary"
    if path in {"/api/cloud-saas", "/api/cloud-saas/summary", "/api/cloud-saas/refresh"}:
        return summary_payload(allow_admin=allow_admin)
    if path == "/api/cloud-saas/config":
        return _redact({"ok": True, "schemaVersion": SCHEMA_VERSION, "source": SOURCE, "config": _load_config(), "admin": admin_token_status()})
    if path == "/api/cloud-saas/licflow3-contract":
        return _redact({"ok": True, "schemaVersion": SCHEMA_VERSION, "source": SOURCE, "licflow3Contract": _licflow3_contract_status()})
    admin_enabled = bool(allow_admin and _admin_token_record().get("token"))
    if path == "/api/cloud-saas/notes":
        return _call("tenantNotes", method="POST", body=_note_payload(body), admin=True, allow_admin=admin_enabled)
    if path == "/api/cloud-saas/receipt-smoke":
        return _call("integrationReceipt", method="POST", body=_receipt_payload(), admin=True, allow_admin=admin_enabled)
    if path == "/api/cloud-saas/device-register-smoke":
        return _call("deviceRegister", method="POST", body=_device_payload(), admin=True, allow_admin=admin_enabled)
    return {"ok": False, "source": SOURCE, "status": "UNKNOWN_ENDPOINT", "path": path, "method": method}
