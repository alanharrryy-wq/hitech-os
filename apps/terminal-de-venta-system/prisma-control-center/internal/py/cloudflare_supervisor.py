from __future__ import annotations

import subprocess
import time
from typing import Any

from config_loader import CONTROL_ROOT, load_cloudflare_config, python_executable
from health_checks import check_cloudflare
from safe_actions import run_command_capture, start_detached_process


def _service_command(service_name: str, verb: str) -> dict[str, Any]:
    script = f"{verb}-Service -Name {service_name!r} -ErrorAction Stop"
    try:
        completed = subprocess.run(
            ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "command": script,
            "returnCode": completed.returncode,
            "stdout": (completed.stdout or "").strip(),
            "stderr": (completed.stderr or "").strip(),
            "ok": completed.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"command": script, "returnCode": 124, "stdout": "", "stderr": "timeout", "ok": False}


def collect_cloudflare_health(public: bool = True) -> dict[str, Any]:
    return check_cloudflare(public=public)


def ensure_control_panel_origin(run_log: Any) -> dict[str, Any]:
    before = check_cloudflare(public=False).get("controlCenter", {})
    if before.get("localHealth", {}).get("ok"):
        result = {"code": "CONTROL_CENTER_ORIGIN_ALREADY_UP", "url": before.get("localUrl")}
        run_log.log("control-center-origin-ok", result)
        return result
    cfg = load_cloudflare_config().get("controlCenter", {})
    if not cfg.get("originMayBeStartedByCloudflareUp", True):
        result = {"code": "CONTROL_CENTER_ORIGIN_START_DISABLED", "url": cfg.get("localUrl")}
        run_log.log("control-center-origin-start-disabled", result)
        return result
    command = f'"{python_executable()}" "{CONTROL_ROOT / "internal" / "py" / "prisma_control_center.py"}" panel'
    result = start_detached_process("control-center-3150", command, str(CONTROL_ROOT))
    run_log.log("start-control-center-origin", result)
    time.sleep(2)
    return {"code": "START_CONTROL_CENTER_ORIGIN", **result}


def ensure_cloudflare(run_log: Any) -> dict[str, Any]:
    cfg = load_cloudflare_config()
    run_log.log("cloudflare-check", {"mode": cfg.get("mode"), "serviceName": cfg.get("serviceName")})
    origin_action = ensure_control_panel_origin(run_log)
    report = check_cloudflare(public=True)
    report.setdefault("actionsTaken", [])
    report.setdefault("actionsBlocked", [])
    report["actionsTaken"].append(origin_action)

    if not report.get("cloudflared", {}).get("found"):
        report["actionsBlocked"].append({"code": "CLOUDFLARED_NOT_FOUND", "message": "cloudflared is not available in PATH."})
        run_log.log("cloudflared-not-found", report["actionsBlocked"][-1])
        return report

    service = report.get("service", {})
    service_name = str(cfg.get("serviceName", "cloudflared"))
    if not service.get("found"):
        report["actionsBlocked"].append({"code": "CLOUDFLARED_SERVICE_MISSING", "serviceName": service_name})
        run_log.log("cloudflared-service-missing", report["actionsBlocked"][-1])
        return report

    if service.get("status") != "Running":
        action = _service_command(service_name, "Start")
        start_record = {"code": "START_CLOUDFLARED_SERVICE", **action}
        run_log.log("start-cloudflared-service", action)
        if not action.get("ok"):
            report["actionsBlocked"].append(
                {
                    "code": "CLOUDFLARED_SERVICE_START_BLOCKED",
                    "serviceName": service_name,
                    "message": "Windows did not allow starting the cloudflared service from this session. Run the Control Center from an elevated shell or start the service manually.",
                    **action,
                }
            )
            run_log.log("start-cloudflared-service-blocked", report["actionsBlocked"][-1])
            return report
        report["actionsTaken"].append(start_record)
        time.sleep(4)
        previous_actions = list(report.get("actionsTaken", []))
        report = check_cloudflare(public=True)
        report.setdefault("actionsTaken", []).extend(previous_actions)
        report.setdefault("actionsBlocked", [])
        return report

    public_endpoints = report.get("publicEndpoints", [])
    public_ok = all(item.get("probe", {}).get("ok") for item in public_endpoints) if public_endpoints else True
    config_ok = report.get("config", {}).get("exists") and not report.get("config", {}).get("drift")
    if config_ok and not public_ok and cfg.get("restartServiceOnPublicHealthFail", True):
        action = _service_command(service_name, "Restart")
        restart_record = {"code": "RESTART_CLOUDFLARED_SERVICE", **action}
        run_log.log("restart-cloudflared-service", action)
        if not action.get("ok"):
            report["actionsBlocked"].append(
                {
                    "code": "CLOUDFLARED_SERVICE_RESTART_BLOCKED",
                    "serviceName": service_name,
                    "message": "Windows did not allow restarting the cloudflared service from this session. The config can be correct while the live connector remains stale until the service is restarted elevated.",
                    **action,
                }
            )
            run_log.log("restart-cloudflared-service-blocked", report["actionsBlocked"][-1])
            return report
        report["actionsTaken"].append(restart_record)
        time.sleep(6)
        retry = check_cloudflare(public=True)
        retry.setdefault("actionsTaken", []).extend(report.get("actionsTaken", []))
        retry.setdefault("actionsBlocked", []).extend(report.get("actionsBlocked", []))
        return retry

    if not config_ok:
        report["actionsBlocked"].append(
            {
                "code": "CONFIG_DRIFT_NO_AUTOFIX",
                "message": "Config drift detected. The Control Center does not rewrite Cloudflare config.yml.",
                "drift": report.get("config", {}).get("drift", []),
            }
        )
        run_log.log("cloudflare-config-drift", report["actionsBlocked"][-1])
    return report


def cloudflare_doctor_commands() -> list[dict[str, Any]]:
    cfg = load_cloudflare_config()
    outputs = []
    outputs.append(run_command_capture(["where.exe", "cloudflared"], timeout=12))
    outputs.append(run_command_capture(["sc.exe", "query", str(cfg.get("serviceName", "cloudflared"))], timeout=12))
    return outputs
