from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from capatch_audit import list_baselines
from capatch_audit.telemetry import enrich_payload, write_telemetry_report
from capatch_runtime.environment_guard import capture_environment_guard, evaluate_environment_guard
from tooling.run_plugin_contract_smoke import run_contract_smoke
from tooling.run_rollback_drill import run_rollback_drill
from tooling.run_windows_smoke import run_windows_smoke


def _check(name: str, status: str, detail: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": str(name),
        "status": str(status),
        "detail": str(detail),
        "payload": dict(payload or {}),
    }


def _aggregate_verdict(checks: list[dict[str, Any]]) -> str:
    statuses = [str(item.get("status") or "") for item in checks]
    if any(status in {"failed", "blocked"} for status in statuses):
        return "blocked"
    if any(status in {"degraded", "warning"} for status in statuses):
        return "degraded"
    return "promotable"


def run_readiness_gate(base_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    base_dir = Path(base_dir).resolve()
    started = time.perf_counter()
    env_payload = capture_environment_guard(base_dir, base_dir)
    env_status = evaluate_environment_guard(env_payload)
    windows_smoke = run_windows_smoke(base_dir, None)
    plugin_smoke = run_contract_smoke(base_dir, None)
    rollback_drill = run_rollback_drill(base_dir, None)
    baselines = list_baselines(base_dir)
    checks = [
        _check(
            "environment_guard",
            "blocked" if env_status.get("status") == "blocked" else ("degraded" if env_status.get("status") == "degraded" else "passed"),
            "; ".join(list(env_status.get("reasons") or []) + list(env_status.get("warnings") or [])) or "environment healthy",
            env_status,
        ),
        _check(
            "windows_smoke",
            "passed" if windows_smoke.get("status") in {"passed", "skipped"} else ("degraded" if windows_smoke.get("status") == "degraded" else "failed"),
            str(windows_smoke.get("reason") or windows_smoke.get("smoke_status_reason") or windows_smoke.get("status")),
            windows_smoke,
        ),
        _check(
            "plugin_contract_smoke",
            "passed" if plugin_smoke.get("status") == "passed" else ("degraded" if plugin_smoke.get("status") == "degraded" else "failed"),
            ", ".join(list(plugin_smoke.get("issues") or [])) or str(plugin_smoke.get("status") or "unknown"),
            plugin_smoke,
        ),
        _check(
            "rollback_drill",
            "passed" if rollback_drill.get("status") == "passed" else "failed",
            str(rollback_drill.get("status") or "unknown"),
            rollback_drill,
        ),
        _check(
            "baseline_inventory",
            "passed" if baselines else "degraded",
            f"baselines={len(baselines)}",
            {"count": len(baselines), "latest": baselines[0] if baselines else None},
        ),
    ]
    verdict = _aggregate_verdict(checks)
    summary = {
        "passed": len([item for item in checks if item["status"] == "passed"]),
        "degraded": len([item for item in checks if item["status"] == "degraded"]),
        "blocked": len([item for item in checks if item["status"] in {"blocked", "failed"}]),
        "check_count": len(checks),
    }
    payload = enrich_payload(
        {
            "name": "readiness_gate",
            "status": verdict,
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "summary": summary,
            "checks": checks,
            "environment_guard": env_status,
            "baseline_count": len(baselines),
        },
        root_dir=base_dir,
        artifact_kind="telemetry-report",
        artifact_scope="reports/telemetry/readiness_gate",
    )
    if output_dir is not None:
        lines = ["## checks", ""]
        for item in checks:
            lines.append(f"- `{item['name']}` => `{item['status']}` :: {item['detail']}")
        payload["report_paths"] = write_telemetry_report(output_dir, "readiness_gate", payload, lines)
    return payload
