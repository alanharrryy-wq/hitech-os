#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from tools.hos._core.stable_json import write_json

from .config import SentinelConfig
from .utils import now_utc_iso


def _build_events(config: SentinelConfig, report_payload: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    health_score = int(report_payload.get("health", {}).get("score", 0))
    health_status = str(report_payload.get("health", {}).get("status", "unknown"))
    if health_score <= int(config.alert_health_threshold):
        events.append(
            {
                "kind": "health",
                "severity": "high" if health_score < 50 else "medium",
                "detail": f"health_score={health_score} status={health_status} threshold={config.alert_health_threshold}",
            }
        )

    security = report_payload.get("security", {})
    security_level = str(security.get("alertLevel", "none")).lower()
    if security_level in {"high", "critical"}:
        events.append(
            {
                "kind": "security",
                "severity": security_level,
                "detail": f"security_alert_level={security_level} findings={security.get('findingCount', 0)}",
            }
        )

    errors = [str(item) for item in report_payload.get("errors", [])]
    stop_errors = [item for item in errors if item.startswith("stop_condition_triggered")]
    if stop_errors:
        events.append(
            {
                "kind": "stop_condition",
                "severity": "high",
                "detail": "; ".join(stop_errors[:3]),
            }
        )

    return events


def _post_webhook(webhook: str, payload: dict[str, Any]) -> tuple[bool, int, str]:
    request = Request(
        webhook,
        data=json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            return True, int(response.status), ""
    except URLError as exc:
        return False, 0, str(exc)
    except OSError as exc:
        return False, 0, str(exc)


def emit_alerts(config: SentinelConfig, report_payload: dict[str, Any]) -> dict[str, Any]:
    events = _build_events(config=config, report_payload=report_payload)
    if not events:
        return {
            "triggered": False,
            "eventCount": 0,
            "sent": False,
            "webhookConfigured": bool(os.getenv(config.alert_webhook_env_var, "").strip()),
            "logPath": "",
            "statusCode": 0,
            "error": "",
        }

    timestamp = str(report_payload.get("timestamp", now_utc_iso()))
    slug = timestamp.replace(":", "").replace("-", "")
    payload = {
        "timestamp": timestamp,
        "repoRoot": report_payload.get("repoRoot", config.repo_root.as_posix()),
        "health": report_payload.get("health", {}),
        "security": report_payload.get("security", {}),
        "errors": report_payload.get("errors", []),
        "events": events,
        "files": report_payload.get("files", {}),
    }
    log_path = (config.log_dir / f"alert_{slug}.json").resolve()
    write_json(log_path, payload, indent=2, sort_keys=True)

    webhook = os.getenv(config.alert_webhook_env_var, "").strip()
    if not webhook:
        return {
            "triggered": True,
            "eventCount": len(events),
            "sent": False,
            "webhookConfigured": False,
            "logPath": log_path.as_posix(),
            "statusCode": 0,
            "error": "",
        }

    sent, status_code, error = _post_webhook(webhook=webhook, payload=payload)
    return {
        "triggered": True,
        "eventCount": len(events),
        "sent": bool(sent),
        "webhookConfigured": True,
        "logPath": log_path.as_posix(),
        "statusCode": int(status_code),
        "error": str(error),
    }
