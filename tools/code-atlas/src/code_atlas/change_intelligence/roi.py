from __future__ import annotations

from typing import Any, Mapping

from .contracts import ROI_SCHEMA, ContractError, require_nonempty_string, sha256_json, utc_now_iso

RAW_METRICS = {
    "contextDiscoveryTime",
    "changeScopeIdentificationTime",
    "humanSupervisionTime",
    "outOfScopeChangeRate",
    "reopenedWorkRate",
    "evidenceAssemblyTime",
    "changeReadinessThroughput",
    "blockedBeforeChangeCount",
    "evidenceCompletenessRate",
}


def build_roi_event(*, metric: str, value: float, unit: str, repository_identity: str, source: str, observed_at: str | None = None, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if metric not in RAW_METRICS:
        raise ContractError(f"unsupported raw ROI metric: {metric}")
    if not isinstance(value, (int, float)) or value < 0:
        raise ContractError("ROI metric value must be a non-negative number")
    event = {
        "schemaVersion": ROI_SCHEMA,
        "metric": metric,
        "value": value,
        "unit": require_nonempty_string(unit, "unit"),
        "repositoryIdentity": require_nonempty_string(repository_identity, "repository_identity"),
        "source": require_nonempty_string(source, "source"),
        "observedAt": observed_at or utc_now_iso(),
        "context": dict(context or {}),
        "financialEstimate": None,
        "observedMetric": True,
        "certifiable": False,
        "productionCertified": False,
    }
    event["eventDigest"] = sha256_json(event)
    return event


def derive_financial_estimate(events: list[Mapping[str, Any]], *, loaded_hourly_cost: float, assumption_label: str) -> dict[str, Any]:
    if not isinstance(loaded_hourly_cost, (int, float)) or loaded_hourly_cost < 0:
        raise ContractError("loaded_hourly_cost must be a non-negative number")
    label = require_nonempty_string(assumption_label, "assumption_label")
    hours = 0.0
    supported_time_metrics = {"contextDiscoveryTime", "changeScopeIdentificationTime", "humanSupervisionTime", "evidenceAssemblyTime"}
    source_events: list[str] = []
    for event in events:
        if event.get("metric") in supported_time_metrics and event.get("unit") == "hours":
            hours += float(event.get("value", 0.0))
            if isinstance(event.get("eventDigest"), str):
                source_events.append(event["eventDigest"])
    return {
        "derived": True,
        "assumptionLabel": label,
        "loadedHourlyCost": loaded_hourly_cost,
        "hours": hours,
        "estimatedValue": hours * loaded_hourly_cost,
        "sourceEventDigests": source_events,
        "doesNotProve": ["realized cash savings", "profit", "customer willingness to pay"],
    }
