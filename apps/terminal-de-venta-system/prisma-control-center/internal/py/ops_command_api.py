
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

try:
    from blackbox_bridge import blackbox_root, ensure_dirs
except Exception:
    blackbox_root = None
    ensure_dirs = None

SOURCE = "prisma-ops-command-api"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _control_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _logs_root() -> Path:
    return _control_root().parents[2] / "tools" / "_local" / "logs" / "prisma-control-center"


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


def _read_text(path: Path, fallback: str = "") -> str:
    try:
        if not path.exists():
            return fallback
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return fallback


def _path_status(path: Path, public: bool = False) -> dict[str, Any]:
    return {
        "path": "<redacted>" if public else str(path),
        "exists": path.exists(),
        "isFile": path.is_file(),
        "isDir": path.is_dir(),
        "size": path.stat().st_size if path.exists() and path.is_file() else None,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if path.exists() else None,
    }


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            low = str(k).lower()
            if any(t in low for t in ["path", "root", "log", "command", "cmd", "pid", "process", "token", "secret", "stdout", "stderr"]):
                out[k] = "<redacted>"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(value, str) and (":\\" in value or ":/" in value):
        return "<redacted>"
    return value


def _latest_health() -> dict[str, Any]:
    root = _blackbox_root()
    latest = _read_json(root / "runtime" / "control_center_latest.json", {})
    if isinstance(latest, dict) and latest:
        return latest
    return _read_json(_logs_root() / "latest" / "health.json", {})


def _latest_bridge() -> dict[str, Any]:
    return _read_json(_blackbox_root() / "runtime" / "control_center_bridge_latest.json", {})


def _active_incidents() -> list[dict[str, Any]]:
    active_root = _blackbox_root() / "incidents" / "active"
    out = []
    if not active_root.exists():
        return out
    for item in sorted(active_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if item.is_dir() and item.name.startswith("INC_CC_"):
            incident = _read_json(item / "incident.json", {})
            if isinstance(incident, dict):
                incident.setdefault("id", item.name)
                out.append(incident)
    return out


def _public_endpoints(health: dict[str, Any]) -> list[dict[str, Any]]:
    cf = health.get("cloudflare", {}) if isinstance(health, dict) else {}
    endpoints = cf.get("publicEndpoints") or cf.get("endpoints") or []
    if not isinstance(endpoints, list):
        endpoints = []
    control_url = (health.get("control_center", {}) or {}).get("public_url") or "https://control.hitechrts.com/"
    has_control = any("control.hitechrts.com" in str(e.get("url") or e.get("name") or "") for e in endpoints if isinstance(e, dict))
    if not has_control:
        public_health = (health.get("control_center", {}) or {}).get("public_health", {}) or {}
        endpoints.insert(0, {
            "name": "control.hitechrts.com",
            "url": control_url,
            "probe": public_health,
        })
    return endpoints


def _cloudflare_status(health: dict[str, Any]) -> str:
    cf = health.get("cloudflare", {}) if isinstance(health, dict) else {}
    raw = str(cf.get("status") or (health.get("control_center", {}) or {}).get("cloudflare") or "UNKNOWN").upper()
    for endpoint in _public_endpoints(health):
        if not isinstance(endpoint, dict):
            continue
        if "control.hitechrts.com" in str(endpoint.get("url") or endpoint.get("name") or ""):
            probe = endpoint.get("probe") or {}
            if probe.get("ok") is True:
                return "PASS"
            code = str(probe.get("statusCode") or probe.get("status") or "")
            if code == "404":
                return "DEGRADED"
    return raw


def _cloudflare_payload(public: bool) -> dict[str, Any]:
    health = _latest_health()
    latest_bridge = _latest_bridge()
    incidents = _active_incidents()
    status = _cloudflare_status(health)
    endpoints = _public_endpoints(health)
    logs_root = _logs_root()
    latest = logs_root / "latest"
    diagnosis = []
    if status != "PASS":
        diagnosis.extend([
            "Validar que cloudflared este corriendo",
            "Revisar config.yml y hostname control.hitechrts.com",
            "Verificar que el service apunte al puerto 3150 correcto",
            "Confirmar DNS / CNAME en Cloudflare",
            "Correr health despues del ajuste para cerrar incidente",
        ])
    else:
        diagnosis.append("Ruta publica visible. Si hay incidente activo, correr health para resolverlo.")
    payload = {
        "schemaVersion": "1.0",
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "status": status,
        "healthScore": health.get("healthScore") if isinstance(health, dict) else None,
        "overallStatus": health.get("overallStatus") if isinstance(health, dict) else None,
        "latestBridge": latest_bridge,
        "activeIncidentCount": len(incidents),
        "activeIncidents": incidents[:5],
        "endpoints": endpoints,
        "diagnosis": diagnosis,
        "latestReport": {
            "html": _path_status(latest / "health.html", public),
            "json": _path_status(latest / "health.json", public),
            "txt": _path_status(latest / "health.txt", public),
            "publicJson": _path_status(latest / "public-health.json", public),
        },
        "actions": {
            "runHealth": {"method": "GET", "url": "/api/ops/action/run-health", "localOnly": True},
            "latestReport": {"method": "GET", "url": "/latest/health.html", "localOnly": False},
            "operatorBrief": {"method": "GET", "url": "/api/ops/operator-brief", "localOnly": False},
        },
    }
    return _redact(payload) if public else payload


def _latest_report(public: bool) -> dict[str, Any]:
    latest = _logs_root() / "latest"
    payload = {
        "schemaVersion": "1.0",
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "files": {
            "html": _path_status(latest / "health.html", public),
            "json": _path_status(latest / "health.json", public),
            "txt": _path_status(latest / "health.txt", public),
            "publicJson": _path_status(latest / "public-health.json", public),
        },
        "summary": _redact(_latest_health()) if public else _latest_health(),
    }
    return payload


def _operator_brief(public: bool) -> dict[str, Any]:
    health = _latest_health()
    cf = _cloudflare_payload(public=False)
    latest_bridge = _latest_bridge()
    incidents = _active_incidents()
    lines = [
        "PRISMA Operator Brief",
        f"Time: {_now()}",
        f"Overall: {health.get('overallStatus') if isinstance(health, dict) else 'UNKNOWN'}",
        f"HealthScore: {health.get('healthScore') if isinstance(health, dict) else '-'}",
        f"Cloudflare: {cf.get('status')}",
        f"ActiveIncidents: {len(incidents)}",
        f"LatestBridge: {latest_bridge.get('status') if isinstance(latest_bridge, dict) else '-'} / {latest_bridge.get('severity') if isinstance(latest_bridge, dict) else '-'}",
        "NextAction: " + str((health.get('recommendedNextAction') if isinstance(health, dict) else None) or (incidents[0].get('recommendedNextAction') if incidents else 'Sin accion inmediata')),
    ]
    payload = {
        "schemaVersion": "1.0",
        "source": SOURCE,
        "time": _now(),
        "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL",
        "briefText": "\n".join(lines),
        "cloudflareDiagnosis": cf.get("diagnosis", []),
        "incidentIds": [item.get("id") for item in incidents],
    }
    return _redact(payload) if public else payload


def _run_health(public: bool) -> dict[str, Any]:
    if public:
        return {"ok": False, "status": "FORBIDDEN", "reason": "run-health is local-only", "source": SOURCE}
    root = _control_root()
    script = root / "internal" / "py" / "prisma_control_center.py"
    out_dir = _logs_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    action_log = out_dir / f"ops_action_run_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PRISMA_CONTROL_CENTER"] = "1"
    started = _now()
    try:
        completed = subprocess.run(
            [sys.executable, str(script), "health"],
            cwd=str(root),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
        )
        action_log.write_text(
            "COMMAND: " + " ".join([sys.executable, str(script), "health"]) + "\n" +
            "RETURN_CODE: " + str(completed.returncode) + "\n\n" +
            "STDOUT:\n" + completed.stdout + "\n\n" +
            "STDERR:\n" + completed.stderr + "\n",
            encoding="utf-8",
            newline="\n",
        )
        ok = completed.returncode in [0, 1, 2, 3]
        return {
            "ok": ok,
            "source": SOURCE,
            "action": "run-health",
            "startedAt": started,
            "finishedAt": _now(),
            "returnCode": completed.returncode,
            "stdoutSample": completed.stdout[-2000:],
            "stderrSample": completed.stderr[-1200:],
            "log": str(action_log),
            "latest": _cloudflare_payload(public=False),
        }
    except Exception as exc:
        return {"ok": False, "source": SOURCE, "action": "run-health", "error": str(exc), "log": str(action_log)}



# PRISMA_V25_BUTTON_ACTIONS_BEGIN
ACTION_WRAPPERS: dict[str, dict[str, Any]] = {
    "local": {"label": "Levantar local", "wrapper": "local_up.ps1", "mode": "spawn"},
    "cloudflare": {"label": "Levantar Cloudflare", "wrapper": "cloudflare_up.ps1", "mode": "spawn"},
    "all": {"label": "Levantar todo", "wrapper": "all_up.ps1", "mode": "spawn"},
    "web-control": {"label": "Web Control", "wrapper": "web_control_local.ps1", "mode": "spawn"},
    "web-control-cloudflare": {"label": "Web + Cloudflare", "wrapper": "web_control_cloudflare.ps1", "mode": "spawn"},
    "chart-lab": {"label": "Chart Lab", "wrapper": "chart_lab_local.ps1", "mode": "spawn"},
    "diagnose": {"label": "Diagnostico", "wrapper": "health.ps1", "mode": "spawn"},
    "panel": {"label": "Reabrir panel", "wrapper": "panel_3150.ps1", "mode": "spawn"},
    "kill": {"label": "Kill PRISMA", "wrapper": "kill_everything.ps1", "mode": "spawn", "danger": True},
}


def _powershell_executable() -> str:
    for candidate in ["pwsh.exe", "powershell.exe", "pwsh", "powershell"]:
        try:
            probe = subprocess.run(
                [candidate, "-NoLogo", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=6,
            )
            if probe.returncode == 0:
                return candidate
        except Exception:
            continue
    return "powershell.exe"


def _run_wrapper_action(action: str, public: bool) -> dict[str, Any]:
    if public:
        return {"ok": False, "status": "FORBIDDEN", "reason": "launcher actions are local-only", "source": SOURCE, "action": action}
    spec = ACTION_WRAPPERS.get(action)
    if not spec:
        return {
            "ok": False,
            "status": "UNKNOWN_ACTION",
            "source": SOURCE,
            "action": action,
            "availableActions": sorted(ACTION_WRAPPERS.keys()),
        }
    root = _control_root()
    wrapper = root / "internal" / "wrappers" / str(spec["wrapper"])
    out_dir = _logs_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    action_log = out_dir / f"ops_button_{action}_{stamp}.log"
    if not wrapper.exists():
        return {"ok": False, "status": "WRAPPER_MISSING", "source": SOURCE, "action": action, "wrapper": str(wrapper)}
    ps = _powershell_executable()
    cmd = [ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(wrapper)]
    try:
        with action_log.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write("PRISMA Control Center V25 button action\n")
            fh.write(f"ACTION: {action}\n")
            fh.write(f"LABEL: {spec.get('label')}\n")
            fh.write("COMMAND: " + " ".join(cmd) + "\n")
            fh.write(f"STARTED: {_now()}\n\n")
            proc = subprocess.Popen(
                cmd,
                cwd=str(root),
                stdout=fh,
                stderr=subprocess.STDOUT,
                text=True,
            )
        return {
            "ok": True,
            "status": "STARTED",
            "source": SOURCE,
            "action": action,
            "label": spec.get("label"),
            "pid": proc.pid,
            "log": str(action_log),
            "startedAt": _now(),
            "note": "Launcher started asynchronously; check log/ZIP evidence for completion.",
        }
    except Exception as exc:
        return {"ok": False, "status": "START_FAILED", "source": SOURCE, "action": action, "error": str(exc), "log": str(action_log)}


def _actions_payload(public: bool) -> dict[str, Any]:
    actions = []
    for key, spec in ACTION_WRAPPERS.items():
        actions.append({
            "id": key,
            "label": spec.get("label"),
            "url": f"/api/ops/action/{key}",
            "localOnly": True,
            "danger": bool(spec.get("danger")),
        })
    return {"ok": True, "schemaVersion": "1.0", "source": SOURCE, "time": _now(), "safetyMode": "PUBLIC_REDACTED" if public else "LOCAL_FULL", "actions": actions}
# PRISMA_V25_BUTTON_ACTIONS_END

def ops_command_payload(path_text: str, public: bool = False) -> dict[str, Any]:
    parsed = urlparse(path_text)
    path = parsed.path.rstrip("/") or "/api/ops/cloudflare"
    _ = parse_qs(parsed.query)
    if path == "/api/ops/latest-report":
        return _latest_report(public=public)
    if path == "/api/ops/operator-brief":
        return _operator_brief(public=public)
    if path == "/api/ops/actions":
        return _actions_payload(public=public)
    if path == "/api/ops/action/run-health":
        return _run_health(public=public)
    if path.startswith("/api/ops/action/"):
        action = path.rsplit("/", 1)[-1].strip().lower()
        return _run_wrapper_action(action, public=public)
    return _cloudflare_payload(public=public)
