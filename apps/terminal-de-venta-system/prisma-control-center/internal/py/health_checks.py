from __future__ import annotations

import json
import shutil
import socket
import ssl
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from config_loader import CONTROL_CENTER_PORT, LATEST_ROOT, active_health_profile, detect_lan_ip, load_cloudflare_config
from ports_inspector import command_exists, inspect_port
from process_classifier import classify_owners
from safe_actions import run_command_capture
from services_registry import ServiceDef


def _probe_match(body: str, probe: dict[str, Any] | None) -> dict[str, Any]:
    if not probe:
        return {"configured": False, "matched": True, "mode": "none", "needles": [], "matches": []}
    needles = [str(item) for item in probe.get("needles", [])]
    mode = str(probe.get("mode", "any")).lower()
    lower = body.lower()
    matches = [needle for needle in needles if needle.lower() in lower]
    if not needles:
        matched = True
    elif mode == "all":
        matched = len(matches) == len(needles)
    else:
        matched = bool(matches)
    return {
        "configured": bool(needles),
        "matched": matched,
        "mode": mode,
        "needles": needles,
        "matches": matches,
    }


def http_probe(url: str, probe: dict[str, Any] | None = None, timeout: float | None = None, public: bool = False) -> dict[str, Any]:
    profile = active_health_profile()
    timeout = timeout if timeout is not None else float(profile.get("publicHttpTimeoutSeconds" if public else "httpTimeoutSeconds", 8))
    max_bytes = int(profile.get("contentProbeMaxBytes", 262144))
    start = time.perf_counter()
    result = {
        "url": url,
        "ok": False,
        "statusCode": None,
        "latencyMs": None,
        "error": "",
        "contentProbe": _probe_match("", probe),
        "bytesRead": 0,
    }
    request = urllib.request.Request(url, headers={"User-Agent": "PRISMA-Control-Center/1.0"})
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            data = response.read(max_bytes)
            status = int(getattr(response, "status", 0) or response.getcode())
            body = data.decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        data = exc.read(max_bytes)
        status = int(exc.code)
        body = data.decode("utf-8", errors="ignore")
        result["error"] = str(exc)
    except Exception as exc:  # noqa: BLE001 - diagnostics must capture broad endpoint failures.
        result["latencyMs"] = round((time.perf_counter() - start) * 1000, 2)
        result["error"] = str(exc)
        return result

    result["latencyMs"] = round((time.perf_counter() - start) * 1000, 2)
    result["statusCode"] = status
    result["bytesRead"] = len(data)
    result["contentProbe"] = _probe_match(body, probe)
    healthy_statuses = set(int(x) for x in profile.get("healthyHttpStatuses", [200]))
    result["ok"] = status in healthy_statuses and bool(result["contentProbe"]["matched"])
    return result


def http_probe_stable(url: str, probe: dict[str, Any] | None = None, public: bool = True) -> dict[str, Any]:
    profile = active_health_profile()
    attempts = max(1, int(profile.get("publicProbeAttempts", 3)))
    interval = max(0.0, float(profile.get("publicProbeIntervalSeconds", 0.75)))
    samples = []
    for index in range(attempts):
        sample = http_probe(url, probe, public=public)
        sample["attempt"] = index + 1
        samples.append(sample)
        if index < attempts - 1 and interval:
            time.sleep(interval)
    base = dict(samples[-1] if samples else http_probe(url, probe, public=public))
    ok_count = sum(1 for item in samples if item.get("ok"))
    status_codes = [item.get("statusCode") for item in samples]
    failures = [item for item in samples if not item.get("ok")]
    latencies = [item.get("latencyMs") for item in samples if isinstance(item.get("latencyMs"), (int, float))]
    base["ok"] = bool(samples) and ok_count == len(samples)
    base["stable"] = base["ok"]
    base["attempts"] = len(samples)
    base["successCount"] = ok_count
    base["failureCount"] = len(samples) - ok_count
    base["statusCodes"] = status_codes
    base["latencyMsAvg"] = round(sum(latencies) / len(latencies), 2) if latencies else None
    base["samples"] = [
        {
            "attempt": item.get("attempt"),
            "ok": item.get("ok"),
            "statusCode": item.get("statusCode"),
            "latencyMs": item.get("latencyMs"),
            "bytesRead": item.get("bytesRead"),
            "error": item.get("error", ""),
        }
        for item in samples
    ]
    if failures:
        base["error"] = failures[0].get("error") or f"PUBLIC_PROBE_UNSTABLE statusCodes={status_codes}"
    return base


def _probe_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    probe_path = path.strip() or "/"
    if probe_path == "/":
        return base + "/"
    return base + "/" + probe_path.lstrip("/")


def _service_probe_url(service: ServiceDef, path: str | None = None) -> str:
    return _probe_url(service.local_url, path if path is not None else service.health_path)


def http_probe_with_headers(url: str, headers: dict[str, str], probe: dict[str, Any] | None = None, timeout: float | None = None) -> dict[str, Any]:
    profile = active_health_profile()
    timeout = timeout if timeout is not None else float(profile.get("httpTimeoutSeconds", 8))
    max_bytes = int(profile.get("contentProbeMaxBytes", 262144))
    start = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": "PRISMA-Control-Center/1.0", **headers})
    result = {
        "url": url,
        "ok": False,
        "statusCode": None,
        "latencyMs": None,
        "error": "",
        "contentProbe": _probe_match("", probe),
        "bytesRead": 0,
        "bodyPreview": "",
    }
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(max_bytes)
            status = int(getattr(response, "status", 0) or response.getcode())
            body = data.decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        data = exc.read(max_bytes)
        status = int(exc.code)
        body = data.decode("utf-8", errors="ignore")
        result["error"] = str(exc)
    except Exception as exc:  # noqa: BLE001 - diagnostics must capture endpoint failures.
        result["latencyMs"] = round((time.perf_counter() - start) * 1000, 2)
        result["error"] = str(exc)
        return result
    result["latencyMs"] = round((time.perf_counter() - start) * 1000, 2)
    result["statusCode"] = status
    result["bytesRead"] = len(data)
    result["bodyPreview"] = body[:800]
    result["contentProbe"] = _probe_match(body, probe)
    result["ok"] = status in set(int(x) for x in profile.get("healthyHttpStatuses", [200])) and bool(result["contentProbe"]["matched"])
    return result


def check_service(service: ServiceDef, action: str = "health", include_lan: bool = True) -> dict[str, Any]:
    profile = active_health_profile()
    port_report = inspect_port(service.port)
    owners = classify_owners(port_report, action=action, service_id=service.id)
    local = http_probe(_service_probe_url(service), service.content_probe, timeout=float(profile.get("httpTimeoutSeconds", 8)))
    alternates = []
    if not local["ok"]:
        for path in service.alternate_health_paths:
            alternates.append(http_probe(_service_probe_url(service, path), service.content_probe, timeout=float(profile.get("httpTimeoutSeconds", 8))))
            if alternates[-1]["ok"]:
                local = alternates[-1]
                break
    if not local["ok"] and service.health_path != "/":
        alternates.append(http_probe(_service_probe_url(service, "/"), service.content_probe, timeout=float(profile.get("httpTimeoutSeconds", 8))))
        if alternates[-1]["ok"]:
            local = alternates[-1]
    lan_probe = None
    lan_ip = detect_lan_ip()
    if include_lan and service.lan_url and lan_ip != "127.0.0.1" and bool(profile.get("lanCheckEnabled", True)):
        lan_probe = http_probe(_probe_url(service.lan_url, service.health_path), service.content_probe, timeout=float(profile.get("httpTimeoutSeconds", 8)))
    service_status = "PASS" if local["ok"] else ("BLOCKED" if any(not o["classification"].get("recognized") for o in owners) else "FAIL")
    return {
        "id": service.id,
        "name": service.name,
        "port": service.port,
        "productRole": service.product_role,
        "criticality": service.criticality,
        "requiredForLocal": service.required_for_local,
        "requiredForCloudflare": service.required_for_cloudflare,
        "urls": {
            "local": service.local_url,
            "lan": service.lan_url,
            "publicHost": service.public_host,
        },
        "portCheck": port_report,
        "owners": owners,
        "localHttp": local,
        "alternateHttp": alternates,
        "lanHttp": lan_probe,
        "status": service_status,
        "blocked": service_status == "BLOCKED",
        "healthy": service_status == "PASS",
        "notes": service.notes,
    }


def _powershell_executable() -> str | None:
    for candidate in ["powershell.exe", "pwsh.exe", "powershell", "pwsh"]:
        found = shutil.which(candidate)
        if found:
            return found
    return None


def _powershell_json(script: str, timeout: int = 15) -> Any:
    ps = _powershell_executable()
    if ps is None:
        return {}
    completed = subprocess.run(
        [ps, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if not completed.stdout.strip():
        return {}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"raw": completed.stdout.strip(), "stderr": completed.stderr.strip(), "returnCode": completed.returncode}


def windows_service_status(service_name: str) -> dict[str, Any]:
    if _powershell_executable() is None:
        return {"found": False, "name": service_name, "status": "Unsupported", "displayName": "", "canStop": False}
    script = f"""
$svc = Get-Service -Name {json.dumps(service_name)} -ErrorAction SilentlyContinue
if ($svc) {{
  [pscustomobject]@{{ found = $true; name = [string]$svc.Name; displayName = [string]$svc.DisplayName; status = [string]$svc.Status; canStop = [bool]$svc.CanStop }} | ConvertTo-Json -Depth 4
}} else {{
  [pscustomobject]@{{ found = $false; name = {json.dumps(service_name)}; status = "Missing"; displayName = ""; canStop = $false }} | ConvertTo-Json -Depth 4
}}
"""
    result = _powershell_json(script)
    return result if isinstance(result, dict) else {"found": False, "name": service_name, "status": "Unknown"}


def scheduled_task_status(task_name: str) -> dict[str, Any]:
    if shutil.which("schtasks.exe") is None:
        return {"taskName": task_name, "found": False, "returnCode": 127, "stdout": "", "stderr": "schtasks.exe unavailable"}
    result = run_command_capture(["schtasks.exe", "/Query", "/TN", task_name, "/FO", "LIST", "/V"], timeout=15)
    return {
        "taskName": task_name,
        "found": result["returnCode"] == 0,
        "returnCode": result["returnCode"],
        "stdout": result["stdout"][:4000],
        "stderr": result["stderr"][:2000],
    }


def _parse_ingress_routes(raw: str) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for index, line in enumerate(raw.splitlines()):
        stripped = line.strip()
        if stripped.startswith("- hostname:"):
            if current:
                routes.append(current)
            current = {"hostname": stripped.split(":", 1)[1].strip(), "service": "", "line": index}
        elif stripped.startswith("- service:"):
            if current:
                routes.append(current)
            current = {"hostname": "", "service": stripped.split(":", 1)[1].strip(), "line": index}
        elif stripped.startswith("service:") and current is not None:
            current["service"] = stripped.split(":", 1)[1].strip()
    if current:
        routes.append(current)
    return routes


def check_config_drift(config_path: str, origins: list[dict[str, Any]], expected_fallback_404: bool) -> dict[str, Any]:
    path = Path(config_path)
    result = {
        "path": config_path,
        "exists": path.exists(),
        "routes": [],
        "ingressRoutes": [],
        "fallback404": False,
        "fallback404AtEnd": False,
        "duplicateRoutes": [],
        "controlRoute": {"hostname": "control.hitechrts.com", "origin": "http://127.0.0.1:3150", "exists": False, "serviceMatches": False},
        "drift": [],
        "rawPreview": "",
    }
    if not path.exists():
        result["drift"].append("CONFIG_MISSING")
        return result
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        result["drift"].append(f"CONFIG_UNREADABLE: {exc}")
        return result
    result["rawPreview"] = raw[:2000]
    compact = raw.replace("'", '"')
    ingress = _parse_ingress_routes(raw)
    result["ingressRoutes"] = [{"hostname": item.get("hostname"), "service": item.get("service"), "line": item.get("line")} for item in ingress]
    seen: dict[str, int] = {}
    for item in ingress:
        host = item.get("hostname") or "<fallback>"
        seen[host] = seen.get(host, 0) + 1
    result["duplicateRoutes"] = [host for host, count in seen.items() if count > 1 and host != "<fallback>"]
    if result["duplicateRoutes"]:
        result["drift"].append("DUPLICATE_INGRESS_ROUTES:" + ",".join(result["duplicateRoutes"]))
    for origin in origins:
        host = str(origin.get("hostname", ""))
        service = str(origin.get("origin", ""))
        host_ok = host in compact
        service_ok = service in compact
        route = {"hostname": host, "origin": service, "hostnameFound": host_ok, "originFound": service_ok, "ok": host_ok and service_ok}
        result["routes"].append(route)
        if not route["ok"]:
            result["drift"].append(f"ROUTE_DRIFT:{host}->{service}")
        if host == "control.hitechrts.com":
            result["controlRoute"] = {
                "hostname": host,
                "origin": service,
                "exists": host_ok,
                "serviceMatches": service_ok,
                "ok": host_ok and service_ok,
            }
    result["fallback404"] = "http_status:404" in compact.replace(" ", "")
    fallback_indexes = [i for i, item in enumerate(ingress) if str(item.get("service", "")).replace(" ", "") == "http_status:404"]
    result["fallback404AtEnd"] = bool(fallback_indexes) and fallback_indexes[-1] == len(ingress) - 1
    if expected_fallback_404 and not result["fallback404"]:
        result["drift"].append("FALLBACK_404_MISSING")
    if expected_fallback_404 and not result["fallback404AtEnd"]:
        result["drift"].append("FALLBACK_404_NOT_LAST")
    return result


def nslookup_host(hostname: str) -> dict[str, Any]:
    result = run_command_capture(["nslookup.exe", hostname], timeout=12)
    return {
        "hostname": hostname,
        "ok": result["returnCode"] == 0 and "Address" in result["stdout"],
        "returnCode": result["returnCode"],
        "output": result["stdout"][:3000],
        "error": result["stderr"][:1200],
    }


def check_control_center(public: bool = True) -> dict[str, Any]:
    cfg = load_cloudflare_config()
    control = cfg.get("controlCenter", {})
    local_url = str(control.get("localUrl", f"http://127.0.0.1:{CONTROL_CENTER_PORT}/"))
    public_url = str(control.get("publicUrl", "https://control.hitechrts.com/"))
    probe = {"mode": "all", "needles": ["PRISMA Control Center", "Control Center", "health"]}
    local_health = http_probe(local_url, probe, timeout=float(active_health_profile().get("httpTimeoutSeconds", 8)))
    public_health = http_probe_stable(public_url, probe, public=True) if public else {"url": public_url, "ok": None, "statusCode": None, "latencyMs": None, "skipped": True}
    public_mode_probe = {"ok": False, "safe": False, "mode": "UNKNOWN", "error": "local panel unavailable"}
    if local_health.get("ok"):
        api_probe = http_probe_with_headers(
            f"http://127.0.0.1:{CONTROL_CENTER_PORT}/api/health",
            {"Host": "control.hitechrts.com"},
            {"mode": "any", "needles": ["PUBLIC_REDACTED", "control_center", "health_score"]},
            timeout=float(active_health_profile().get("httpTimeoutSeconds", 8)),
        )
        public_json = LATEST_ROOT / "public-health.json"
        sensitive_hits: list[str] = []
        if public_json.exists():
            text = public_json.read_text(encoding="utf-8", errors="ignore")
            for pattern in [r"(?i)commandLine", r"(?i)executablePath", r"(?i)C:\\Users\\", r"(?i)F:\\repos\\hitech-os\\", r"(?i)\bpid\b", r"(?i)credentials-file", r"(?i)token", r"(?i)secret"]:
                if __import__("re").search(pattern, text):
                    sensitive_hits.append(pattern)
        public_mode_probe = {
            "ok": api_probe.get("ok"),
            "safe": not sensitive_hits,
            "mode": "PUBLIC_REDACTED" if api_probe.get("ok") else "UNKNOWN",
            "apiProbe": {k: v for k, v in api_probe.items() if k != "bodyPreview"},
            "sensitiveHits": sensitive_hits,
        }
    status = "PASS" if local_health.get("ok") and (not public or public_health.get("ok")) and public_mode_probe.get("safe") else "DEGRADED"
    if public and public_health.get("ok") is False:
        status = "DEGRADED"
    return {
        "status": status,
        "localUrl": local_url,
        "publicUrl": public_url,
        "localMode": control.get("localMode", "LOCAL_FULL"),
        "publicMode": control.get("publicMode", "PUBLIC_REDACTED"),
        "localHealth": local_health,
        "publicHealth": public_health,
        "publicModeProbe": public_mode_probe,
    }


def check_cloudflare(public: bool = True) -> dict[str, Any]:
    cfg = load_cloudflare_config()
    cloudflared = command_exists("cloudflared")
    if not cloudflared.get("found"):
        cloudflared = command_exists("cloudflared.exe")
    version = None
    tunnel_info = None
    tunnel_list = None
    if cloudflared.get("found"):
        version = run_command_capture([cloudflared["source"], "--version"], timeout=12)
        tunnel_info = run_command_capture([cloudflared["source"], "tunnel", "info", str(cfg.get("tunnelName", ""))], timeout=20)
        tunnel_list = run_command_capture([cloudflared["source"], "tunnel", "list"], timeout=20)
    service = windows_service_status(str(cfg.get("serviceName", "cloudflared")))
    drift = check_config_drift(str(cfg.get("configPath", "")), list(cfg.get("origins", [])), bool(cfg.get("expectedFallback404", True)))
    dns_routes = [nslookup_host(host) for host in cfg.get("hostnames", [])]
    scheduled_tasks = [scheduled_task_status(name) for name in cfg.get("knownScheduledTasks", [])]
    control_center = check_control_center(public=public)
    endpoints = []
    if public:
        for endpoint in cfg.get("publicEndpoints", []):
            endpoints.append(
                {
                    **endpoint,
                    "probe": http_probe_stable(str(endpoint.get("url", "")), endpoint.get("contentProbe", {}), public=True),
                }
            )
        for endpoint in endpoints:
            if endpoint.get("id") == "public-control-center":
                control_center["publicHealth"] = endpoint.get("probe", {})
                if not endpoint.get("probe", {}).get("ok"):
                    control_center["status"] = "DEGRADED"
                break
    required_endpoints = [item for item in endpoints if item.get("required")]
    required_public_ok = all(item["probe"]["ok"] for item in required_endpoints) if required_endpoints else True
    optional_public_ok = all(item["probe"]["ok"] for item in endpoints) if endpoints else True
    config_ok = drift["exists"] and not drift["drift"]
    service_ok = service.get("found") and service.get("status") == "Running"
    binary_ok = bool(cloudflared.get("found"))
    if not binary_ok or not config_ok:
        status = "FAIL" if cfg.get("mode") == "required" else "DEGRADED"
    elif not service_ok:
        status = "DEGRADED"
    elif not required_public_ok:
        status = "FAIL"
    elif not optional_public_ok:
        status = "DEGRADED"
    else:
        status = "PASS"
    return {
        "mode": cfg.get("mode", "optional"),
        "status": status,
        "cloudflared": cloudflared,
        "version": version,
        "service": service,
        "config": drift,
        "tunnelName": cfg.get("tunnelName"),
        "tunnelInfo": tunnel_info,
        "tunnelList": tunnel_list,
        "dnsRoutes": dns_routes,
        "scheduledTasks": scheduled_tasks,
        "controlCenter": control_center,
        "publicEndpoints": endpoints,
        "origins": cfg.get("origins", []),
        "actionsTaken": [],
        "actionsBlocked": [],
    }
