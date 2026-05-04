#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

VERSION = "0.6.0"
SERVICE = "prisma-license-server-mvp"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3140
DEFAULT_PLAN = "TABLET_PC_REQUIRED"
DEFAULT_CUSTOMER_ID = "cust_demo"
DEFAULT_BUSINESS_ID = "biz_demo"
DEFAULT_DEVICE_ID = "device_demo_tablet_01"
DEFAULT_TERMINAL_ID = "tablet_01"
DEFAULT_ISSUER = "PRISMA_LICENSE_SERVER_MVP_06"
DEFAULT_KEY_ID = "dev-local-06"
DEV_SECRET_FALLBACK = "PRISMA_LICENSE_SERVER_MVP_06_DEV_ONLY_NOT_FOR_PRODUCTION"

PLAN_LIMITS = {
    "TABLET_SOLO": {"terminalLimit": 1, "branchLimit": 1},
    "TABLET_PRO": {"terminalLimit": 2, "branchLimit": 1},
    "TABLET_PC_REQUIRED": {"terminalLimit": 6, "branchLimit": 3},
}

FEATURES_BY_PLAN = {
    "TABLET_SOLO": [
        "pos.open",
        "pos.product.search",
        "pos.sale.create",
        "pos.sale.complete",
        "inventory.local.view",
        "report.today.view",
        "export.local.create",
    ],
    "TABLET_PRO": [
        "pos.open",
        "pos.product.search",
        "pos.sale.create",
        "pos.sale.complete",
        "pos.sale.cancel",
        "pos.return.create",
        "inventory.local.view",
        "inventory.local.adjust",
        "report.today.view",
        "export.local.create",
        "event.outbox.view",
        "shift.open",
        "shift.close",
    ],
    "TABLET_PC_REQUIRED": [
        "pos.open",
        "pos.product.search",
        "pos.sale.create",
        "pos.sale.complete",
        "pos.sale.cancel",
        "pos.return.create",
        "inventory.local.view",
        "inventory.local.adjust",
        "pc.open",
        "pc.dashboard.view",
        "pc.inventory.advanced",
        "pc.audit.view",
        "pc.sync.view",
        "report.today.view",
        "export.local.create",
        "event.outbox.view",
        "shift.open",
        "shift.close",
    ],
}

SENSITIVE_EVENT_TYPES = {
    "license.activated",
    "license.refreshed",
    "license.suspended",
    "license.revoked",
    "license.current_read",
    "license.customer_listed",
    "device.activation_denied",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def add_days(days: int) -> str:
    return (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def default_out_dir() -> Path:
    return Path(r"F:\descargasf") if os.name == "nt" else Path(tempfile.gettempdir())


@dataclass
class ServerConfig:
    root: Path
    data_dir: Path
    host: str
    port: int
    issuer: str
    key_id: str
    signing_secret: str

    @property
    def store_path(self) -> Path:
        return self.data_dir / "license-server-store.json"


def resolve_root(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path.cwd().resolve()


def resolve_config(args: argparse.Namespace) -> ServerConfig:
    root = resolve_root(getattr(args, "root", None))
    host = getattr(args, "host", None) or os.environ.get("PRISMA_LICENSE_SERVER_HOST", DEFAULT_HOST)
    port = int(getattr(args, "port", None) or os.environ.get("PRISMA_LICENSE_SERVER_PORT", DEFAULT_PORT))
    data_dir_arg = getattr(args, "data_dir", None) or os.environ.get("PRISMA_LICENSE_SERVER_DATA_DIR")
    if data_dir_arg:
        data_dir = Path(data_dir_arg)
        if not data_dir.is_absolute():
            data_dir = root / data_dir
    else:
        data_dir = root / "local-runtime" / "license-server"
    issuer = getattr(args, "issuer", None) or os.environ.get("PRISMA_LICENSE_ISSUER", DEFAULT_ISSUER)
    key_id = getattr(args, "key_id", None) or os.environ.get("PRISMA_LICENSE_DEV_KEY_ID", DEFAULT_KEY_ID)
    signing_secret = getattr(args, "signing_secret", None) or os.environ.get("PRISMA_LICENSE_DEV_SIGNING_SECRET", DEV_SECRET_FALLBACK)
    return ServerConfig(
        root=root,
        data_dir=data_dir.resolve(),
        host=host,
        port=port,
        issuer=issuer,
        key_id=key_id,
        signing_secret=signing_secret,
    )


class JsonStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.RLock()

    def load(self) -> dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return fresh_store()
            with self.path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            return normalize_store(data)

    def save(self, data: dict[str, Any]) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(normalize_store(data), fh, ensure_ascii=False, indent=2, sort_keys=True)
                fh.write("\n")
            tmp.replace(self.path)

    def mutate(self, fn):
        with self._lock:
            data = self.load()
            result = fn(data)
            self.save(data)
            return result


def fresh_store() -> dict[str, Any]:
    return {
        "schemaVersion": "06.mvp.1",
        "createdAt": utc_now(),
        "customers": {},
        "businesses": {},
        "devices": {},
        "licenses": {},
        "events": [],
    }


def normalize_store(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        data = fresh_store()
    data.setdefault("schemaVersion", "06.mvp.1")
    data.setdefault("createdAt", utc_now())
    data.setdefault("customers", {})
    data.setdefault("businesses", {})
    data.setdefault("devices", {})
    data.setdefault("licenses", {})
    data.setdefault("events", [])
    return data


def log_event(store: dict[str, Any], event_type: str, payload: dict[str, Any]) -> None:
    event = {
        "eventId": f"evt_{uuid.uuid4().hex}",
        "type": event_type,
        "occurredAt": utc_now(),
        "payload": payload,
        "sensitive": event_type in SENSITIVE_EVENT_TYPES,
    }
    events = store.setdefault("events", [])
    if events and events[-1].get("type") == event_type and events[-1].get("payload") == payload:
        return
    events.append(event)
    if len(events) > 500:
        del events[:-500]


def error_payload(code: str, message: str, details: dict[str, Any] | None = None, status: int = 400) -> tuple[int, dict[str, Any]]:
    return status, {"ok": False, "code": code, "message": message, "details": details or {}}


def ok_payload(data: Any = None, meta: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    return 200, {"ok": True, "data": data if data is not None else {}, "meta": meta or {}}


def require_fields(body: dict[str, Any], fields: list[str]) -> tuple[bool, str | None]:
    for field in fields:
        if not body.get(field):
            return False, field
    return True, None


def make_license_payload(config: ServerConfig, activation: dict[str, Any], state: str = "active") -> dict[str, Any]:
    plan = activation["plan"]
    limits = PLAN_LIMITS[plan]
    issued_at = utc_now()
    license_id = activation.get("licenseId") or f"lic_{uuid.uuid4().hex[:16]}"
    payload = {
        "schemaVersion": "1.0.0",
        "licenseId": license_id,
        "customerId": activation["customerId"],
        "businessId": activation["businessId"],
        "deviceId": activation["deviceId"],
        "terminalId": activation["terminalId"],
        "plan": plan,
        "state": state,
        "validFrom": issued_at,
        "validUntil": add_days(365),
        "issuedAt": issued_at,
        "issuer": config.issuer,
        "offlineGraceDays": 14,
        "limits": limits,
        "features": FEATURES_BY_PLAN[plan],
        "source": "license-server-mvp-06",
        "warnings": ["Firma dev/staging. No usar como firma productiva."],
    }
    payload["signature"] = sign_payload(config, payload)
    return payload


def sign_payload(config: ServerConfig, payload: dict[str, Any]) -> dict[str, str]:
    unsigned = {k: v for k, v in payload.items() if k != "signature"}
    digest = hmac.new(config.signing_secret.encode("utf-8"), canonical_json(unsigned), hashlib.sha256).digest()
    return {
        "algorithm": "HS256_DEV_ONLY",
        "keyId": config.key_id,
        "value": b64url(digest),
    }


def ensure_customer_business(store: dict[str, Any], customer_id: str, business_id: str) -> None:
    customers = store.setdefault("customers", {})
    businesses = store.setdefault("businesses", {})
    customers.setdefault(customer_id, {"customerId": customer_id, "createdAt": utc_now(), "status": "active"})
    businesses.setdefault(business_id, {"businessId": business_id, "customerId": customer_id, "createdAt": utc_now(), "status": "active"})


def active_device_count(store: dict[str, Any], business_id: str, plan: str, exclude_device_id: str | None = None) -> int:
    count = 0
    for device in store.get("devices", {}).values():
        if device.get("businessId") != business_id:
            continue
        if exclude_device_id and device.get("deviceId") == exclude_device_id:
            continue
        if device.get("plan") == plan and device.get("status") == "active":
            count += 1
    return count


def find_license(store: dict[str, Any], license_id: str | None = None, device_id: str | None = None) -> dict[str, Any] | None:
    licenses = store.get("licenses", {})
    if license_id:
        return licenses.get(license_id)
    if device_id:
        for lic in licenses.values():
            if lic.get("deviceId") == device_id:
                return lic
    return None


class LicenseService:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.store = JsonStore(config.store_path)

    def seed(self) -> dict[str, Any]:
        body = {
            "customerId": DEFAULT_CUSTOMER_ID,
            "businessId": DEFAULT_BUSINESS_ID,
            "deviceId": DEFAULT_DEVICE_ID,
            "terminalId": DEFAULT_TERMINAL_ID,
            "plan": DEFAULT_PLAN,
        }
        status, payload = self.activate(body)
        return {"status": status, "payload": payload, "store": str(self.config.store_path)}

    def health(self) -> tuple[int, dict[str, Any]]:
        data = {
            "service": SERVICE,
            "status": "ok",
            "version": VERSION,
            "store": str(self.config.store_path),
            "time": utc_now(),
        }
        return ok_payload(data)

    def activate(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        ok, missing = require_fields(body, ["customerId", "businessId", "deviceId", "terminalId", "plan"])
        if not ok:
            return error_payload("MISSING_FIELD", f"Falta campo requerido: {missing}", {"field": missing})
        plan = str(body["plan"])
        if plan not in PLAN_LIMITS:
            return error_payload("INVALID_PLAN", f"Plan no soportado: {plan}", {"allowed": sorted(PLAN_LIMITS)})

        def mutate(store: dict[str, Any]) -> tuple[int, dict[str, Any]]:
            customer_id = str(body["customerId"])
            business_id = str(body["businessId"])
            device_id = str(body["deviceId"])
            terminal_id = str(body["terminalId"])
            ensure_customer_business(store, customer_id, business_id)
            devices = store.setdefault("devices", {})
            existing = devices.get(device_id)
            if not existing:
                current = active_device_count(store, business_id, plan)
                limit = PLAN_LIMITS[plan]["terminalLimit"]
                if current >= limit:
                    log_event(store, "device.activation_denied", {"businessId": business_id, "deviceId": device_id, "plan": plan, "limit": limit})
                    return error_payload(
                        "TERMINAL_LIMIT_EXCEEDED",
                        "El plan ya alcanzó el límite de terminales activas.",
                        {"businessId": business_id, "plan": plan, "terminalLimit": limit, "activeTerminals": current},
                        status=409,
                    )
            activation = {
                "customerId": customer_id,
                "businessId": business_id,
                "deviceId": device_id,
                "terminalId": terminal_id,
                "plan": plan,
                "activatedAt": existing.get("activatedAt") if existing else utc_now(),
                "status": "active",
            }
            old_license_id = existing.get("licenseId") if existing else None
            if old_license_id and old_license_id in store.get("licenses", {}):
                activation["licenseId"] = old_license_id
            license_payload = make_license_payload(self.config, activation, state="active")
            activation["licenseId"] = license_payload["licenseId"]
            devices[device_id] = activation
            store.setdefault("licenses", {})[license_payload["licenseId"]] = license_payload
            log_event(store, "license.activated", {"licenseId": license_payload["licenseId"], "deviceId": device_id, "plan": plan})
            return ok_payload({"license": license_payload, "activation": activation})

        return self.store.mutate(mutate)

    def refresh(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        license_id = body.get("licenseId")
        device_id = body.get("deviceId")
        if not license_id and not device_id:
            return error_payload("MISSING_LOOKUP", "Se requiere licenseId o deviceId.")

        def mutate(store: dict[str, Any]) -> tuple[int, dict[str, Any]]:
            lic = find_license(store, license_id=str(license_id) if license_id else None, device_id=str(device_id) if device_id else None)
            if not lic:
                return error_payload("LICENSE_NOT_FOUND", "No se encontró licencia para refrescar.", {"licenseId": license_id, "deviceId": device_id}, status=404)
            lic["lastRefreshAt"] = utc_now()
            lic["signature"] = sign_payload(self.config, lic)
            store.setdefault("licenses", {})[lic["licenseId"]] = lic
            log_event(store, "license.refreshed", {"licenseId": lic["licenseId"], "state": lic.get("state")})
            return ok_payload({"license": lic})

        return self.store.mutate(mutate)

    def change_state(self, body: dict[str, Any], state: str) -> tuple[int, dict[str, Any]]:
        license_id = body.get("licenseId")
        device_id = body.get("deviceId")
        reason = body.get("reason") or state
        if not license_id and not device_id:
            return error_payload("MISSING_LOOKUP", "Se requiere licenseId o deviceId.")

        def mutate(store: dict[str, Any]) -> tuple[int, dict[str, Any]]:
            lic = find_license(store, license_id=str(license_id) if license_id else None, device_id=str(device_id) if device_id else None)
            if not lic:
                return error_payload("LICENSE_NOT_FOUND", "No se encontró licencia.", {"licenseId": license_id, "deviceId": device_id}, status=404)
            lic["state"] = state
            lic["statusReason"] = reason
            lic["statusChangedAt"] = utc_now()
            lic["signature"] = sign_payload(self.config, lic)
            store.setdefault("licenses", {})[lic["licenseId"]] = lic
            device = store.setdefault("devices", {}).get(lic.get("deviceId"))
            if device:
                device["status"] = state
            event_type = "license.suspended" if state == "suspended" else "license.revoked"
            log_event(store, event_type, {"licenseId": lic["licenseId"], "reason": reason})
            return ok_payload({"license": lic})

        return self.store.mutate(mutate)

    def current(self, query: dict[str, list[str]]) -> tuple[int, dict[str, Any]]:
        license_id = first(query.get("licenseId"))
        device_id = first(query.get("deviceId"))
        if not license_id and not device_id:
            return error_payload("MISSING_LOOKUP", "Se requiere licenseId o deviceId.")
        store = self.store.load()
        lic = find_license(store, license_id=license_id, device_id=device_id)
        if not lic:
            return error_payload("LICENSE_NOT_FOUND", "No se encontró licencia.", {"licenseId": license_id, "deviceId": device_id}, status=404)
        log_event(store, "license.current_read", {"licenseId": lic["licenseId"]})
        self.store.save(store)
        return ok_payload({"license": lic})

    def customer_licenses(self, customer_id: str) -> tuple[int, dict[str, Any]]:
        store = self.store.load()
        licenses = [lic for lic in store.get("licenses", {}).values() if lic.get("customerId") == customer_id]
        log_event(store, "license.customer_listed", {"customerId": customer_id, "count": len(licenses)})
        self.store.save(store)
        return ok_payload({"customerId": customer_id, "licenses": licenses, "count": len(licenses)})


def first(values: list[str] | None) -> str | None:
    if not values:
        return None
    return values[0]


def make_handler(service: LicenseService):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"{SERVICE}/{VERSION}"

        def log_message(self, fmt: str, *args: Any) -> None:
            if os.environ.get("PRISMA_LICENSE_SERVER_SILENT") == "1":
                return
            super().log_message(fmt, *args)

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            if parsed.path == "/health":
                return self.send_result(*service.health())
            if parsed.path == "/licenses/current":
                return self.send_result(*service.current(query))
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) == 3 and parts[0] == "customers" and parts[2] == "licenses":
                return self.send_result(*service.customer_licenses(parts[1]))
            return self.send_result(*error_payload("NOT_FOUND", f"Ruta no encontrada: {parsed.path}", status=404))

        def do_POST(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            try:
                body = self.read_json()
            except ValueError as exc:
                return self.send_result(*error_payload("INVALID_JSON", str(exc)))
            if parsed.path == "/licenses/activate":
                return self.send_result(*service.activate(body))
            if parsed.path == "/licenses/refresh":
                return self.send_result(*service.refresh(body))
            if parsed.path == "/licenses/suspend":
                return self.send_result(*service.change_state(body, "suspended"))
            if parsed.path == "/licenses/revoke":
                return self.send_result(*service.change_state(body, "revoked"))
            return self.send_result(*error_payload("NOT_FOUND", f"Ruta no encontrada: {parsed.path}", status=404))

        def read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or "0")
            raw = self.rfile.read(length) if length else b"{}"
            if not raw:
                return {}
            try:
                data = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON inválido: {exc}") from exc
            if not isinstance(data, dict):
                raise ValueError("El body debe ser un objeto JSON.")
            return data

        def send_result(self, status: int, payload: dict[str, Any]) -> None:
            raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

    return Handler


def run_server(config: ServerConfig) -> None:
    config.data_dir.mkdir(parents=True, exist_ok=True)
    service = LicenseService(config)
    service.store.save(service.store.load())
    handler = make_handler(service)
    httpd = ThreadingHTTPServer((config.host, config.port), handler)
    actual_host, actual_port = httpd.server_address
    print(f"PRISMA License Server MVP 06")
    print(f"URL http://{actual_host}:{actual_port}")
    print(f"Store {config.store_path}")
    print("CTRL+C para detener")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Detenido")
    finally:
        httpd.server_close()


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 10) -> tuple[int, dict[str, Any]]:
    raw = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        raw = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=raw, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"ok": False, "code": "HTTP_ERROR", "message": body}
        return exc.code, parsed


def smoke(args: argparse.Namespace) -> int:
    out_dir = Path(getattr(args, "out_dir", None) or default_out_dir()).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / f"terminal_venta_license_server_mvp_06_smoke_{dt.datetime.now().strftime('%y%m%d_%H%M')}.md"
    external_url = getattr(args, "base_url", None)
    server = None
    thread = None
    temp_root = None
    if external_url:
        base_url = external_url.rstrip("/")
    else:
        temp_root = Path(tempfile.mkdtemp(prefix="prisma_license_server_06_"))
        config = resolve_config(args)
        config = ServerConfig(
            root=temp_root,
            data_dir=temp_root / "license-server",
            host=DEFAULT_HOST,
            port=0,
            issuer=config.issuer,
            key_id=config.key_id,
            signing_secret=config.signing_secret,
        )
        service = LicenseService(config)
        service.store.save(service.store.load())
        server = ThreadingHTTPServer((config.host, 0), make_handler(service))
        host, port = server.server_address
        base_url = f"http://{host}:{port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        os.environ["PRISMA_LICENSE_SERVER_SILENT"] = "1"
        thread.start()
        time.sleep(0.15)

    lines = ["# PRISMA License Server MVP 06 Smoke", "", f"Base URL: `{base_url}`", ""]
    ok_all = True
    license_id = None
    try:
        status, body = http_json("GET", f"{base_url}/health")
        ok = status == 200 and body.get("ok") is True
        ok_all = ok_all and ok
        lines.append(f"- health: {'OK' if ok else 'FAIL'} status={status}")

        activation_request = {
            "customerId": DEFAULT_CUSTOMER_ID,
            "businessId": DEFAULT_BUSINESS_ID,
            "deviceId": DEFAULT_DEVICE_ID,
            "terminalId": DEFAULT_TERMINAL_ID,
            "plan": DEFAULT_PLAN,
        }
        status, body = http_json("POST", f"{base_url}/licenses/activate", activation_request)
        license_obj = body.get("data", {}).get("license", {}) if isinstance(body, dict) else {}
        license_id = license_obj.get("licenseId")
        ok = status == 200 and body.get("ok") is True and license_id and license_obj.get("signature", {}).get("algorithm") == "HS256_DEV_ONLY"
        ok_all = ok_all and bool(ok)
        lines.append(f"- activate: {'OK' if ok else 'FAIL'} status={status} licenseId={license_id}")

        status, body = http_json("POST", f"{base_url}/licenses/refresh", {"licenseId": license_id})
        ok = status == 200 and body.get("ok") is True and body.get("data", {}).get("license", {}).get("licenseId") == license_id
        ok_all = ok_all and ok
        lines.append(f"- refresh: {'OK' if ok else 'FAIL'} status={status}")

        current_url = f"{base_url}/licenses/current?" + urllib.parse.urlencode({"deviceId": DEFAULT_DEVICE_ID})
        status, body = http_json("GET", current_url)
        ok = status == 200 and body.get("ok") is True
        ok_all = ok_all and ok
        lines.append(f"- current: {'OK' if ok else 'FAIL'} status={status}")

        status, body = http_json("GET", f"{base_url}/customers/{DEFAULT_CUSTOMER_ID}/licenses")
        ok = status == 200 and body.get("ok") is True and body.get("data", {}).get("count", 0) >= 1
        ok_all = ok_all and ok
        lines.append(f"- customer licenses: {'OK' if ok else 'FAIL'} status={status}")

        status, body = http_json("POST", f"{base_url}/licenses/suspend", {"licenseId": license_id, "reason": "smoke_suspend"})
        ok = status == 200 and body.get("ok") is True and body.get("data", {}).get("license", {}).get("state") == "suspended"
        ok_all = ok_all and ok
        lines.append(f"- suspend: {'OK' if ok else 'FAIL'} status={status}")

        status, body = http_json("POST", f"{base_url}/licenses/revoke", {"licenseId": license_id, "reason": "smoke_revoke"})
        ok = status == 200 and body.get("ok") is True and body.get("data", {}).get("license", {}).get("state") == "revoked"
        ok_all = ok_all and ok
        lines.append(f"- revoke: {'OK' if ok else 'FAIL'} status={status}")

        lines.append("")
        lines.append("FINAL READY" if ok_all else "FINAL BLOCKED")
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))
        print(f"Report: {report}")
        return 0 if ok_all else 2
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if thread:
            thread.join(timeout=2)


def seed(args: argparse.Namespace) -> int:
    config = resolve_config(args)
    config.data_dir.mkdir(parents=True, exist_ok=True)
    result = LicenseService(config).seed()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("FINAL READY")
    return 0


def inspect_store(args: argparse.Namespace) -> int:
    config = resolve_config(args)
    data = JsonStore(config.store_path).load()
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRISMA License Server MVP 06")
    parser.add_argument("--root", default=None, help="Raiz del proyecto terminal-de-venta-system.")
    parser.add_argument("--data-dir", default=None, help="Directorio del store JSON. Puede ser relativo a --root.")
    parser.add_argument("--host", default=None, help="Host del servidor. Default 127.0.0.1.")
    parser.add_argument("--port", type=int, default=None, help="Puerto del servidor. Default 3140.")
    parser.add_argument("--issuer", default=None, help="Issuer de licencias.")
    parser.add_argument("--key-id", default=None, help="Key ID dev/staging.")
    parser.add_argument("--signing-secret", default=None, help="Secreto HMAC dev. Preferible via PRISMA_LICENSE_DEV_SIGNING_SECRET.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve", help="Arranca servidor local/staging.")
    smoke_parser = sub.add_parser("smoke", help="Ejecuta smoke. Si no se pasa --base-url, levanta servidor efimero.")
    smoke_parser.add_argument("--base-url", default=None, help="URL de servidor existente.")
    smoke_parser.add_argument("--out-dir", default=None, help="Directorio del reporte smoke.")
    sub.add_parser("seed", help="Crea cliente/negocio/dispositivo/licencia demo en el store.")
    sub.add_parser("inspect", help="Imprime el store JSON actual.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "serve":
        run_server(resolve_config(args))
        return 0
    if args.command == "smoke":
        return smoke(args)
    if args.command == "seed":
        return seed(args)
    if args.command == "inspect":
        return inspect_store(args)
    parser.error(f"Comando no soportado: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
