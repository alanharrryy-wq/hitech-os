from __future__ import annotations

import time
from typing import Any

from config_loader import active_health_profile
from health_checks import check_service
from ports_inspector import inspect_port
from process_classifier import classify_owners
from safe_actions import now_iso, start_detached_process, stop_process_safely
from services_registry import ServiceDef, load_services


def collect_local_health(action: str = "health", include_lan: bool = True) -> list[dict[str, Any]]:
    return [check_service(service, action=action, include_lan=include_lan) for service in load_services()]


def _wait_for_service(service: ServiceDef, timeline: list[dict[str, Any]]) -> dict[str, Any]:
    profile = active_health_profile()
    timeout = int(profile.get("startupTimeoutSeconds", 80))
    poll = max(1, int(profile.get("startupPollSeconds", 3)))
    deadline = time.time() + timeout
    latest = check_service(service, action="local-up")
    while time.time() < deadline:
        latest = check_service(service, action="local-up")
        if latest.get("healthy"):
            timeline.append({"time": now_iso(), "event": "service-healthy", "detail": {"serviceId": service.id, "port": service.port}})
            return latest
        time.sleep(poll)
    timeline.append({"time": now_iso(), "event": "service-start-timeout", "detail": {"serviceId": service.id, "port": service.port}})
    return latest


def ensure_local_services(run_log: Any, action: str = "local-up") -> list[dict[str, Any]]:
    services = load_services()
    results: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = run_log.entries
    for service in services:
        run_log.log("local-check", {"serviceId": service.id, "port": service.port})
        current = check_service(service, action=action)
        current.setdefault("actionsTaken", [])
        current.setdefault("actionsBlocked", [])
        if current.get("healthy"):
            current["actionsTaken"].append("NOOP_HEALTHY")
            results.append(current)
            continue

        port_report = inspect_port(service.port)
        owners = classify_owners(port_report, action=action, service_id=service.id)
        unknown_owners = [owner for owner in owners if not owner.get("classification", {}).get("recognized")]
        recognized_owners = [owner for owner in owners if owner.get("classification", {}).get("recognized")]

        if unknown_owners:
            blocked = {
                "code": "BLOCKED_UNKNOWN_PROCESS",
                "serviceId": service.id,
                "port": service.port,
                "owners": unknown_owners,
            }
            current["status"] = "BLOCKED"
            current["blocked"] = True
            current["actionsBlocked"].append(blocked)
            run_log.log("blocked-unknown-process", blocked)
            results.append(current)
            continue

        if recognized_owners:
            for owner in recognized_owners:
                stop_result = stop_process_safely(owner, action=action, service_id=service.id, timeline=timeline)
                if str(stop_result.get("status", "")).startswith("BLOCKED"):
                    current["status"] = "BLOCKED"
                    current["blocked"] = True
                    current["actionsBlocked"].append(stop_result)
                    run_log.log("blocked-recognized-stop", stop_result)
                    results.append(current)
                    break
                current["actionsTaken"].append(stop_result)
            if current.get("status") == "BLOCKED":
                continue

        if not service.has_start_command:
            blocked = {
                "code": "MISSING_START_COMMAND",
                "serviceId": service.id,
                "port": service.port,
                "message": "startCommand is TO_DEFINE.",
            }
            current["status"] = "FAIL"
            current["actionsBlocked"].append(blocked)
            run_log.log("missing-start-command", blocked)
            results.append(current)
            continue

        start_result = start_detached_process(service.id, service.start_command, service.cwd)
        current["actionsTaken"].append(start_result)
        run_log.log("start-service", {"serviceId": service.id, **start_result})
        after = _wait_for_service(service, timeline)
        after.setdefault("actionsTaken", [])
        after.setdefault("actionsBlocked", [])
        after["actionsTaken"].extend(current["actionsTaken"])
        after["actionsBlocked"].extend(current["actionsBlocked"])
        if not after.get("healthy") and after.get("status") != "BLOCKED":
            after["status"] = "FAIL"
        results.append(after)
    return results
