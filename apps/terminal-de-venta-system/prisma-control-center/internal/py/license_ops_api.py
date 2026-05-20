from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from config_loader import LOG_ROOT, TERMINAL_ROOT, ensure_log_dirs
from report_writer import export_support_bundle
from safe_actions import start_detached_process

SOURCE = "prisma-license-ops-api"
SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _logs_root() -> Path:
    root = LOG_ROOT / "license-ops"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _programdata_root() -> Path:
    return Path(os.environ.get("ProgramData") or r"C:\ProgramData")


def _canonical_config_root() -> Path:
    return _programdata_root() / "PRISMA" / "Commerce" / "Config"


def _canonical_runtime_config() -> Path:
    return _canonical_config_root() / "runtime.json"


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


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, val in value.items():
            low = str(key).lower()
            if any(token in low for token in ["path", "root", "command", "stdout", "stderr", "log", "token", "secret", "signature"]):
                out[key] = "<redacted>"
            else:
                out[key] = _redact(val)
        return out
    if isinstance(value, str) and (":\\" in value or ":/" in value):
        return "<redacted>"
    return value


def _node_executable() -> str:
    for candidate in ["node.exe", "node"]:
        found = shutil.which(candidate)
        if found:
            return found
    return "node.exe" if os.name == "nt" else "node"


def _pnpm_executable() -> str:
    for candidate in ["pnpm.cmd", "pnpm.exe", "pnpm"]:
        found = shutil.which(candidate)
        if found:
            return found
    return "pnpm.cmd" if os.name == "nt" else "pnpm"


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

    assignment = license_doc.get("assignment") if isinstance(license_doc, dict) else None
    if not isinstance(assignment, dict):
        assignment = {}

    license_summary = None
    if isinstance(license_doc, dict):
        license_summary = {
            "licenseId": license_doc.get("licenseId") or license_doc.get("id"),
            "plan": license_doc.get("plan"),
            "status": license_doc.get("status") or license_doc.get("state"),
            "validUntil": license_doc.get("validUntil") or license_doc.get("expiresAt"),
            "assignment": {
                "clientId": assignment.get("clientId") or license_doc.get("clientId"),
                "businessId": assignment.get("businessId") or license_doc.get("businessId"),
                "storeId": assignment.get("storeId") or assignment.get("branchId") or license_doc.get("storeId"),
                "terminalId": assignment.get("terminalId") or license_doc.get("terminalId"),
                "deviceId": assignment.get("deviceId") or assignment.get("tabletId") or license_doc.get("deviceId"),
            },
            "signaturePresent": bool(license_doc.get("signature") or license_doc.get("signed") or license_doc.get("proof")),
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
            "canonicalRoot": str(_canonical_config_root()),
            "repoRoot": str(TERMINAL_ROOT),
        },
    }
    return _redact(bundle) if public else bundle


LICENSE_OPS_ACTIONS: dict[str, dict[str, Any]] = {
    "detect-runtime": {
        "label": "Detectar runtime",
        "kind": "latest",
        "description": "Lee runtime, identidad y licencia desde ProgramData canonical o PRISMA_RUNTIME_CONFIG.",
    },
    "provision-tablet-solo-dry-run": {
        "label": "Dry run provisioning",
        "kind": "command",
        "timeout": 180,
        "args": ["tools/provision-prisma-runtime.mjs", "--dry-run", "--runtime-mode", "customer", "--vertical", "commerce", "--role", "tablet", "--package-type", "TABLET_SOLO"],
        "description": "Simula instalacion Tablet Solo sin escribir ProgramData.",
    },
    "provision-tablet-solo": {
        "label": "Provisionar Tablet Solo",
        "kind": "command",
        "timeout": 180,
        "args": ["tools/provision-prisma-runtime.mjs", "--apply", "--runtime-mode", "customer", "--vertical", "commerce", "--role", "tablet", "--package-type", "TABLET_SOLO"],
        "description": "Crea runtime.json, identidad y carpetas canonical de Tablet Solo.",
    },
    "validate-runtime-config": {
        "label": "Validar runtime config",
        "kind": "command",
        "timeout": 180,
        "args": ["tools/verify-runtime-config.mjs"],
        "description": "Ejecuta verify:runtime-config.",
    },
    "validate-provisioning": {
        "label": "Validar provisioning",
        "kind": "command",
        "timeout": 180,
        "args": ["tools/verify-tablet-provisioning.mjs"],
        "description": "Ejecuta verify:tablet-provisioning.",
    },
    "tablet-solo-smoke": {
        "label": "Tablet Solo smoke",
        "kind": "command",
        "timeout": 180,
        "args": ["tools/verify-tablet-solo-smoke.mjs"],
        "description": "Valida venta basica local y gating de licencia.",
    },
    "no-direct-db-in-ui": {
        "label": "No direct DB/license in UI",
        "kind": "command",
        "timeout": 180,
        "args": ["scripts/verify-no-direct-db-in-ui.mjs"],
        "description": "Confirma que UI no lee DB/licencia directa.",
    },
    "customer-smoke": {
        "label": "Customer smoke",
        "kind": "pnpm",
        "timeout": 320,
        "args": ["-C", "quality", "quality:customer-smoke"],
        "description": "Ejecuta customer smoke desde Quality.",
    },
    "export-evidence-zip": {
        "label": "Exportar evidencia ZIP",
        "kind": "export",
        "description": "Empaqueta evidencia local de Control Center y runtime/licencia.",
    },
    "open-programdata": {
        "label": "Abrir carpeta ProgramData",
        "kind": "open-programdata",
        "description": "Abre C:\\ProgramData\\PRISMA\\Commerce\\Config desde la maquina local.",
    },
    "start-tablet-runtime-config": {
        "label": "Levantar Tablet con PRISMA_RUNTIME_CONFIG",
        "kind": "spawn-tablet",
        "description": "Arranca Tablet usando runtime.json canonical.",
    },
    "import-local-license": {
        "label": "Importar licencia local",
        "kind": "import-license",
        "description": "Copia una licencia firmada al path resuelto por runtime.",
    },
}


def _actions_payload(public: bool = False) -> dict[str, Any]:
    actions = []
    for key, spec in LICENSE_OPS_ACTIONS.items():
        actions.append({
            "id": key,
            "label": spec.get("label"),
            "description": spec.get("description"),
            "url": f"/api/license-ops/run/{key}",
            "localOnly": True,
            "danger": False,
        })
    payload = {"ok": True, "schemaVersion": SCHEMA_VERSION, "source": SOURCE, "time": _now(), "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL", "actions": actions}
    return _redact(payload) if public else payload


def _write_action_log(action: str, cmd: list[str], completed: subprocess.CompletedProcess[str], started: str) -> Path:
    path = _logs_root() / f"license_ops_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    path.write_text(
        "PRISMA License Ops action\n"
        f"ACTION: {action}\n"
        "COMMAND: " + " ".join(cmd) + "\n"
        f"STARTED: {started}\n"
        f"FINISHED: {_now()}\n"
        f"RETURN_CODE: {completed.returncode}\n\n"
        "STDOUT:\n" + (completed.stdout or "") + "\n\n"
        "STDERR:\n" + (completed.stderr or "") + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _run_command_action(action: str, spec: dict[str, Any]) -> dict[str, Any]:
    node = _node_executable()
    cmd = [node] + [str(TERMINAL_ROOT / item) if item.endswith(".mjs") else item for item in spec.get("args", [])]
    started = _now()
    completed = subprocess.run(
        cmd,
        cwd=str(TERMINAL_ROOT),
        env={**os.environ, "NODE_DISABLE_COLORS": "1", "PRISMA_CONTROL_CENTER": "1"},
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=int(spec.get("timeout", 180)),
    )
    log = _write_action_log(action, cmd, completed, started)
    return {
        "ok": completed.returncode == 0,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "source": SOURCE,
        "action": action,
        "label": spec.get("label"),
        "startedAt": started,
        "finishedAt": _now(),
        "returnCode": completed.returncode,
        "log": str(log),
        "stdoutSample": (completed.stdout or "")[-3500:],
        "stderrSample": (completed.stderr or "")[-1800:],
        "latest": _latest_payload(public=False),
    }


def _run_pnpm_action(action: str, spec: dict[str, Any]) -> dict[str, Any]:
    cmd = [_pnpm_executable()] + list(spec.get("args", []))
    started = _now()
    completed = subprocess.run(
        cmd,
        cwd=str(TERMINAL_ROOT),
        env={**os.environ, "NODE_DISABLE_COLORS": "1", "PRISMA_CONTROL_CENTER": "1"},
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=int(spec.get("timeout", 320)),
    )
    log = _write_action_log(action, cmd, completed, started)
    return {
        "ok": completed.returncode == 0,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "source": SOURCE,
        "action": action,
        "label": spec.get("label"),
        "startedAt": started,
        "finishedAt": _now(),
        "returnCode": completed.returncode,
        "log": str(log),
        "stdoutSample": (completed.stdout or "")[-3500:],
        "stderrSample": (completed.stderr or "")[-1800:],
        "latest": _latest_payload(public=False),
    }


def _import_license(query: dict[str, list[str]]) -> dict[str, Any]:
    raw = (query.get("licenseFile") or query.get("path") or [""])[0]
    if not raw:
        return {"ok": False, "status": "INPUT_REQUIRED", "source": SOURCE, "action": "import-local-license", "requiredQuery": "licenseFile", "message": "Proporciona una ruta absoluta a licencia firmada."}
    source = Path(unquote(raw)).resolve()
    if not source.exists() or not source.is_file():
        return {"ok": False, "status": "LICENSE_SOURCE_MISSING", "source": SOURCE, "action": "import-local-license", "path": str(source)}
    bundle = _read_runtime_bundle(public=False)
    target_path = Path(str(bundle.get("licenseFile", {}).get("path") or _canonical_config_root() / "license.json"))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target_path)
    evidence = _logs_root() / f"license_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    payload = {"ok": True, "status": "IMPORTED", "source": SOURCE, "action": "import-local-license", "importedAt": _now(), "sourceFile": str(source), "targetFile": str(target_path)}
    evidence.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    payload["evidence"] = str(evidence)
    payload["latest"] = _latest_payload(public=False)
    return payload


def _export_evidence() -> dict[str, Any]:
    support = export_support_bundle()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_path = _logs_root() / f"prisma_license_ops_evidence_{stamp}.zip"
    include_paths: list[Path] = []
    for pattern in [
        "PRISMA_RUNTIME_CONFIG_VERIFY_*.json",
        "PRISMA_RUNTIME_CONFIG_VERIFY_*.md",
        "PRISMA_TABLET_PROVISIONING*.json",
        "PRISMA_TABLET_PROVISIONING*.md",
        "PRISMA_TABLET_SOLO_SMOKE_*.json",
        "PRISMA_TABLET_SOLO_SMOKE_*.md",
        "NO_DIRECT_DB_IN_UI_REPORT_*.json",
        "NO_DIRECT_DB_IN_UI_REPORT_*.md",
    ]:
        include_paths.extend(Path(r"F:\descargasf").glob(pattern))
    include_paths.extend(_logs_root().glob("*.log"))
    include_paths.extend(_logs_root().glob("*.json"))
    runtime_bundle = _read_runtime_bundle(public=False)
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("license-ops-runtime-summary.json", json.dumps(runtime_bundle, ensure_ascii=True, indent=2))
        for item in sorted(set(include_paths), key=lambda p: str(p))[-80:]:
            if item.exists() and item.is_file():
                try:
                    archive.write(item, arcname=f"evidence/{item.name}")
                except Exception:
                    continue
    return {"ok": True, "status": "EXPORTED", "source": SOURCE, "bundle": str(bundle_path), "supportBundle": support}


def _open_programdata() -> dict[str, Any]:
    path = _canonical_config_root()
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    return {"ok": True, "status": "OPENED", "source": SOURCE, "path": str(path)}


def _start_tablet_runtime_config() -> dict[str, Any]:
    runtime_path = _canonical_runtime_config()
    command = "pnpm -C products/tablet/app dev"
    result = start_detached_process(
        "tablet-runtime-config",
        command,
        str(TERMINAL_ROOT),
        env_extra={"PRISMA_RUNTIME_CONFIG": str(runtime_path)},
    )
    return {"ok": result.get("status") == "STARTED", "source": SOURCE, "action": "start-tablet-runtime-config", "runtimeConfig": str(runtime_path), **result}


def _run_action(action: str, query: dict[str, list[str]], public: bool) -> dict[str, Any]:
    if public:
        return {"ok": False, "status": "FORBIDDEN", "reason": "license ops actions are local-only", "source": SOURCE, "action": action}
    spec = LICENSE_OPS_ACTIONS.get(action)
    if not spec:
        return {"ok": False, "status": "UNKNOWN_ACTION", "source": SOURCE, "action": action, "availableActions": sorted(LICENSE_OPS_ACTIONS)}
    try:
        kind = spec.get("kind")
        if kind == "latest":
            return _latest_payload(public=False)
        if kind == "command":
            return _run_command_action(action, spec)
        if kind == "pnpm":
            return _run_pnpm_action(action, spec)
        if kind == "import-license":
            return _import_license(query)
        if kind == "export":
            return _export_evidence()
        if kind == "open-programdata":
            return _open_programdata()
        if kind == "spawn-tablet":
            return _start_tablet_runtime_config()
        return {"ok": False, "status": "UNSUPPORTED_ACTION_KIND", "source": SOURCE, "action": action, "kind": kind}
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "status": "TIMEOUT", "source": SOURCE, "action": action, "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "status": "ACTION_ERROR", "source": SOURCE, "action": action, "error": str(exc)}


def _tablet_db_path() -> Path:
    explicit = os.environ.get("TABLET_DATABASE_PATH")
    if explicit:
        return Path(explicit)
    return TERMINAL_ROOT / "products" / "tablet" / "app" / "data" / "tablet-pos.db"


def _sqlite_rows(db_path: Path, query: str) -> dict[str, Any]:
    if not db_path.exists():
        return {"available": False, "path": str(db_path), "reason": "tablet database not found"}
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
            latest = conn.execute(
                "select id, folio, businessId, terminalId, clientRequestId, status, createdAt, totalCents from Sale order by createdAt desc limit 5"
            ).fetchall()
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
            for key, val in value.items():
                walk(val, f"{key_path}.{key}" if key_path else str(key))
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
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "query": query,
        "runtime": runtime_bundle,
        "readOnly": True,
        "serverBoundary": [
            "products/tablet/app/app/api/pos/sales/detail/route.ts",
            "products/tablet/app/src/server/pos-api/sales-detail.prisma.ts",
            "products/tablet/app/src/server/prisma/client.ts",
            "shared/runtime/runtime-context-resolver.ts",
            "shared/licensing/license-loader.ts",
        ],
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
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "runtime": _read_runtime_bundle(public=public),
        "actions": _actions_payload(public=False)["actions"],
        "explorer": {
            "readOnly": True,
            "url": "/api/license-ops/explorer?query=<id>",
            "fields": ["clientId", "businessId", "storeId", "terminalId", "deviceId", "licenseId", "saleId", "folio", "clientRequestId", "featureKey", "entitlement"],
        },
    }
    return _redact(payload) if public else payload


def license_ops_payload(path_text: str, public: bool = False) -> dict[str, Any]:
    ensure_log_dirs()
    parsed = urlparse(path_text)
    path = parsed.path.rstrip("/") or "/api/license-ops/latest"
    query = parse_qs(parsed.query)
    if path == "/api/license-ops/actions":
        return _actions_payload(public=public)
    if path == "/api/license-ops/latest":
        return _latest_payload(public=public)
    if path == "/api/license-ops/explorer":
        return _explorer_payload((query.get("query") or query.get("q") or [""])[0], public=public)
    if path.startswith("/api/license-ops/run/"):
        action = path.rsplit("/", 1)[-1].strip().lower()
        return _run_action(action, query, public=public)
    return _latest_payload(public=public)
