#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prisma Cloud Center.

Private cockpit server for PRISMA Cloud on 127.0.0.1:3160. It keeps the
current Control Center on 3150 protected and exposes cloud, licensing,
runtime and diagnostic APIs through a local-only command surface.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cloud_saas_api
import license_ops_api
import command_center_store
import licflow4_admin_bridge
import support_resolver_api

SUPPORT_RESOLVER_RELOAD_LOCK = threading.Lock()

def support_resolver_payload(path: str, method: str = "GET", body: Dict[str, Any] | None = None, local_request: bool = False) -> Dict[str, Any]:
    """Reload support_resolver_api per request so Cloud Center support fixes are visible without stale module state."""
    global support_resolver_api
    with SUPPORT_RESOLVER_RELOAD_LOCK:
        support_resolver_api = importlib.reload(support_resolver_api)
    return support_resolver_api.support_payload(path, method=method, body=body, local_request=local_request)


APP_VERSION = "4.3.0-prisma-cloud-center-operator-readiness"
DEFAULT_PORT = 3160
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PROTECTED_CURRENT = r"F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center"
DEFAULT_OUT_DIR = r"F:\descargasf"

MODULE_CONTRACT: Dict[str, Any] = {
    "contractVersion": 1,
    "lab": {
        "name": "Prisma Cloud Center",
        "displayName": "Prisma Cloud Center",
        "mode": "PRISMA_CLOUD_CTR",
        "host": "127.0.0.1",
        "port": 3160,
        "themeInheritance": False,
        "noTouchPolicy": "Never modifies protected current Control Center",
    },
    "themeTokens": {
        "supportedThemes": ["prisma-frost-command"],
        "defaultTheme": "prisma-frost-command",
    },
    "modules": [
        {
            "id": "cloud-saas",
            "name": "Prisma Cloud Center",
            "role": "Cloud License Gateway + License Operations",
            "displayRole": "Cloud License Gateway + License Operations",
            "port": 3160,
            "portLabel": "app.hitechrts.com",
            "directUrl": "https://app.hitechrts.com",
            "embedUrl": "native://cloud-saas",
            "healthUrl": "https://app.hitechrts.com/health",
            "fallbackUrl": "https://app.hitechrts.com/health",
            "embedMode": "nativeCloud",
            "viewportMode": "desktop",
            "themeMode": "inherits",
            "protected": False,
            "actions": ["nativeCloud", "refresh", "adminBridge", "adminNote", "receiptSmoke", "deviceSmoke", "licenseOps"],
            "statusLabel": "LICFLOW3_CLOUDFLARE_ROUTES_LIVE",
            "statusDisplay": "Cloud License Gateway: Live",
            "qualityScope": ["cloud", "adminTokenPresenceOnly", "licflow4AdminBridge", "licenseAdminBridge", "licenseOpsReadOnly"],
            "healthKind": "cloud",
        },
        {
            "id": "control",
            "name": "Control Center bueno",
            "role": "Protegido / torre actual",
            "port": 3150,
            "directUrl": "http://127.0.0.1:3150",
            "embedUrl": "/__proxy__/3150/",
            "healthUrl": "http://127.0.0.1:3150",
            "fallbackUrl": "http://127.0.0.1:3150",
            "embedMode": "proxy",
            "viewportMode": "desktop",
            "themeMode": "isolated",
            "protected": True,
            "actions": ["openExternal", "reload", "health", "logs", "diagnostics"],
            "statusLabel": "PROTECTED_LINKED",
            "qualityScope": ["port", "http", "proxy"],
        },
        {
            "id": "chart",
            "name": "Chart Analytics",
            "role": "Analytics / lectura visual",
            "port": 3000,
            "directUrl": "http://127.0.0.1:3000",
            "embedUrl": "http://127.0.0.1:3000",
            "healthUrl": "http://127.0.0.1:3000",
            "fallbackUrl": "http://127.0.0.1:3000",
            "embedMode": "direct",
            "viewportMode": "desktop",
            "themeMode": "isolated",
            "protected": False,
            "actions": ["openEmbedded", "openExternal", "reload", "health", "logs"],
            "statusLabel": "OBSERVE",
            "qualityScope": ["port", "http"],
        },
        {
            "id": "web",
            "name": "Web/EIT",
            "role": "Web Control local",
            "port": 3110,
            "directUrl": "http://127.0.0.1:3110",
            "embedUrl": "http://127.0.0.1:3110",
            "healthUrl": "http://127.0.0.1:3110",
            "fallbackUrl": "http://127.0.0.1:3110",
            "embedMode": "direct",
            "viewportMode": "desktop",
            "themeMode": "isolated",
            "protected": False,
            "actions": ["openEmbedded", "openExternal", "reload", "health", "logs"],
            "statusLabel": "OBSERVE",
            "qualityScope": ["port", "http"],
        },
        {
            "id": "tablet",
            "name": "Tablet",
            "role": "Opera sola",
            "port": 3120,
            "directUrl": "http://127.0.0.1:3120",
            "embedUrl": "native://tablet-preview",
            "liveEmbedUrl": "http://127.0.0.1:3120",
            "healthUrl": "http://127.0.0.1:3120",
            "fallbackUrl": "http://127.0.0.1:3120",
            "embedMode": "nativePreview",
            "viewportMode": "tablet",
            "themeMode": "inherits",
            "protected": False,
            "actions": ["nativePreview", "liveEmbed", "openExternal", "health", "logs"],
            "statusLabel": "TABLET_OPERATES_ALONE",
            "qualityScope": ["port", "http", "canonicalRule"],
        },
        {
            "id": "pc",
            "name": "PC",
            "role": "Gobierna si existe",
            "port": 3130,
            "directUrl": "http://127.0.0.1:3130",
            "embedUrl": "http://127.0.0.1:3130",
            "healthUrl": "http://127.0.0.1:3130",
            "fallbackUrl": "http://127.0.0.1:3130",
            "embedMode": "direct",
            "viewportMode": "desktop",
            "themeMode": "isolated",
            "protected": False,
            "actions": ["openEmbedded", "openExternal", "reload", "health", "logs"],
            "statusLabel": "PC_GOVERNS_IF_PRESENT",
            "qualityScope": ["port", "http"],
        },
        {
            "id": "mobile",
            "name": "Mobile",
            "role": "Supervisa, no vende",
            "port": 3140,
            "directUrl": "http://127.0.0.1:3140",
            "embedUrl": "native://mobile-preview",
            "liveEmbedUrl": "http://127.0.0.1:3140",
            "healthUrl": "http://127.0.0.1:3140",
            "fallbackUrl": "http://127.0.0.1:3140",
            "embedMode": "nativePreview",
            "viewportMode": "mobile",
            "themeMode": "inherits",
            "protected": False,
            "actions": ["nativePreview", "liveEmbed", "openExternal", "health", "logs"],
            "statusLabel": "MOBILE_SUPERVISES",
            "qualityScope": ["port", "http", "canonicalRule"],
        },
        {
            "id": "addon",
            "name": "Nuevo Añadido",
            "role": "Slot listo para conectar",
            "port": 3165,
            "directUrl": "http://127.0.0.1:3165",
            "embedUrl": "native://addon-slot",
            "liveEmbedUrl": "http://127.0.0.1:3165",
            "healthUrl": "http://127.0.0.1:3165",
            "fallbackUrl": "http://127.0.0.1:3165",
            "embedMode": "nativePreview",
            "viewportMode": "fluid",
            "themeMode": "inherits",
            "protected": False,
            "actions": ["contract", "nativePreview", "liveEmbed", "openExternal", "health", "diagnostics"],
            "statusLabel": "SLOT_READY",
            "qualityScope": ["contract", "futurePort"],
        },
    ],
}

RUNTIME_LOCK = threading.Lock()
RUNTIME_STATE: Dict[str, Any] = {
    "startedAt": datetime.now().isoformat(timespec="seconds"),
    "lastHealthAt": None,
    "lastDiagnosticAt": None,
    "events": [],
}


def clean_path(value: str | None) -> Path:
    text = str(value or "")
    text = text.replace("\x00", "").replace("\r", "").replace("\n", "")
    text = text.strip().strip('"').strip("'").strip()
    while (text.endswith("\\") or text.endswith("/")) and len(text) > 3:
        text = text[:-1]
    if not text:
        raise RuntimeError("Ruta vacia")
    return Path(text)


def add_event(message: str, level: str = "info") -> None:
    event = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "level": level,
        "message": message,
    }
    with RUNTIME_LOCK:
        RUNTIME_STATE["events"].append(event)
        RUNTIME_STATE["events"] = RUNTIME_STATE["events"][-250:]
    print(f"[{level.upper()}] {message}", flush=True)


def run(args: List[str], timeout: int = 20) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(
            args,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as exc:
        return 127, "", str(exc)


def port_owners(port: int) -> List[int]:
    rc, out, err = run(["netstat.exe", "-ano", "-p", "tcp"], timeout=15)
    owners: List[int] = []
    for raw in out.splitlines():
        parts = re.split(r"\s+", raw.strip())
        if len(parts) < 5:
            continue
        local = parts[1]
        state = parts[3]
        pid_text = parts[4]
        if state.upper() != "LISTENING" or not pid_text.isdigit():
            continue
        match = re.search(r":(\d+)$", local)
        if match and int(match.group(1)) == port:
            owners.append(int(pid_text))
    return sorted(set(owners))


def process_info(pid: int) -> Dict[str, Any]:
    ps = (
        f"$p = Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\" -ErrorAction SilentlyContinue; "
        "if ($p) { Write-Output ([string]$p.Name + '|PRISMA_SPLIT|' + [string]$p.ExecutablePath + '|PRISMA_SPLIT|' + [string]$p.CommandLine + '|PRISMA_SPLIT|' + [string]$p.ParentProcessId) }"
    )
    rc, out, err = run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps], timeout=20)
    text = out.strip()
    if "|PRISMA_SPLIT|" in text:
        pieces = text.split("|PRISMA_SPLIT|")
        return {
            "pid": pid,
            "processName": pieces[0].strip() if len(pieces) > 0 else "unknown",
            "executablePath": pieces[1].strip() if len(pieces) > 1 else "",
            "commandLine": pieces[2].strip() if len(pieces) > 2 else "",
            "parentPid": pieces[3].strip() if len(pieces) > 3 else "",
        }
    return {"pid": pid, "processName": "unknown", "executablePath": "", "commandLine": "", "parentPid": ""}


def socket_alive(host: str, port: int, timeout: float = 0.65) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def http_probe(url: str, timeout: float = 1.2) -> Dict[str, Any]:
    started = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PRISMA-Lab-v3/health"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(256)
            elapsed = int((time.perf_counter() - started) * 1000)
            return {
                "ok": True,
                "statusCode": resp.status,
                "latencyMs": elapsed,
                "contentType": resp.headers.get("Content-Type", ""),
                "sampleBytes": len(body),
            }
    except urllib.error.HTTPError as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return {"ok": False, "statusCode": exc.code, "latencyMs": elapsed, "error": str(exc)}
    except Exception as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return {"ok": False, "statusCode": None, "latencyMs": elapsed, "error": str(exc)}


def classify_status(module: Dict[str, Any], socket_ok: bool, http: Dict[str, Any]) -> str:
    if module.get("embedMode") == "nativePreview" and module["id"] == "addon":
        return "SLOT_READY"
    if socket_ok and http.get("ok"):
        return "LIVE"
    if socket_ok:
        return "PARTIAL"
    if module.get("protected"):
        return "PROTECTED_OFFLINE"
    if module.get("embedMode") == "nativePreview":
        return "PREVIEW_ONLY"
    return "OFFLINE"


def health_snapshot() -> Dict[str, Any]:
    snapshot = []
    blockers = 0
    warnings = 0
    for module in MODULE_CONTRACT["modules"]:
        if module.get("healthKind") == "cloud":
            cloud = cloud_saas_api.quick_status()
            status = cloud.get("status", "CLOUD_UNKNOWN")
            if status != "CLOUD_LIVE":
                warnings += 1
            snapshot.append({
                "id": module["id"],
                "name": module["name"],
                "role": module["role"],
                "port": int(module["port"]),
                "portLabel": module.get("portLabel"),
                "embedMode": module["embedMode"],
                "viewportMode": module["viewportMode"],
                "themeMode": module["themeMode"],
                "protected": bool(module.get("protected")),
                "socketOk": True,
                "http": {
                    "ok": bool(cloud.get("ok")),
                    "statusCode": cloud.get("healthStatusCode"),
                    "latencyMs": cloud.get("latencyMs"),
                    "service": cloud.get("service"),
                    "version": cloud.get("version"),
                },
                "status": status,
                "owners": [],
                "directUrl": module["directUrl"],
                "embedUrl": module["embedUrl"],
                "liveEmbedUrl": module.get("liveEmbedUrl"),
                "actions": module.get("actions", []),
                "qualityScope": module.get("qualityScope", []),
            })
            continue
        port = int(module["port"])
        owners = port_owners(port)
        owner_infos = [process_info(pid) for pid in owners[:8]]
        socket_ok = socket_alive("127.0.0.1", port)
        http = http_probe(module.get("healthUrl", module["directUrl"])) if socket_ok else {"ok": False, "error": "port closed", "latencyMs": None}
        status = classify_status(module, socket_ok, http)
        if status in {"OFFLINE", "PROTECTED_OFFLINE"} and module["id"] not in {"addon"}:
            warnings += 1
        if status == "PARTIAL":
            warnings += 1
        snapshot.append({
            "id": module["id"],
            "name": module["name"],
            "role": module["role"],
            "port": port,
            "embedMode": module["embedMode"],
            "viewportMode": module["viewportMode"],
            "themeMode": module["themeMode"],
            "protected": bool(module.get("protected")),
            "socketOk": socket_ok,
            "http": http,
            "status": status,
            "owners": owner_infos,
            "directUrl": module["directUrl"],
            "embedUrl": module["embedUrl"],
            "liveEmbedUrl": module.get("liveEmbedUrl"),
            "actions": module.get("actions", []),
            "qualityScope": module.get("qualityScope", []),
        })
    overall = "OK" if warnings == 0 and blockers == 0 else ("PARTIAL" if blockers == 0 else "BLOCKED")
    with RUNTIME_LOCK:
        RUNTIME_STATE["lastHealthAt"] = datetime.now().isoformat(timespec="seconds")
    return {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "overall": overall,
        "blockers": blockers,
        "warnings": warnings,
        "modules": snapshot,
        "canonicalRule": "Tablet opera sola. PC gobierna si existe. Mobile supervisa. Core registra. Control audita.",
    }


def write_contract_files(lab_root: Path, protected_current: Path, out_dir: Path) -> None:
    runtime = lab_root / "internal" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    contract = json.loads(json.dumps(MODULE_CONTRACT))
    contract["lab"]["protectedCurrentPath"] = str(protected_current)
    contract["lab"]["outDir"] = str(out_dir)
    (runtime / "prisma-module-contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
    (runtime / "prisma-lab-port-override.json").write_text(json.dumps({
        "mode": "PRISMA_CLOUD_CTR",
        "cloudCenterHost": DEFAULT_HOST,
        "cloudCenterPort": DEFAULT_PORT,
        "cloudCenterUrl": f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/unified-shell.html",
        "protectedCurrentControlCenter": {
            "path": str(protected_current),
            "port": 3150,
            "url": "http://127.0.0.1:3150",
            "policy": "observe_only_do_not_kill",
        },
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
    }, indent=2, ensure_ascii=False), encoding="utf-8")


def export_diagnostics(out_dir: Path) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot = health_snapshot()
    with RUNTIME_LOCK:
        events = list(RUNTIME_STATE["events"])
        RUNTIME_STATE["lastDiagnosticAt"] = datetime.now().isoformat(timespec="seconds")
    payload = {
        "version": APP_VERSION,
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "health": snapshot,
        "runtimeState": RUNTIME_STATE,
        "events": events,
        "contract": MODULE_CONTRACT,
        "cloudSaas": cloud_saas_api.summary_payload(allow_admin=False),
        "licenseOps": license_ops_api.license_ops_payload("/api/license-ops/latest", public=True),
        "licenseAdminBridge": licflow4_admin_bridge.diagnostics_payload(),
        "licflow4AdminBridge": licflow4_admin_bridge.diagnostics_payload(),
    }
    json_path = out_dir / f"PRISMA_CLOUD_CTR_DIAGNOSTICS_{ts}.json"
    txt_path = out_dir / f"PRISMA_CLOUD_CTR_DIAGNOSTICS_{ts}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "Prisma Cloud Center diagnostics",
        f"Generated: {payload['generatedAt']}",
        f"Overall: {snapshot['overall']}",
        f"Warnings: {snapshot['warnings']}",
        "",
        "Modules:",
    ]
    for module in snapshot["modules"]:
        lines.append(f"- {module['name']} port={module['port']} status={module['status']} mode={module['embedMode']} url={module['directUrl']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    add_event(f"Diagnostics exported: {json_path}")
    return {"json": str(json_path), "txt": str(txt_path), "payload": payload}


def command_center_html(lab_root: Path) -> str:
    html_path = lab_root / "internal" / "web" / "cloud_command_center.html"
    try:
        return html_path.read_text(encoding="utf-8")
    except Exception as exc:
        add_event(f"Command Center HTML fallback: {exc}", "warn")
        return """<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><title>Prisma Cloud Center</title><body style=\"font-family:Segoe UI;background:#07101b;color:#f4f8fc;padding:32px\"><h1>Prisma Cloud Center</h1><p>Web assets are not available. Check internal/web/cloud_command_center.html.</p></body></html>"""


def replace_absolute_refs(html: str, port: int) -> str:
    prefix = f"/__proxy__/{port}"
    html = re.sub(r"(<head[^>]*>)", r"\1<base href=\"" + prefix + r"/\">", html, count=1, flags=re.I)
    html = re.sub(r"((?:href|src|action)=[\"'])/(?!/)", r"\1" + prefix + r"/", html, flags=re.I)
    html = re.sub(r"(url\([\"']?)/(?!/)", r"\1" + prefix + r"/", html, flags=re.I)
    for root in ["_next", "api", "static", "assets"]:
        html = html.replace(f'"/{root}/', f'"{prefix}/{root}/')
        html = html.replace(f"'/{root}/", f"'{prefix}/{root}/")
    return html


UI_HTML = r'''<!doctype html>
<html lang="es" data-theme="obsidian">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Prisma Cloud Center</title>
<link rel="stylesheet" href="/internal/web/cloud_saas_console.css" />
<link rel="stylesheet" href="/internal/web/license_ops_console.css" />
<style>
:root {
  --bg:#07111e; --panel:rgba(255,255,255,.075); --panel2:rgba(255,255,255,.11); --panel3:rgba(255,255,255,.15);
  --text:#eef7ff; --muted:rgba(238,247,255,.68); --line:rgba(255,255,255,.16);
  --accent:#63d7ff; --ok:#45f0a6; --warn:#ffd36a; --bad:#ff6d7a; --violet:#cb8cff;
  --shadow:0 26px 80px rgba(0,0,0,.38); --radius:26px;
}
html[data-theme="liquid"] { --bg:#06151a; --accent:#6fffe9; --panel:rgba(111,255,233,.08); --panel2:rgba(111,255,233,.13); --text:#edfffb; --muted:rgba(237,255,251,.68); --line:rgba(111,255,233,.20); }
html[data-theme="pearl"] { --bg:#edf3f8; --accent:#0b7dff; --panel:rgba(255,255,255,.70); --panel2:rgba(255,255,255,.92); --text:#142033; --muted:rgba(20,32,51,.66); --line:rgba(20,32,51,.14); --shadow:0 26px 80px rgba(35,62,96,.16); }
html[data-theme="rose"] { --bg:#130916; --accent:#cb8cff; --panel:rgba(255,130,210,.08); --panel2:rgba(160,120,255,.13); --text:#fff2fb; --muted:rgba(255,242,251,.68); --line:rgba(255,180,235,.20); }
html[data-theme="tactical"] { --bg:#070908; --accent:#a9ff68; --panel:rgba(169,255,104,.07); --panel2:rgba(169,255,104,.11); --text:#f4ffee; --muted:rgba(244,255,238,.66); --line:rgba(169,255,104,.18); }
* { box-sizing:border-box; }
body { margin:0; min-height:100vh; color:var(--text); font-family:Inter,Segoe UI,system-ui,sans-serif; background:radial-gradient(circle at 14% 12%, color-mix(in srgb,var(--accent) 28%,transparent), transparent 34%), radial-gradient(circle at 84% 0%, rgba(120,92,255,.24), transparent 32%), linear-gradient(135deg,var(--bg),color-mix(in srgb,var(--bg) 84%,#000 16%)); }
.shell { display:grid; grid-template-columns:330px 1fr; gap:18px; padding:18px; min-height:100vh; }
.card { border:1px solid var(--line); background:linear-gradient(145deg,var(--panel2),var(--panel)); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(18px); }
.side { padding:18px; display:flex; flex-direction:column; gap:14px; min-height:0; }
.brand h1 { margin:0; font-size:22px; letter-spacing:-.04em; }
.brand p { margin:5px 0 0; color:var(--muted); font-size:12px; line-height:1.35; }
.theme { border:1px solid var(--line); color:var(--text); background:var(--panel); border-radius:14px; padding:10px; }
.tabs { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.tabbtn { border:1px solid var(--line); color:var(--text); background:rgba(255,255,255,.05); border-radius:14px; padding:10px; cursor:pointer; font-weight:800; }
.tabbtn.active { border-color:var(--accent); background:color-mix(in srgb,var(--accent) 18%,transparent); }
.panel { display:none; min-height:0; }
.panel.active { display:block; }
.motor { cursor:pointer; border:1px solid var(--line); background:rgba(255,255,255,.055); padding:14px; border-radius:20px; transition:.16s ease; margin-bottom:8px; }
.motor:hover { transform:translateY(-1px); border-color:color-mix(in srgb,var(--accent) 62%,var(--line)); }
.motor.active { border-color:var(--accent); background:color-mix(in srgb,var(--accent) 18%,transparent); }
.motor strong { display:block; font-size:14px; }
.motor span { display:block; color:var(--muted); font-size:12px; margin-top:5px; }
.statusRow { display:flex; align-items:center; justify-content:space-between; gap:8px; }
.pill { display:inline-flex; padding:5px 8px; border-radius:999px; border:1px solid var(--line); font-size:10px; color:var(--muted); }
.pill.live { color:var(--ok); border-color:color-mix(in srgb,var(--ok) 40%,var(--line)); }
.pill.warn { color:var(--warn); border-color:color-mix(in srgb,var(--warn) 45%,var(--line)); }
.pill.bad { color:var(--bad); border-color:color-mix(in srgb,var(--bad) 45%,var(--line)); }
.main { display:grid; grid-template-rows:auto auto 1fr auto; overflow:hidden; }
.top { padding:18px; display:flex; align-items:center; justify-content:space-between; gap:14px; border-bottom:1px solid var(--line); }
.top h2 { margin:0; font-size:23px; letter-spacing:-.035em; }
.top p { margin:5px 0 0; color:var(--muted); }
.actions { display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }
button,a.btn { border:1px solid var(--line); background:color-mix(in srgb,var(--accent) 18%,var(--panel)); color:var(--text); padding:10px 13px; border-radius:15px; text-decoration:none; cursor:pointer; font-weight:800; }
button.secondary,a.secondary { background:rgba(255,255,255,.06); }
.meta { padding:14px 18px; display:grid; grid-template-columns:repeat(5,minmax(110px,1fr)); gap:10px; border-bottom:1px solid var(--line); }
.kpi { padding:12px; border-radius:18px; border:1px solid var(--line); background:rgba(255,255,255,.052); min-width:0; }
.kpi label { display:block; color:var(--muted); font-size:11px; }
.kpi strong { display:block; margin-top:4px; font-size:13px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.workspace { padding:18px; display:grid; min-height:0; }
.frame-wrap { min-height:520px; overflow:hidden; border-radius:22px; border:1px solid var(--line); background:rgba(0,0,0,.20); position:relative; }
iframe { width:100%; height:100%; min-height:600px; border:0; background:white; }
.native { display:none; width:100%; height:100%; min-height:600px; padding:28px; }
.native.show { display:grid; place-items:center; }
.device { width:min(410px,96%); min-height:560px; border-radius:42px; border:1px solid var(--line); background:linear-gradient(160deg,var(--panel2),rgba(0,0,0,.25)); box-shadow:var(--shadow); padding:22px; display:flex; flex-direction:column; gap:12px; }
.tabletDevice { width:min(880px,96%); min-height:520px; border-radius:34px; }
.screen { flex:1; border-radius:28px; background:linear-gradient(135deg,rgba(255,255,255,.16),rgba(255,255,255,.045)); border:1px solid var(--line); padding:18px; display:flex; flex-direction:column; gap:14px; }
.fakeCard { height:54px; border-radius:18px; background:rgba(255,255,255,.10); border:1px solid var(--line); }
.addonBox { width:min(820px,96%); border-radius:30px; padding:28px; border:1px solid var(--line); background:linear-gradient(145deg,var(--panel2),var(--panel)); }
.addonGrid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:18px; }
.fallback { position:absolute; inset:0; display:none; place-items:center; padding:30px; text-align:center; background:linear-gradient(145deg,var(--panel2),var(--panel)); }
.fallback.show { display:grid; }
.fallback h3 { margin:0 0 8px; }
.fallback p { margin:0 auto 16px; color:var(--muted); max-width:680px; }
.bottom { padding:12px 18px; border-top:1px solid var(--line); color:var(--muted); font-size:12px; display:flex; justify-content:space-between; gap:14px; }
.drawer { padding:14px; border-radius:20px; background:rgba(255,255,255,.05); border:1px solid var(--line); margin-bottom:10px; }
.drawer h3 { margin:0 0 8px; font-size:14px; }
.drawer p, .drawer li { color:var(--muted); font-size:12px; line-height:1.45; }
pre { white-space:pre-wrap; word-break:break-word; color:var(--muted); background:rgba(0,0,0,.18); border:1px solid var(--line); border-radius:18px; padding:12px; max-height:300px; overflow:auto; font-size:11px; }
@media (max-width:1100px) { .shell { grid-template-columns:1fr; } .meta { grid-template-columns:1fr 1fr; } }
</style>
</head>
<body>
<div class="shell">
  <aside class="side card">
    <div class="brand">
      <h1>Prisma Cloud Center</h1>
      <p>Consola local 3160 para licencias, LICFLOW3, health, diagnostics y evidencia sanitizada.</p>
    </div>
    <select class="theme" id="theme">
      <option value="obsidian">Obsidian Glass</option>
      <option value="liquid">Liquid Metal</option>
      <option value="pearl">Pearl Ice</option>
      <option value="rose">Obsidian Rose</option>
      <option value="tactical">Tactical Green</option>
    </select>
    <div class="tabs">
      <button class="tabbtn active" data-panel="modules">Módulos</button>
      <button class="tabbtn" data-panel="cloudPanel">Cloud SaaS</button>
      <button class="tabbtn" data-panel="licensePanel">Licencias</button>
      <button class="tabbtn" data-panel="quality">Quality</button>
      <button class="tabbtn" data-panel="logs">Logs</button>
      <button class="tabbtn" data-panel="contract">Contrato</button>
    </div>
    <div id="modules" class="panel active"></div>
    <div id="cloudPanel" class="panel"></div>
    <div id="licensePanel" class="panel"></div>
    <div id="quality" class="panel"></div>
    <div id="logs" class="panel"></div>
    <div id="contract" class="panel"></div>
  </aside>

  <main class="main card">
    <header class="top">
      <div><h2 id="title">Control Center bueno</h2><p id="subtitle">Protegido y observable.</p></div>
      <div class="actions">
        <button class="secondary" onclick="setViewMode('nativePreview')">Preview</button>
        <button class="secondary" onclick="setViewMode('direct')">Live embed</button>
        <button class="secondary" onclick="reloadFrame()">Reload</button>
        <button onclick="refreshHealth()">Health</button>
        <button onclick="exportDiagnostics()">Export diag</button>
        <a class="btn" id="openExternal" target="_blank" rel="noreferrer">Abrir externo</a>
      </div>
    </header>
    <section class="meta">
      <div class="kpi"><label>Estado</label><strong id="status">...</strong></div>
      <div class="kpi"><label>Puerto</label><strong id="port">...</strong></div>
      <div class="kpi"><label>Embed</label><strong id="embedMode">...</strong></div>
      <div class="kpi"><label>Viewport</label><strong id="viewportMode">...</strong></div>
      <div class="kpi"><label>Tema</label><strong id="themeMode">...</strong></div>
    </section>
    <section class="workspace">
      <div class="frame-wrap">
        <iframe id="frame" title="PRISMA module"></iframe>
        <div class="native" id="native"></div>
        <div class="fallback" id="fallback"><div><h3>No se pudo embeber este módulo</h3><p id="fallbackText">Usa Abrir externo o revisa health/logs.</p><a class="btn" id="fallbackOpen" target="_blank" rel="noreferrer">Abrir externo</a></div></div>
      </div>
    </section>
    <footer class="bottom"><span id="footLeft">Tablet opera sola. PC gobierna si existe. Mobile supervisa.</span><span id="footRight">Core registra · Control audita</span></footer>
  </main>
</div>
<script src="/internal/web/license_ops_console.js"></script>
<script src="/internal/web/cloud_saas_console.js"></script>
<script>
let contract = null;
let health = null;
let current = null;
let forcedMode = null;
const $ = (id) => document.getElementById(id);

async function api(path, opts) { const r = await fetch(path, opts); if(!r.ok) throw new Error(path + ' -> ' + r.status); return r.json(); }
function statusClass(s) { const raw = String(s || '').toUpperCase(); return (raw.includes('LIVE') || raw.includes('READY') || raw.includes('LINKED') || raw.includes('FULL')) ? 'live' : (raw.includes('PARTIAL') || raw.includes('PREVIEW') || raw.includes('READONLY') || raw.includes('READ_ONLY') || raw.includes('MISSING') || raw.includes('OFFLINE')) ? 'warn' : 'bad'; }
function moduleHealth(id) { return health?.modules?.find(m => m.id === id); }

function setPanel(id) { document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active')); document.querySelectorAll('.tabbtn').forEach(b=>b.classList.toggle('active', b.dataset.panel===id)); $(id).classList.add('active'); }
document.querySelectorAll('.tabbtn').forEach(b=>b.onclick=()=>setPanel(b.dataset.panel));

function applyTheme() { const t = localStorage.getItem('prisma.cloud.ctr.theme') || contract?.themeTokens?.defaultTheme || 'obsidian'; document.documentElement.dataset.theme = t; $('theme').value = t; }
$('theme').onchange = () => { localStorage.setItem('prisma.cloud.ctr.theme', $('theme').value); applyTheme(); };

function renderModules() {
  const wrap = $('modules'); wrap.innerHTML = '';
  contract.modules.forEach(m => {
    const h = moduleHealth(m.id) || {};
    const portText = m.portLabel || ('puerto ' + m.port);
    const div = document.createElement('div');
    div.className = 'motor' + (current?.id === m.id ? ' active' : '');
    div.innerHTML = `<div class="statusRow"><strong>${m.name}</strong><span class="pill ${statusClass(h.status || m.statusLabel)}">${h.status || m.statusLabel}</span></div><span>${m.role} · ${portText} · ${m.embedMode}</span>`;
    div.onclick = () => selectModule(m.id);
    wrap.appendChild(div);
  });
}

function openCloudView(view) {
  selectModule('cloud-saas');
  setTimeout(() => window.PRISMA_CLOUD_SAAS?.setView(view), 0);
}

function renderSidePanels() {
  $('cloudPanel').innerHTML = `<div class="drawer"><h3>Cloud SaaS</h3><p>PRISMA Cloud Semilla, Prisma Original Customer, snapshots, notes, receipts y status.</p><button onclick="openCloudView('overview')">Abrir Cloud SaaS</button><button class="secondary" onclick="openCloudView('health')">Health</button><button class="secondary" onclick="openCloudView('commercial')">Commercial</button></div>`;
  $('licensePanel').innerHTML = `<div class="drawer"><h3>Licencias</h3><p>Modulo 3150 adaptado en modo read-only dentro de Prisma Cloud Center.</p><button onclick="openCloudView('licenses')">Abrir Licencias</button></div>`;
}

function renderQuality() {
  const wrap = $('quality');
  const rows = (health?.modules || []).filter(m => !['LIVE','SLOT_READY','PREVIEW_ONLY'].includes(m.status));
  let html = '<div class="drawer"><h3>Quality Bay</h3><p>Solo problemas reales o condiciones accionables. Nada de tiliches.</p></div>';
  if (!rows.length) html += '<div class="drawer"><h3>OK</h3><p>Sin blockers. Si un módulo está apagado pero es preview/slot, no se marca como incendio.</p></div>';
  rows.forEach(m => { html += `<div class="drawer"><h3>${m.name}</h3><p>Status: ${m.status}</p><p>Puerto ${m.port}. HTTP: ${m.http?.statusCode || 'n/a'} ${m.http?.error || ''}</p></div>`; });
  wrap.innerHTML = html;
}

function renderLogs() {
  const wrap = $('logs');
  const events = health?.events || [];
  wrap.innerHTML = `<div class="drawer"><h3>Runtime logs</h3><p>Últimos eventos del runtime.</p><pre>${JSON.stringify(events.slice(-40), null, 2)}</pre></div>`;
}

function renderContract() {
  $('contract').innerHTML = `<div class="drawer"><h3>Module Contract</h3><p>Contrato vivo usado por Prisma Cloud Center.</p><pre>${JSON.stringify(contract, null, 2)}</pre></div>`;
}

function nativeHtml(m) {
  if (m.id === 'cloud-saas') return `<div id="cloudSaasConsole" class="cloudSaasMount"></div>`;
  if (m.id === 'mobile') return `<div class="device"><div class="screen"><span class="pill live">MOBILE SUPERVISA</span><h2>Mobile Intelligence Layer</h2><p>Snapshot, freshness, alertas, action inbox y evidencia. No vende; supervisa.</p><div class="fakeCard"></div><div class="fakeCard"></div><div class="fakeCard"></div><button onclick="setViewMode('direct')">Ver app viva en 3140</button></div></div>`;
  if (m.id === 'tablet') return `<div class="device tabletDevice"><div class="screen"><span class="pill live">TABLET OPERA SOLA</span><h2>Tablet Operations Preview</h2><p>La tablet no depende de PC, Mobile, cloud ni consola para operar.</p><div class="fakeCard"></div><div class="fakeCard"></div><button onclick="setViewMode('direct')">Ver tablet viva en 3120</button></div></div>`;
  if (m.id === 'addon') return `<div class="addonBox"><span class="pill live">SLOT READY · 3165</span><h2>Nuevo Añadido</h2><p>Contrato listo para conectar módulo real sin duplicar bays. Hereda temas, health, logs y fallback.</p><div class="addonGrid"><div class="kpi"><label>embedMode</label><strong>nativePreview</strong></div><div class="kpi"><label>Puerto</label><strong>3165</strong></div><div class="kpi"><label>Estado</label><strong>SLOT_READY</strong></div></div><br><button onclick="setViewMode('direct')">Probar live embed 3165</button></div>`;
  return `<div class="addonBox"><span class="pill warn">PREVIEW</span><h2>${m.name}</h2><p>Este módulo usa ${m.embedMode}. Puedes cambiar a live embed o abrir externo.</p><button onclick="setViewMode('direct')">Ver live embed</button></div>`;
}

function showNative(m) { $('frame').style.display = 'none'; $('fallback').classList.remove('show'); $('native').classList.add('show'); $('native').classList.toggle('cloudSaasNative', m.id === 'cloud-saas'); $('native').innerHTML = nativeHtml(m); if (m.id === 'cloud-saas') window.PRISMA_CLOUD_SAAS?.mount('cloudSaasConsole'); }
function showFrame(src) { $('native').classList.remove('show'); $('native').innerHTML = ''; $('frame').style.display = 'block'; $('fallback').classList.remove('show'); $('frame').src = src + (src.includes('?') ? '&' : '?') + '_=' + Date.now(); }

function selectModule(id) {
  current = contract.modules.find(m=>m.id===id) || contract.modules[0];
  localStorage.setItem('prisma.cloud.ctr.lastModule', current.id);
  forcedMode = null;
  renderCurrent(); renderModules();
}
function setViewMode(mode) { forcedMode = mode; renderCurrent(); }
function renderCurrent() {
  const h = moduleHealth(current.id) || {};
  $('title').textContent = current.name; $('subtitle').textContent = current.role;
  $('status').textContent = h.status || current.statusLabel; $('port').textContent = current.portLabel || h.portLabel || current.port;
  $('embedMode').textContent = forcedMode || current.embedMode; $('viewportMode').textContent = current.viewportMode; $('themeMode').textContent = current.themeMode;
  $('openExternal').href = current.directUrl; $('fallbackOpen').href = current.fallbackUrl || current.directUrl;
  const mode = forcedMode || current.embedMode;
  if (mode === 'nativePreview' || mode === 'nativeCloud') showNative(current); else if (mode === 'direct') showFrame(current.liveEmbedUrl || current.directUrl); else showFrame(current.embedUrl);
}
function reloadFrame() { renderCurrent(); }
async function refreshHealth() { health = await api('/api/health'); health.events = (await api('/api/runtime')).events; renderModules(); renderQuality(); renderLogs(); if(current) renderCurrent(); }
async function exportDiagnostics() { const r = await api('/api/export-diagnostics', {method:'POST'}); alert('Diagnóstico exportado:\n' + r.json + '\n' + r.txt); await refreshHealth(); }
async function boot() { contract = await api('/api/contract'); applyTheme(); renderSidePanels(); await refreshHealth(); renderContract(); const last = localStorage.getItem('prisma.cloud.ctr.lastModule') || 'cloud-saas'; selectModule(last); setInterval(refreshHealth, 10000); }
boot().catch(e => { document.body.innerHTML = '<pre style="color:white;padding:20px">' + e.stack + '</pre>'; });
</script>
</body>
</html>
'''


class PrismaLabHandler(SimpleHTTPRequestHandler):
    server_version = "PRISMA-Cloud-Ctr"

    def __init__(self, *args: Any, directory: str | None = None, lab_root: Path, protected_current: Path, out_dir: Path, **kwargs: Any) -> None:
        self.lab_root = lab_root
        self.protected_current = protected_current
        self.out_dir = out_dir
        super().__init__(*args, directory=directory, **kwargs)

    def json_response(self, payload: Any, code: int = 200) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def html_response(self, html: str, code: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def is_local_operator_request(self) -> bool:
        client = str(self.client_address[0] or "").lower()
        host_header = str(self.headers.get("Host", "")).lower()
        if host_header.startswith("[") and "]" in host_header:
            host = host_header.split("]", 1)[0].strip("[]")
        else:
            host = host_header.split(":", 1)[0].strip("[]")
        local_values = {"", "127.0.0.1", "localhost", "::1"}
        return client in {"127.0.0.1", "::1", "::ffff:127.0.0.1"} and host in local_values

    def read_json_body(self) -> Dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        if length > 65536:
            raise RuntimeError("JSON body too large")
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8", errors="replace"))
        return payload if isinstance(payload, dict) else {}

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/export-diagnostics":
            result = export_diagnostics(self.out_dir)
            self.json_response({"ok": True, "json": result["json"], "txt": result["txt"]})
            return
        if path.startswith("/api/command-center"):
            try:
                body = self.read_json_body()
                payload = command_center_store.command_center_payload(self.path, method="POST", body=body)
                code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))
                self.json_response(payload, code=code)
            except Exception as exc:
                self.json_response({"ok": False, "error": str(exc)}, code=400)
            return
        if path.startswith("/api/licflow4/bridge"):
            try:
                body = self.read_json_body()
                payload = licflow4_admin_bridge.bridge_payload(
                    self.path,
                    method="POST",
                    body=body,
                    local_request=self.is_local_operator_request(),
                )
                code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))
                self.json_response(payload, code=code)
            except Exception as exc:
                self.json_response({"ok": False, "code": "LICFLOW4_BRIDGE_ERROR", "error": str(exc), "secretsExposed": False}, code=400)
            return
        if path.startswith("/api/support"):
            try:
                body = self.read_json_body()
                payload = support_resolver_payload(
                    self.path,
                    method="POST",
                    body=body,
                    local_request=self.is_local_operator_request(),
                )
                code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))
                self.json_response(payload, code=code)
            except Exception as exc:
                self.json_response({"ok": False, "code": "SUPPORT_RESOLVER_ERROR", "error": str(exc), "secretsExposed": False}, code=400)
            return
        if path.startswith("/api/cloud-saas"):
            try:
                body = self.read_json_body()
                payload = cloud_saas_api.cloud_saas_payload(self.path, method="POST", body=body, allow_admin=self.is_local_operator_request())
                self.json_response(payload, code=200 if payload.get("ok") or payload.get("skipped") else 409)
            except Exception as exc:
                self.json_response({"ok": False, "error": str(exc)}, code=400)
            return
        if path.startswith("/api/license-ops"):
            payload = license_ops_api.license_ops_payload(self.path, public=not self.is_local_operator_request())
            self.json_response(payload, code=200 if payload.get("ok") else 409)
            return
        self.json_response({"ok": False, "error": "Unknown POST"}, code=404)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("", "/", "/unified-shell.html", "/index.html"):
            self.html_response(command_center_html(self.lab_root))
            return
        if path == "/api/contract":
            self.json_response(MODULE_CONTRACT)
            return
        if path == "/api/health":
            self.json_response(health_snapshot())
            return
        if path == "/api/runtime":
            with RUNTIME_LOCK:
                payload = dict(RUNTIME_STATE)
            self.json_response(payload)
            return
        if path.startswith("/api/command-center"):
            payload = command_center_store.command_center_payload(self.path, method="GET")
            code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))
            self.json_response(payload, code=code)
            return
        if path.startswith("/api/licflow4/bridge"):
            payload = licflow4_admin_bridge.bridge_payload(self.path, method="GET", local_request=self.is_local_operator_request())
            code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))
            self.json_response(payload, code=code)
            return
        if path.startswith("/api/support"):
            payload = support_resolver_payload(self.path, method="GET", local_request=self.is_local_operator_request())
            code = int(payload.pop("_httpStatus", 200 if payload.get("ok") else 409))
            self.json_response(payload, code=code)
            return
        if path.startswith("/api/cloud-saas"):
            payload = cloud_saas_api.cloud_saas_payload(self.path, method="GET", allow_admin=self.is_local_operator_request())
            self.json_response(payload, code=200 if payload.get("ok") else 409)
            return
        if path.startswith("/api/license-ops"):
            payload = license_ops_api.license_ops_payload(self.path, public=not self.is_local_operator_request())
            self.json_response(payload, code=200 if payload.get("ok") else 409)
            return
        if path.startswith("/__proxy__/"):
            self.proxy_request()
            return
        return super().do_GET()

    def proxy_request(self) -> None:
        match = re.match(r"^/__proxy__/(\d+)(/.*)?$", self.path)
        if not match:
            self.send_error(404, "Bad proxy path")
            return
        port = int(match.group(1))
        rest = match.group(2) or "/"
        allowed_ports = {int(m["port"]) for m in MODULE_CONTRACT["modules"]}
        if port not in allowed_ports:
            self.send_error(403, "Proxy port not allowed")
            return
        target = f"http://127.0.0.1:{port}{rest}"
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "PRISMA-Cloud-Ctr/proxy", "Accept": self.headers.get("Accept", "*/*")})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                content_type = resp.headers.get("Content-Type", "application/octet-stream")
                blocked = {"x-frame-options", "content-security-policy", "content-security-policy-report-only", "transfer-encoding", "content-encoding", "connection", "keep-alive", "server", "date"}
                if "text/html" in content_type.lower():
                    try:
                        text = raw.decode("utf-8", errors="replace")
                        raw = replace_absolute_refs(text, port).encode("utf-8")
                    except Exception:
                        pass
                self.send_response(resp.status)
                for key, value in resp.headers.items():
                    if key.lower() in blocked or key.lower() == "content-length":
                        continue
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-PRISMA-Cloud-Ctr-Proxy", APP_VERSION)
                self.end_headers()
                self.wfile.write(raw)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "text/plain"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            body = f"""<!doctype html><meta charset=\"utf-8\"><title>PRISMA proxy offline</title>
            <body style=\"font-family:Segoe UI;background:#130916;color:white;padding:30px\">
            <h2>Modulo no disponible por proxy</h2><p>Puerto destino: {port}</p><p>Error: {exc}</p>
            <p><a style=\"color:#cb8cff\" href=\"http://127.0.0.1:{port}\" target=\"_blank\">Abrir externo</a></p></body>""".encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        add_event(fmt % args, "http")


def serve(lab_root: Path, protected_current: Path, out_dir: Path, host: str, port: int) -> None:
    write_contract_files(lab_root, protected_current, out_dir)
    lab_root.mkdir(parents=True, exist_ok=True)
    handler = partial(PrismaLabHandler, directory=str(lab_root), lab_root=lab_root, protected_current=protected_current, out_dir=out_dir)
    httpd = ThreadingHTTPServer((host, port), handler)
    add_event(f"Prisma Cloud Center listening on http://{host}:{port}/unified-shell.html")
    httpd.serve_forever()


def start(lab_root: Path, protected_current: Path, out_dir: Path, host: str, port: int, open_browser: bool) -> None:
    lab_root.mkdir(parents=True, exist_ok=True)
    write_contract_files(lab_root, protected_current, out_dir)
    if not port_owners(port):
        env = os.environ.copy()
        env["PRISMA_LAB_ROOT"] = str(lab_root)
        env["PRISMA_PROTECTED_CURRENT"] = str(protected_current)
        env["PRISMA_OUT_DIR"] = str(out_dir)
        env["PRISMA_LAB_HOST"] = host
        env["PRISMA_LAB_PORT"] = str(port)
        subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--serve"],
            cwd=str(lab_root),
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.5)
    else:
        print(f"Puerto {port} ya tiene un proceso escuchando; no se mata ni se reemplaza. Reabre manualmente si necesitas recargar Prisma Cloud Center.")
    url = f"http://{host}:{port}/unified-shell.html?v={int(time.time())}"
    print("=" * 64)
    print("Prisma Cloud Center")
    print(f"Local cockpit: {url}")
    print(f"Protected current Control Center: {protected_current}")
    print("No toca 3150. Prisma Cloud Center corre en 3160. Cloud SaaS y licencias viven dentro de la consola.")
    print("=" * 64)
    if open_browser:
        webbrowser.open(url)


def self_test(lab_root: Path, protected_current: Path, out_dir: Path) -> int:
    failures: List[str] = []
    required = [
        lab_root / "00_ABRIR_PRISMA_CLOUD_CTR.cmd",
        lab_root / "01_SELF_TEST_PRISMA_CLOUD_CTR.cmd",
        lab_root / "02_EXPORT_DIAGNOSTICS_PRISMA_CLOUD_CTR.cmd",
        lab_root / "00_ABRIR_UNIFIED_SHELL_LAB_V3.cmd",
        lab_root / "01_SELF_TEST_LAB_V3.cmd",
        lab_root / "02_EXPORT_DIAGNOSTICS_LAB_V3.cmd",
        lab_root / "README.md",
        lab_root / "MANUAL.md",
        lab_root / "RUNBOOK.md",
        lab_root / "ARCHITECTURE.md",
        lab_root / "SECURITY.md",
        lab_root / "TROUBLESHOOTING.md",
        lab_root / "CHANGELOG.md",
        lab_root / "internal" / "py" / "prisma_unified_lab_v3.py",
        lab_root / "internal" / "py" / "cloud_saas_api.py",
        lab_root / "internal" / "py" / "license_ops_api.py",
        lab_root / "internal" / "py" / "licflow4_admin_bridge.py",
        lab_root / "internal" / "py" / "support_resolver_api.py",
        lab_root / "internal" / "web" / "cloud_command_center.html",
        lab_root / "internal" / "web" / "cloud_command_center.js",
        lab_root / "internal" / "web" / "cloud_command_center.css",
        lab_root / "internal" / "web" / "assets" / "simon-spring-zmMrlEHsFQY-unsplash.jpg",
        lab_root / "internal" / "web" / "assets" / "prisma-logo-mark.png",
        lab_root / "internal" / "web" / "license_ops_console.js",
        lab_root / "internal" / "web" / "license_ops_console.css",
        lab_root / "internal" / "config" / "cloud_saas.json",
        lab_root / "internal" / "runtime" / "prisma-module-contract.json",
    ]
    write_contract_files(lab_root, protected_current, out_dir)
    for path in required:
        if not path.exists():
            failures.append(f"Missing: {path}")
    try:
        json.loads((lab_root / "internal" / "runtime" / "prisma-module-contract.json").read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"Contract JSON invalid: {exc}")
    try:
        bridge = licflow4_admin_bridge.bridge_payload("/api/licflow4/bridge/status", method="GET", local_request=True)
        if bridge.get("bridgeAvailable") is not True:
            failures.append("LICFLOW4 bridge status is not available")
        if not isinstance(bridge.get("adminTokenPresent"), bool):
            failures.append("LICFLOW4 bridge status does not expose adminTokenPresent as boolean")
        missing_confirmation = licflow4_admin_bridge.bridge_payload("/api/licflow4/bridge/activate", method="POST", body={}, local_request=True)
        if missing_confirmation.get("code") != "ADMIN_ACTION_CONFIRMATION_REQUIRED":
            failures.append("LICFLOW4 activate does not require explicit confirmation")
        revoke_missing_phrase = licflow4_admin_bridge.bridge_payload("/api/licflow4/bridge/revoke", method="POST", body={
            "confirmAdminLicenseAction": True,
            "licenseKey": "SELF-TEST-LICENSE",
            "deviceId": "SELF-TEST-DEVICE",
            "tenantId": "self-test-tenant",
            "reason": "self-test",
        }, local_request=True)
        if revoke_missing_phrase.get("code") != "REVOKE_CONFIRMATION_REQUIRED":
            failures.append("LICFLOW4 revoke does not require the revoke phrase")
        dry_run = licflow4_admin_bridge.bridge_payload("/api/licflow4/bridge/refresh", method="POST", body={
            "confirmAdminLicenseAction": True,
            "licenseKey": "SELF-TEST-LICENSE",
            "deviceId": "SELF-TEST-DEVICE",
            "tenantId": "self-test-tenant",
            "dryRun": True,
        }, local_request=True)
        if dry_run.get("code") != "DRY_RUN_READY" or dry_run.get("dryRun") is not True:
            failures.append("LICFLOW4 dry-run route did not stay non-mutating")
        ui_text = (lab_root / "internal" / "web" / "cloud_command_center.js").read_text(encoding="utf-8")
        for forbidden in ["X-Prisma-Admin-Token", "Authorization: Bearer", "x-admin-token", "localStorage.setItem('ADMIN_TOKEN", "wrangler deploy", "cloudflared tunnel"]:
            if forbidden in ui_text:
                failures.append(f"Forbidden frontend/admin operation token detected: {forbidden}")
    except Exception as exc:
        failures.append(f"LICFLOW4 self-test failed: {exc}")
    if str(lab_root).lower() == str(protected_current).lower():
        failures.append("LabRoot equals ProtectedCurrent")
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "health": health_snapshot(),
    }
    report = out_dir / f"PRISMA_CLOUD_CTR_SELF_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("SELF TEST:", result["status"])
    print("Report:", report)
    if failures:
        for failure in failures:
            print("-", failure)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", default=os.environ.get("PRISMA_LAB_ROOT", str(Path(__file__).resolve().parents[2])))
    parser.add_argument("--protected-current", default=os.environ.get("PRISMA_PROTECTED_CURRENT", DEFAULT_PROTECTED_CURRENT))
    parser.add_argument("--out-dir", default=os.environ.get("PRISMA_OUT_DIR", DEFAULT_OUT_DIR))
    parser.add_argument("--host", default=os.environ.get("PRISMA_LAB_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PRISMA_LAB_PORT", str(DEFAULT_PORT))))
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--export-diagnostics", action="store_true")
    args = parser.parse_args()

    lab_root = clean_path(args.lab_root)
    protected_current = clean_path(args.protected_current)
    out_dir = clean_path(args.out_dir)

    if str(lab_root).lower() == str(protected_current).lower():
        raise SystemExit("ERROR: LabRoot y ProtectedCurrent son iguales. Me niego a tocar la carpeta buena.")

    if args.self_test:
        return self_test(lab_root, protected_current, out_dir)
    if args.export_diagnostics:
        result = export_diagnostics(out_dir)
        print("Diagnostics JSON:", result["json"])
        print("Diagnostics TXT:", result["txt"])
        return 0
    if args.serve:
        serve(lab_root, protected_current, out_dir, args.host, args.port)
        return 0
    start(lab_root, protected_current, out_dir, args.host, args.port, not args.no_open)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
