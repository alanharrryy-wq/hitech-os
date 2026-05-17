from __future__ import annotations

import html
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config_loader import CONFIG_ROOT, LATEST_ROOT, LOG_ROOT, TEMPLATES_ROOT, active_health_profile, detect_lan_ip, ensure_log_dirs, load_cloudflare_config, load_state, save_state, write_json

# PRISMA_BLACKBOX_BRIDGE_V1_HELPER_BEGIN
def _prisma_emit_to_blackbox(payload: dict[str, Any], report_paths: dict[str, str]) -> dict[str, Any]:
    try:
        from blackbox_bridge import emit_control_center_report
        return emit_control_center_report(payload, report_paths)
    except Exception as exc:
        try:
            run_log = payload.get("runLog")
            if run_log:
                with open(run_log, "a", encoding="utf-8", newline="\n") as handle:
                    handle.write(f"[blackbox_bridge] WARN {exc}\n")
        except Exception:
            pass
        return {"ok": False, "error": str(exc)}
# PRISMA_BLACKBOX_BRIDGE_V1_HELPER_END


class RunLog:
    def __init__(self, action: str) -> None:
        ensure_log_dirs()
        self.action = action
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = LOG_ROOT / f"run_{self.run_id}.log"
        self.entries: list[dict[str, Any]] = []

    def log(self, event: str, detail: Any = "") -> None:
        stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        item = {"time": stamp, "event": event, "detail": detail}
        self.entries.append(item)
        line = f"[{stamp}] {event} {detail}\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)


def _service_weight(service: dict[str, Any]) -> int:
    criticality = str(service.get("criticality", "")).lower()
    if criticality == "critical":
        return 35
    if criticality == "high":
        return 25
    return 15


def compute_health_score(services: list[dict[str, Any]], cloudflare: dict[str, Any]) -> int:
    total = 0
    earned = 0
    for service in services:
        weight = _service_weight(service)
        total += weight
        if service.get("status") == "PASS":
            earned += weight
        elif service.get("status") == "DEGRADED":
            earned += weight // 2
    total += 20
    if cloudflare.get("status") == "PASS":
        earned += 20
    elif cloudflare.get("status") == "DEGRADED":
        earned += 10
    if total <= 0:
        return 0
    return max(0, min(100, round((earned / total) * 100)))


def compute_overall_status(services: list[dict[str, Any]], cloudflare: dict[str, Any]) -> str:
    if any(service.get("status") == "BLOCKED" for service in services):
        return "BLOCKED"
    required_fail = [
        service
        for service in services
        if service.get("requiredForLocal") and service.get("status") not in {"PASS", "DEGRADED"}
    ]
    if required_fail:
        return "FAIL"
    if any(service.get("status") != "PASS" for service in services):
        return "DEGRADED"
    if cloudflare.get("status") == "FAIL":
        return "FAIL" if cloudflare.get("mode") == "required" else "DEGRADED"
    if cloudflare.get("status") == "DEGRADED":
        return "DEGRADED"
    return "PASS"


def recommended_next_action(overall: str, services: list[dict[str, Any]], cloudflare: dict[str, Any]) -> str:
    if overall == "PASS":
        return "Todo quedo arriba. Mantener monitoreo desde el panel 3150."
    blocked = [service for service in services if service.get("status") == "BLOCKED"]
    if blocked:
        names = ", ".join(f"{item.get('name')}:{item.get('port')}" for item in blocked)
        return f"Resolver proceso desconocido antes de reiniciar: {names}."
    failed = [service for service in services if service.get("status") == "FAIL"]
    if failed:
        names = ", ".join(f"{item.get('name')}:{item.get('port')}" for item in failed)
        return f"Revisar logs de arranque y dependencias locales para: {names}."
    if cloudflare.get("status") != "PASS":
        blocked_codes = {str(item.get("code", "")) for item in cloudflare.get("actionsBlocked", [])}
        if "CLOUDFLARED_SERVICE_RESTART_BLOCKED" in blocked_codes:
            return "Cloudflare esta degradado porque Windows bloqueo el reinicio de cloudflared. Reiniciar el servicio cloudflared como administrador y repetir health."
        if "CLOUDFLARED_SERVICE_START_BLOCKED" in blocked_codes:
            return "Cloudflare esta degradado porque Windows bloqueo el arranque de cloudflared. Iniciar el servicio cloudflared como administrador y repetir health."
        return "Cloudflare esta degradado. Revisar cloudflared, config.yml, DNS y endpoints publicos."
    return "Sistema degradado sin bloqueo critico. Revisar latencias y probes de contenido."


SENSITIVE_KEY_RE = re.compile(
    r"(?i)^(pid|process[_-]?id|command[_-]?line|cwd|executable[_-]?path|path[_-]?name|credentials|credentials[_-]?file|cert|token|secret|authorization|cookie|raw|rawpreview|stdout|stderr|command|args|log|runlog|logpath|logroot)$"
)
SENSITIVE_VALUE_RE = re.compile(
    r"(?i)([A-Z]:\\(?:Users\\[^\\\s]+|repos\\hitech-os|Windows|Program Files)[^\"'\n\r\t ]*|\\.env(?:\\b|[^A-Za-z0-9_])|token[=:][^\"'\s]+|secret[=:][^\"'\s]+|credentials-file:\\s*[^\\n\\r]+|authorization:\\s*[^\\n\\r]+|cookie:\\s*[^\\n\\r]+)"
)


def redact_public_text(value: str) -> str:
    text = str(value)
    text = SENSITIVE_VALUE_RE.sub("<redacted>", text)
    return text[:260]


def _public_safe_value(key: str, value: Any) -> Any:
    if SENSITIVE_KEY_RE.search(key):
        if isinstance(value, list):
            return f"<redacted:{len(value)} items>"
        if isinstance(value, dict):
            return "<redacted:object>"
        return "<redacted>"
    if isinstance(value, dict):
        return {k: _public_safe_value(k, v) for k, v in value.items() if not SENSITIVE_KEY_RE.search(k)}
    if isinstance(value, list):
        return [_public_safe_value(key, item) for item in value[:50]]
    if isinstance(value, str):
        return redact_public_text(value)
    return value


def _service_public_summary(service: dict[str, Any]) -> dict[str, Any]:
    owners = service.get("owners", [])
    unknown_count = sum(1 for owner in owners if owner.get("classification", {}).get("classification") == "UNKNOWN_PROCESS")
    return {
        "id": service.get("id"),
        "name": service.get("name"),
        "port": service.get("port"),
        "productRole": service.get("productRole"),
        "criticality": service.get("criticality"),
        "status": service.get("status"),
        "healthy": service.get("healthy"),
        "blocked": service.get("blocked"),
        "unknownProcessCount": unknown_count,
        "localHttp": {
            "ok": service.get("localHttp", {}).get("ok"),
            "statusCode": service.get("localHttp", {}).get("statusCode"),
            "latencyMs": service.get("localHttp", {}).get("latencyMs"),
        },
        "lanHttp": {
            "ok": service.get("lanHttp", {}).get("ok") if service.get("lanHttp") else None,
            "statusCode": service.get("lanHttp", {}).get("statusCode") if service.get("lanHttp") else None,
            "latencyMs": service.get("lanHttp", {}).get("latencyMs") if service.get("lanHttp") else None,
        },
        "publicHost": service.get("urls", {}).get("publicHost"),
    }


def _cloudflare_public_summary(cloudflare: dict[str, Any]) -> dict[str, Any]:
    config = cloudflare.get("config", {})
    endpoints = []
    for endpoint in cloudflare.get("publicEndpoints", []):
        endpoints.append(
            {
                "id": endpoint.get("id"),
                "name": endpoint.get("name"),
                "url": endpoint.get("url"),
                "required": endpoint.get("required", False),
                "securityMode": endpoint.get("securityMode"),
                "probe": {
                    "ok": endpoint.get("probe", {}).get("ok"),
                    "statusCode": endpoint.get("probe", {}).get("statusCode"),
                    "latencyMs": endpoint.get("probe", {}).get("latencyMs"),
                    "contentProbe": endpoint.get("probe", {}).get("contentProbe"),
                    "error": redact_public_text(endpoint.get("probe", {}).get("error", "")),
                },
            }
        )
    return {
        "status": cloudflare.get("status"),
        "mode": cloudflare.get("mode"),
        "service": {
            "found": cloudflare.get("service", {}).get("found"),
            "status": cloudflare.get("service", {}).get("status"),
        },
        "config": {
            "exists": config.get("exists"),
            "drift": [redact_public_text(item) for item in config.get("drift", [])],
            "fallback404": config.get("fallback404"),
            "fallback404AtEnd": config.get("fallback404AtEnd"),
            "duplicateRoutes": config.get("duplicateRoutes", []),
            "controlRoute": config.get("controlRoute", {}),
        },
        "dnsRoutes": [
            {
                "hostname": item.get("hostname"),
                "ok": item.get("ok"),
                "returnCode": item.get("returnCode"),
                "summary": "DNS route resolved" if item.get("ok") else "DNS route missing or unavailable",
            }
            for item in cloudflare.get("dnsRoutes", [])
        ],
        "publicEndpoints": endpoints,
        "origins": [
            {
                "serviceId": origin.get("serviceId"),
                "hostname": origin.get("hostname"),
                "originPort": str(origin.get("origin", "")).rsplit(":", 1)[-1],
            }
            for origin in cloudflare.get("origins", [])
        ],
    }


def sanitize_for_public(payload: dict[str, Any]) -> dict[str, Any]:
    services = [_service_public_summary(service) for service in payload.get("services", [])]
    cloudflare = _cloudflare_public_summary(payload.get("cloudflare", {}))
    control = payload.get("control_center", {})
    public = {
        "schemaVersion": payload.get("schemaVersion", "1.0"),
        "runId": payload.get("runId"),
        "generatedAt": payload.get("generatedAt"),
        "lastUpdated": payload.get("generatedAt"),
        "safetyMode": "PUBLIC_REDACTED",
        "overallStatus": payload.get("overallStatus"),
        "healthScore": payload.get("healthScore"),
        "recommendedNextAction": redact_public_text(payload.get("recommendedNextAction", "")),
        "recommendations": [redact_public_text(payload.get("recommendedNextAction", ""))],
        "services": services,
        "cloudflare": cloudflare,
        "actionsBlockedSummary": {
            "count": len(payload.get("actionsBlocked", [])),
            "unknownProcessBlocks": sum(1 for service in services if service.get("unknownProcessCount")),
        },
        "security": {
            "mode": "PUBLIC_REDACTED",
            "readOnly": True,
            "advancedAuth": False,
            "redactedFields": [
                "process identifiers",
                "process launch details",
                "working directories",
                "local filesystem paths",
                "credential material",
                "auth material",
                "raw logs",
                "raw command output",
            ],
            "publicWarning": "Public panel is read-only and sanitized. No destructive actions are exposed.",
        },
        "control_center": {
            "public_url": control.get("public_url") or control.get("publicUrl") or "https://control.hitechrts.com/",
            "public_mode": "PUBLIC_REDACTED",
            "status": payload.get("overallStatus"),
            "health_score": payload.get("healthScore"),
            "last_updated": payload.get("generatedAt"),
            "services_summary": services,
            "cloudflare_summary": cloudflare,
            "recommendations": [redact_public_text(payload.get("recommendedNextAction", ""))],
        },
    }
    return _public_safe_value("root", public)


def public_payload_has_sensitive_data(payload: dict[str, Any]) -> dict[str, Any]:
    raw = html.unescape(str(payload))
    patterns = [
        r"(?i)\bpid\b\s*[:=]",
        r"(?i)commandLine",
        r"(?i)executablePath",
        r"(?i)\bcwd\b",
        r"(?i)C:\\Users\\",
        r"(?i)F:\\repos\\hitech-os\\",
        r"(?i)\.env",
        r"(?i)credentials-file",
        r"(?i)token",
        r"(?i)secret",
        r"(?i)authorization",
        r"(?i)cookie",
    ]
    hits = [pattern for pattern in patterns if re.search(pattern, raw)]
    return {"safe": not hits, "hits": hits}


def _services_text(services: list[dict[str, Any]]) -> str:
    lines = []
    for item in services:
        owner_bits = []
        for owner in item.get("owners", []):
            cls = owner.get("classification", {})
            owner_bits.append(f"PID={owner.get('pid')} {owner.get('processName')} {cls.get('classification')}")
        owners = "; ".join(owner_bits) if owner_bits else "no owner"
        local = item.get("localHttp", {})
        lines.append(
            f"- {item.get('name')} {item.get('port')} status={item.get('status')} "
            f"http={local.get('statusCode')} latencyMs={local.get('latencyMs')} owners={owners}"
        )
    return "\n".join(lines) if lines else "- No services"


def _services_html(services: list[dict[str, Any]]) -> str:
    rows = []
    for item in services:
        local = item.get("localHttp", {})
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('port')))}</td>"
            f"<td>{html.escape(str(item.get('name')))}</td>"
            f"<td>{html.escape(str(item.get('status')))}</td>"
            f"<td>{html.escape(str(local.get('statusCode')))}</td>"
            f"<td>{html.escape(str(local.get('latencyMs')))}</td>"
            "</tr>"
        )
    return "<table><tr><th>Puerto</th><th>Servicio</th><th>Estado</th><th>HTTP</th><th>ms</th></tr>" + "".join(rows) + "</table>"


def _cloudflare_text(cloudflare: dict[str, Any]) -> str:
    service = cloudflare.get("service", {})
    cfg = cloudflare.get("config", {})
    endpoints = cloudflare.get("publicEndpoints", [])
    public = ", ".join(f"{ep.get('name')}={ep.get('probe', {}).get('ok')}" for ep in endpoints)
    return (
        f"status={cloudflare.get('status')} mode={cloudflare.get('mode')} "
        f"service={service.get('status')} configExists={cfg.get('exists')} "
        f"drift={cfg.get('drift')} fallbackAtEnd={cfg.get('fallback404AtEnd')} public=[{public}]"
    )


def _cloudflare_html(cloudflare: dict[str, Any]) -> str:
    rows = [
        ("Estado", cloudflare.get("status")),
        ("Modo", cloudflare.get("mode")),
        ("Servicio Windows", cloudflare.get("service", {}).get("status")),
        ("Config", cloudflare.get("config", {}).get("path")),
        ("Drift", ", ".join(cloudflare.get("config", {}).get("drift", [])) or "OK"),
    ]
    body = "".join(f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k, v in rows)
    return "<table>" + body + "</table>"


def _render_template(name: str, replacements: dict[str, str]) -> str:
    raw = (TEMPLATES_ROOT / name).read_text(encoding="utf-8")
    for key, value in replacements.items():
        raw = raw.replace("{{" + key + "}}", value)
    return raw


def write_reports(
    action: str,
    services: list[dict[str, Any]],
    cloudflare: dict[str, Any],
    run_log: RunLog,
    assumptions: list[str] | None = None,
    commands_executed: list[Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, str]:
    ensure_log_dirs()
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    timeline = list(run_log.entries)
    actions_taken = []
    actions_blocked = []
    for service in services:
        actions_taken.extend(service.get("actionsTaken", []))
        actions_blocked.extend(service.get("actionsBlocked", []))
    actions_taken.extend(cloudflare.get("actionsTaken", []))
    actions_blocked.extend(cloudflare.get("actionsBlocked", []))
    score = compute_health_score(services, cloudflare)
    overall = compute_overall_status(services, cloudflare)
    next_action = recommended_next_action(overall, services, cloudflare)
    state = load_state()
    cloudflare_cfg = load_cloudflare_config()
    control_cfg = cloudflare_cfg.get("controlCenter", {})
    control_center = {
        "local_url": control_cfg.get("localUrl", "http://127.0.0.1:3150/"),
        "public_url": control_cfg.get("publicUrl", "https://control.hitechrts.com/"),
        "local_mode": control_cfg.get("localMode", "LOCAL_FULL"),
        "public_mode": control_cfg.get("publicMode", "PUBLIC_REDACTED"),
        "local_health": cloudflare.get("controlCenter", {}).get("localHealth", {}),
        "public_health": cloudflare.get("controlCenter", {}).get("publicHealth", {}),
        "public_mode_probe": cloudflare.get("controlCenter", {}).get("publicModeProbe", {}),
        "public_sanitized_report_path": str(LATEST_ROOT / "public-health.json"),
    }
    payload: dict[str, Any] = {
        "schemaVersion": "1.0",
        "runId": run_log.run_id,
        "generatedAt": generated_at,
        "action": action,
        "profile": active_health_profile().get("name", "standard"),
        "lanIp": detect_lan_ip(),
        "overallStatus": overall,
        "healthScore": score,
        "recommendedNextAction": next_action,
        "services": services,
        "cloudflare": cloudflare,
        "control_center": control_center,
        "actionsTaken": actions_taken,
        "actionsBlocked": actions_blocked,
        "timeline": timeline,
        "commandsExecuted": commands_executed or [],
        "assumptions": assumptions or [],
        "lastGoodHealth": state.get("lastGoodHealth"),
        "logRoot": str(LOG_ROOT),
        "runLog": str(run_log.path),
    }
    if extra:
        payload.update(extra)
    json_path = LOG_ROOT / f"health_{run_log.run_id}.json"
    txt_path = LOG_ROOT / f"health_{run_log.run_id}.txt"
    html_path = LOG_ROOT / f"health_{run_log.run_id}.html"
    public_json_path = LOG_ROOT / f"public-health_{run_log.run_id}.json"
    write_json(json_path, payload)
    public_payload = sanitize_for_public(payload)
    write_json(public_json_path, public_payload)
    services_text = _services_text(services)
    cloudflare_text = _cloudflare_text(cloudflare)
    control_text = (
        f"local={control_center['local_url']} mode={control_center['local_mode']} "
        f"public={control_center['public_url']} mode={control_center['public_mode']} "
        f"localOk={control_center.get('local_health', {}).get('ok')} "
        f"publicOk={control_center.get('public_health', {}).get('ok')} "
        f"publicSanitized={control_center.get('public_mode_probe', {}).get('safe')}"
    )
    action_lines = "\n".join([f"- {x}" for x in actions_taken]) or "- None"
    blocked_lines = "\n".join([f"- {x}" for x in actions_blocked]) or "- None"
    txt = _render_template(
        "report.txt",
        {
            "run_id": run_log.run_id,
            "generated_at": generated_at,
            "action": action,
            "overall_status": overall,
            "health_score": str(score),
            "recommended_next_action": next_action,
            "services_text": services_text,
            "cloudflare_text": cloudflare_text,
            "control_center_text": control_text,
            "actions_taken": action_lines,
            "actions_blocked": blocked_lines,
            "logs_text": str(run_log.path),
        },
    )
    txt_path.write_text(txt, encoding="utf-8", newline="\n")
    html_report = _render_template(
        "report.html",
        {
            "overall_status": html.escape(overall),
            "health_score": html.escape(str(score)),
            "generated_at": html.escape(generated_at),
            "action": html.escape(action),
            "services_html": _services_html(services),
            "cloudflare_html": _cloudflare_html(cloudflare),
            "control_center_text": html.escape(control_text),
            "actions_text": html.escape(f"Taken:\n{action_lines}\n\nBlocked:\n{blocked_lines}"),
            "recommended_next_action": html.escape(next_action),
        },
    )
    html_path.write_text(html_report, encoding="utf-8", newline="\n")
    shutil.copyfile(json_path, LATEST_ROOT / "health.json")
    shutil.copyfile(public_json_path, LATEST_ROOT / "public-health.json")
    shutil.copyfile(txt_path, LATEST_ROOT / "health.txt")
    shutil.copyfile(html_path, LATEST_ROOT / "health.html")
    # PRISMA_BLACKBOX_BRIDGE_V1_CALL_BEGIN
    _prisma_blackbox_bridge = _prisma_emit_to_blackbox(
        payload,
        {
            "json": str(json_path),
            "txt": str(txt_path),
            "html": str(html_path),
            "publicJson": str(public_json_path),
            "latestJson": str(LATEST_ROOT / "health.json"),
            "latestPublicJson": str(LATEST_ROOT / "public-health.json"),
            "latestTxt": str(LATEST_ROOT / "health.txt"),
            "latestHtml": str(LATEST_ROOT / "health.html"),
            "runLog": str(run_log.path),
        },
    )
    # PRISMA_BLACKBOX_BRIDGE_V1_CALL_END
    if overall == "PASS":
        state["lastGoodHealth"] = {
            "runId": run_log.run_id,
            "generatedAt": generated_at,
            "healthScore": score,
            "summary": [{"id": s.get("id"), "status": s.get("status")} for s in services],
        }
        save_state(state)
    return {
        "json": str(json_path),
        "txt": str(txt_path),
        "html": str(html_path),
        "publicJson": str(public_json_path),
        "latestJson": str(LATEST_ROOT / "health.json"),
        "latestPublicJson": str(LATEST_ROOT / "public-health.json"),
        "latestTxt": str(LATEST_ROOT / "health.txt"),
        "latestHtml": str(LATEST_ROOT / "health.html"),
        "runLog": str(run_log.path),
    }


SECRET_PATTERNS = [
    re.compile(r"(?i)(token|secret|credential|password|api[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"(?i)(cert|key-file|origincert)\s*[:=]\s*['\"]?[^'\"\s]+"),
]


def sanitize_text(text: str) -> str:
    clean = text
    for pattern in SECRET_PATTERNS:
        clean = pattern.sub(lambda match: match.group(0).split(match.group(1), 1)[0] + match.group(1) + "=<redacted>", clean)
    return clean


def export_support_bundle() -> dict[str, Any]:
    ensure_log_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle = LOG_ROOT / f"prisma_control_center_support_{stamp}.zip"
    include_paths: list[Path] = []
    include_paths.extend(sorted(LATEST_ROOT.glob("health.*")))
    include_paths.extend(sorted(LATEST_ROOT.glob("public-health.*")))
    include_paths.extend(sorted(LOG_ROOT.glob("health_*.json"))[-5:])
    include_paths.extend(sorted(LOG_ROOT.glob("public-health_*.json"))[-5:])
    include_paths.extend(sorted(LOG_ROOT.glob("health_*.txt"))[-5:])
    include_paths.extend(sorted(LOG_ROOT.glob("health_*.html"))[-5:])
    include_paths.extend(sorted(LOG_ROOT.glob("run_*.log"))[-8:])
    include_paths.extend(sorted(CONFIG_ROOT.glob("*.json")))
    state_path = LOG_ROOT / "state.json"
    if state_path.exists():
        include_paths.append(state_path)

    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in include_paths:
            if not path.exists() or path.is_dir():
                continue
            lowered = str(path).lower()
            if ".env" in lowered or "credential" in lowered or "token" in lowered:
                continue
            try:
                raw = path.read_text(encoding="utf-8", errors="ignore")
                data = sanitize_text(raw).encode("utf-8")
                archive.writestr(path.name if path.parent == LOG_ROOT else str(path.relative_to(path.parents[1])), data)
            except Exception:
                continue
    return {"bundle": str(bundle), "filesConsidered": len(include_paths)}
