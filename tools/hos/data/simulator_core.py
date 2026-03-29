#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from tools.hos._core.hashing import hash_json_stable
from tools.hos.data.reference_catalog import (
    ACTOR_DISPLAY_NAMES,
    EVENT_MESSAGE_SNIPPETS,
    RUN_NAME_CATALOG,
    TAG_CATALOG,
)

Severity = str
RunStatus = str

RUN_STATUSES: tuple[RunStatus, ...] = (
    "queued",
    "scheduled",
    "running",
    "paused",
    "succeeded",
    "failed",
    "canceled",
)
RUN_PRIORITIES: tuple[str, ...] = ("low", "normal", "high", "critical")
RUN_SOURCES: tuple[str, ...] = ("manual", "schedule", "api", "automation")
RUN_HEALTH: tuple[str, ...] = ("healthy", "degraded", "stalled", "unknown")
SEVERITIES: tuple[Severity, ...] = ("debug", "info", "warn", "error", "critical")
ACTOR_TYPES: tuple[str, ...] = ("user", "service", "system")
EVENT_TYPES: tuple[str, ...] = (
    "run.created",
    "run.queued",
    "run.started",
    "run.progress",
    "run.paused",
    "run.resumed",
    "run.completed",
    "run.failed",
    "run.canceled",
    "evidence.added",
    "widget.updated",
    "system.alert",
    "auth.login",
    "auth.logout",
)


@dataclass(frozen=True)
class ScenarioDefinition:
    name: str
    description: str
    run_count: int
    duration_minutes: int
    baseline_cpu: float
    baseline_memory_mb: float
    baseline_throughput: float
    baseline_latency_ms: float
    error_ratio: float
    critical_event_ratio: float
    burst_chance: float
    burst_scale: float
    queue_pressure_base: float
    recovery_bias: float


@dataclass(frozen=True)
class SimulationConfig:
    scenario: ScenarioDefinition
    seed: int
    start_at: dt.datetime
    request_prefix: str = "req"


@dataclass(frozen=True)
class SimulationBundle:
    metadata: dict[str, Any]
    series: list[dict[str, Any]]
    runs: list[dict[str, Any]]
    activity: list[dict[str, Any]]
    widgets: list[dict[str, Any]]
    layout: dict[str, Any]


class DeterministicRng:
    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def uniform(self, low: float, high: float) -> float:
        return self._rng.uniform(low, high)

    def randint(self, low: int, high: int) -> int:
        return self._rng.randint(low, high)

    def choice(self, items: list[Any]) -> Any:
        if not items:
            raise ValueError("choice requires non-empty list")
        return items[self._rng.randrange(0, len(items))]

    def weighted_choice(self, weighted: list[tuple[Any, float]]) -> Any:
        if not weighted:
            raise ValueError("weighted_choice requires non-empty list")
        total = sum(max(0.0, weight) for _, weight in weighted)
        if total <= 0:
            return weighted[0][0]
        cursor = self.uniform(0.0, total)
        seen = 0.0
        for value, weight in weighted:
            seen += max(0.0, weight)
            if seen >= cursor:
                return value
        return weighted[-1][0]

    def probability(self, chance: float) -> bool:
        clamped = max(0.0, min(1.0, chance))
        return self.uniform(0.0, 1.0) <= clamped

    def normal(self, mean: float, sigma: float) -> float:
        return self._rng.normalvariate(mean, sigma)


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).replace(tzinfo=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _build_series(config: SimulationConfig, rng: DeterministicRng) -> list[dict[str, Any]]:
    scenario = config.scenario
    points: list[dict[str, Any]] = []
    for minute in range(scenario.duration_minutes):
        timestamp = config.start_at + dt.timedelta(minutes=minute)
        phase = (minute / max(1, scenario.duration_minutes)) * 2.0 * math.pi

        harmonic = math.sin(phase) * 0.5 + math.sin(phase * 2.3) * 0.25
        cpu = scenario.baseline_cpu + harmonic * 8.0 + rng.normal(0, 3.2)
        latency = scenario.baseline_latency_ms + harmonic * 14.0 + rng.normal(0, 7.5)
        throughput = scenario.baseline_throughput + harmonic * 85.0 + rng.normal(0, 32.0)
        memory = scenario.baseline_memory_mb + harmonic * 96.0 + rng.normal(0, 44.0)
        queue = scenario.queue_pressure_base + harmonic * 0.12 + rng.normal(0, 0.06)
        errors = scenario.error_ratio + rng.normal(0, scenario.error_ratio * 0.45 + 0.001)

        if rng.probability(scenario.burst_chance):
            scale = scenario.burst_scale * rng.uniform(0.75, 1.35)
            cpu += 10.0 * scale
            latency += 35.0 * scale
            throughput -= 110.0 * scale
            queue += 0.2 * scale
            errors += 0.02 * scale

        if scenario.recovery_bias > 0:
            recovery = (minute / max(1, scenario.duration_minutes)) * scenario.recovery_bias
            latency -= recovery * 24.0
            queue -= recovery * 0.18
            errors -= recovery * 0.01
            throughput += recovery * 120.0

        cpu = _clamp(cpu, 5.0, 99.0)
        memory = _clamp(memory, 512.0, 128_000.0)
        throughput = _clamp(throughput, 50.0, 24_000.0)
        queue = _clamp(queue, 0.0, 1.0)
        errors = _clamp(errors, 0.0, 1.0)
        latency = _clamp(latency, 5.0, 2_000.0)

        success_rate = _clamp(1.0 - errors * 1.75 - queue * 0.12, 0.0, 1.0)
        p50 = latency
        p95 = latency * (1.25 + queue * 0.4)
        p99 = latency * (1.55 + queue * 0.6)

        points.append(
            {
                "at": _iso(timestamp),
                "cpuPercent": round(cpu, 2),
                "memoryMb": round(memory, 2),
                "throughputPerMin": round(throughput, 2),
                "latencyMs": {
                    "p50": round(p50, 2),
                    "p95": round(p95, 2),
                    "p99": round(p99, 2),
                },
                "queuePressure": round(queue, 4),
                "errorRatio": round(errors, 5),
                "successRate": round(success_rate, 5),
                "activeWorkers": int(round(_clamp(cpu / 8.0 + queue * 8.0, 1.0, 32.0))),
            }
        )
    return points


def _weighted_status_for_scenario(scenario: ScenarioDefinition) -> list[tuple[str, float]]:
    if scenario.name == "incident":
        return [
            ("running", 0.22),
            ("failed", 0.28),
            ("paused", 0.16),
            ("queued", 0.14),
            ("scheduled", 0.08),
            ("canceled", 0.07),
            ("succeeded", 0.05),
        ]
    if scenario.name == "recovery":
        return [
            ("running", 0.30),
            ("succeeded", 0.30),
            ("queued", 0.10),
            ("scheduled", 0.10),
            ("paused", 0.08),
            ("failed", 0.08),
            ("canceled", 0.04),
        ]
    if scenario.name == "degraded":
        return [
            ("running", 0.30),
            ("paused", 0.16),
            ("failed", 0.14),
            ("queued", 0.14),
            ("scheduled", 0.10),
            ("succeeded", 0.10),
            ("canceled", 0.06),
        ]
    if scenario.name == "spike":
        return [
            ("running", 0.38),
            ("queued", 0.18),
            ("scheduled", 0.14),
            ("succeeded", 0.12),
            ("failed", 0.09),
            ("paused", 0.06),
            ("canceled", 0.03),
        ]
    return [
        ("running", 0.32),
        ("succeeded", 0.24),
        ("queued", 0.13),
        ("scheduled", 0.10),
        ("failed", 0.08),
        ("paused", 0.08),
        ("canceled", 0.05),
    ]


def _derive_health(status: str, progress: float, queue_pressure: float, error_ratio: float) -> str:
    if status in {"failed", "canceled"}:
        return "degraded"
    if status == "succeeded":
        return "healthy"
    if queue_pressure >= 0.82:
        return "stalled"
    if error_ratio >= 0.08 or (status == "running" and progress < 2.0):
        return "degraded"
    if status in {"queued", "scheduled"}:
        return "unknown"
    return "healthy"


def _progress_for_status(status: str, rng: DeterministicRng) -> tuple[int, int, float, int | None]:
    total_steps = rng.randint(6, 24)
    if status == "queued":
        current = 0
    elif status == "scheduled":
        current = rng.randint(0, 1)
    elif status == "running":
        current = rng.randint(1, max(1, total_steps - 2))
    elif status == "paused":
        current = rng.randint(1, max(1, total_steps - 3))
    else:
        current = total_steps

    percent = round((current / total_steps) * 100.0, 2)
    if status in {"failed", "canceled"}:
        percent = round(_clamp(percent * rng.uniform(0.2, 0.95), 1.0, 99.0), 2)
    eta = None if status in {"failed", "canceled", "succeeded", "scheduled", "queued"} else rng.randint(90, 4200)
    return current, total_steps, percent, eta


def _run_name(index: int) -> str:
    if not RUN_NAME_CATALOG:
        return f"Run #{index:04d}"
    return RUN_NAME_CATALOG[(index - 1) % len(RUN_NAME_CATALOG)]


def _generate_runs(config: SimulationConfig, series: list[dict[str, Any]], rng: DeterministicRng) -> list[dict[str, Any]]:
    scenario = config.scenario
    statuses = _weighted_status_for_scenario(scenario)
    widgets_pool = [f"wid_stat-{i:03d}" for i in range(1, 21)] + [f"wid_table-{i:03d}" for i in range(1, 21)] + [
        f"wid_feed-{i:03d}" for i in range(1, 12)
    ]

    runs: list[dict[str, Any]] = []
    for idx in range(1, scenario.run_count + 1):
        run_id = f"run_{_slug(scenario.name)}-{idx:03d}"
        status = rng.weighted_choice(statuses)
        priority = rng.weighted_choice(
            [("normal", 0.44), ("high", 0.30), ("critical", 0.12), ("low", 0.14)]
        )
        source = rng.weighted_choice([("automation", 0.45), ("schedule", 0.25), ("api", 0.16), ("manual", 0.14)])

        progress_step, total_steps, progress_percent, eta = _progress_for_status(status=status, rng=rng)
        sample = rng.choice(series)
        health = _derive_health(
            status=status,
            progress=progress_percent,
            queue_pressure=float(sample["queuePressure"]),
            error_ratio=float(sample["errorRatio"]),
        )

        finished = status in {"succeeded", "failed", "canceled"}
        now = config.start_at + dt.timedelta(minutes=config.scenario.duration_minutes - 1)
        created = now - dt.timedelta(minutes=rng.randint(8, scenario.duration_minutes + 420))
        scheduled = created + dt.timedelta(minutes=rng.randint(1, 35))
        started = scheduled + dt.timedelta(minutes=rng.randint(1, 30)) if status != "queued" else None
        updated = now - dt.timedelta(minutes=rng.randint(0, 20))
        if started is not None and updated < started:
            updated = started + dt.timedelta(minutes=rng.randint(1, 5))
        finished_at = None
        if finished and started is not None:
            candidate = started + dt.timedelta(minutes=rng.randint(4, 260))
            finished_at = candidate if candidate <= now else now
            updated = finished_at

        widget_count = rng.randint(1, 4)
        widget_ids = sorted({rng.choice(widgets_pool) for _ in range(widget_count)})
        available_tags = list(TAG_CATALOG) + [scenario.name]
        tags = sorted({rng.choice(available_tags) for _ in range(rng.randint(2, 5))})

        runs.append(
            {
                "id": run_id,
                "name": _run_name(idx),
                "status": status,
                "priority": priority,
                "source": source,
                "ownerId": f"usr_owner-{(idx % 9) + 1:04d}",
                "assigneeId": f"usr_exec-{(idx % 11) + 1:04d}" if rng.probability(0.65) else None,
                "widgetIds": widget_ids,
                "health": health if health in RUN_HEALTH else "unknown",
                "progress": {
                    "currentStep": progress_step,
                    "totalSteps": total_steps,
                    "percent": progress_percent,
                    "etaSeconds": eta,
                },
                "tags": tags,
                "timestamps": {
                    "createdAt": _iso(created),
                    "scheduledAt": _iso(scheduled) if status != "queued" else None,
                    "startedAt": _iso(started) if started is not None else None,
                    "updatedAt": _iso(updated),
                    "finishedAt": _iso(finished_at) if finished_at is not None else None,
                },
                "version": rng.randint(1, 18),
            }
        )
    runs.sort(key=lambda item: (item["status"], item["priority"], item["id"]))
    return runs


def _actor_for_event(rng: DeterministicRng) -> dict[str, Any]:
    actor_type = rng.weighted_choice([("service", 0.5), ("user", 0.3), ("system", 0.2)])
    if actor_type == "service":
        display = rng.choice(
            [
                "Scheduler Service",
                "Pipeline Service",
                "Alerts Service",
                "Metrics Service",
                "API Service",
            ]
        )
        return {
            "type": "service",
            "id": f"svc_{rng.choice(['scheduler', 'pipeline', 'alerts', 'metrics', 'api'])}",
            "userId": None,
            "displayName": display,
            "avatarUrl": None,
        }
    if actor_type == "system":
        return {
            "type": "system",
            "id": f"sys_{rng.choice(['guard', 'monitor', 'observer', 'runtime'])}",
            "userId": None,
            "displayName": rng.choice(["System Guard", "System Monitor", "System Observer", "Runtime Core"]),
            "avatarUrl": None,
        }
    return {
        "type": "user",
        "id": f"usr_ops-{rng.randint(1, 99):04d}",
        "userId": f"usr_ops-{rng.randint(1, 99):04d}",
        "displayName": rng.choice(list(ACTOR_DISPLAY_NAMES) if ACTOR_DISPLAY_NAMES else ["Ops Analyst"]),
        "avatarUrl": None,
    }


def _event_severity(rng: DeterministicRng, event_type: str, scenario: ScenarioDefinition) -> Severity:
    if event_type == "system.alert":
        return rng.weighted_choice(
            [("warn", 0.25), ("error", 0.45), ("critical", 0.30 + scenario.critical_event_ratio)]
        )
    if event_type in {"run.failed", "run.canceled"}:
        return rng.weighted_choice([("warn", 0.25), ("error", 0.5), ("critical", 0.25)])
    if event_type in {"run.paused", "run.resumed", "widget.updated"}:
        return rng.weighted_choice([("info", 0.5), ("warn", 0.35), ("debug", 0.15)])
    if event_type in {"run.progress", "auth.logout"}:
        return rng.weighted_choice([("debug", 0.65), ("info", 0.35)])
    return rng.weighted_choice([("info", 0.75), ("debug", 0.15), ("warn", 0.10)])


def _event_title(event_type: str, run_name: str | None) -> str:
    titles = {
        "run.created": "Run Created",
        "run.queued": "Run Queued",
        "run.started": "Run Started",
        "run.progress": "Run Progress",
        "run.paused": "Run Paused",
        "run.resumed": "Run Resumed",
        "run.completed": "Run Completed",
        "run.failed": "Run Failed",
        "run.canceled": "Run Canceled",
        "evidence.added": "Evidence Added",
        "widget.updated": "Widget Updated",
        "system.alert": "System Alert",
        "auth.login": "User Login",
        "auth.logout": "User Logout",
    }
    if run_name:
        return f"{titles.get(event_type, 'Activity')} · {run_name}"
    return titles.get(event_type, "Activity")


def _event_message(event_type: str, run_name: str | None, rng: DeterministicRng, sample: dict[str, Any]) -> str:
    fallback = rng.choice(list(EVENT_MESSAGE_SNIPPETS) if EVENT_MESSAGE_SNIPPETS else ["event recorded"])
    if event_type == "system.alert":
        return (
            f"Queue pressure at {sample['queuePressure']} and latency p99={sample['latencyMs']['p99']}ms "
            f"during {run_name or 'global operations'}."
        )
    if event_type == "run.progress":
        return f"{run_name or 'Run'} reported throughput {sample['throughputPerMin']} events/min."
    if event_type == "run.failed":
        return f"{run_name or 'Run'} failed after elevated error ratio {sample['errorRatio']}."
    if event_type == "run.completed":
        return f"{run_name or 'Run'} completed with success rate {sample['successRate']}."
    if event_type == "widget.updated":
        return f"Widget settings changed by control plane for {run_name or 'dashboard'}."
    if event_type == "auth.login":
        return f"Operator session opened from trusted segment {rng.randint(10, 99)}."
    if event_type == "auth.logout":
        return f"Operator session closed after {rng.randint(5, 95)} minutes."
    return f"{run_name or 'Run'} generated event type {event_type}; {fallback}"


def _generate_activity(
    config: SimulationConfig,
    series: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    rng: DeterministicRng,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    event_count = max(40, int(len(runs) * 4.5))
    for idx in range(1, event_count + 1):
        run = rng.choice(runs) if rng.probability(0.85) else None
        event_type = rng.choice(list(EVENT_TYPES))
        sample = rng.choice(series)
        created_at = dt.datetime.fromisoformat(sample["at"].replace("Z", "+00:00"))
        jitter_seconds = rng.randint(0, 59)
        created_at = created_at + dt.timedelta(seconds=jitter_seconds)

        if run and run["status"] == "succeeded" and event_type == "run.failed":
            event_type = "run.completed"

        severity = _event_severity(rng=rng, event_type=event_type, scenario=config.scenario)
        event_id = f"act_{created_at.strftime('%Y%m%d%H%M%S')}-{_slug(event_type)}-{idx:04d}"

        metadata = {
            "cpuPercent": sample["cpuPercent"],
            "queuePressure": sample["queuePressure"],
            "throughputPerMin": sample["throughputPerMin"],
            "scenario": config.scenario.name,
            "seriesIndex": idx % len(series),
        }
        if run is not None:
            metadata["runStatus"] = run["status"]
            metadata["runPriority"] = run["priority"]

        items.append(
            {
                "id": event_id,
                "type": event_type,
                "severity": severity,
                "title": _event_title(event_type, run["name"] if run else None),
                "message": _event_message(event_type, run["name"] if run else None, rng, sample),
                "actor": _actor_for_event(rng),
                "runId": run["id"] if run else None,
                "createdAt": _iso(created_at),
                "acknowledged": rng.probability(0.42 if severity in {"error", "critical"} else 0.76),
                "metadata": metadata,
            }
        )

    items.sort(key=lambda item: (item["createdAt"], item["id"]), reverse=True)
    return items


def _widget_row_key(kind: str) -> str:
    return "id" if kind == "table" else "key"


def _generate_widgets(series: list[dict[str, Any]], runs: list[dict[str, Any]], rng: DeterministicRng) -> list[dict[str, Any]]:
    last = series[-1]
    sparkline_values = [point["throughputPerMin"] for point in series[-20:]]
    queue_values = [point["queuePressure"] * 100.0 for point in series[-20:]]
    success_values = [point["successRate"] * 100.0 for point in series[-20:]]
    widgets: list[dict[str, Any]] = [
        {
            "id": "wid_stat-001",
            "kind": "stat",
            "title": "Throughput",
            "subtitle": "per minute",
            "description": "Current throughput estimated from deterministic simulator.",
            "refresh": {"mode": "interval", "intervalSeconds": 15},
            "density": "compact",
            "pinned": True,
            "hidden": False,
            "config": {
                "value": round(last["throughputPerMin"], 2),
                "unit": "evt/min",
                "trend": "up" if sparkline_values[-1] >= sparkline_values[0] else "down",
                "precision": 2,
                "sparkline": [round(value, 2) for value in sparkline_values],
            },
        },
        {
            "id": "wid_stat-002",
            "kind": "stat",
            "title": "Success Rate",
            "subtitle": "window",
            "description": "Derived from error ratio and queue pressure.",
            "refresh": {"mode": "interval", "intervalSeconds": 30},
            "density": "compact",
            "pinned": True,
            "hidden": False,
            "config": {
                "value": round(last["successRate"] * 100.0, 2),
                "unit": "%",
                "trend": "flat",
                "precision": 2,
                "sparkline": [round(value, 2) for value in success_values],
            },
        },
        {
            "id": "wid_dial-001",
            "kind": "dial-placeholder",
            "title": "Queue Pressure",
            "subtitle": "risk window",
            "description": "Queue pressure scale from 0 to 100.",
            "refresh": {"mode": "interval", "intervalSeconds": 10},
            "density": "comfortable",
            "pinned": True,
            "hidden": False,
            "config": {
                "min": 0,
                "max": 100,
                "value": round(last["queuePressure"] * 100.0, 2),
                "warningThreshold": 70,
                "criticalThreshold": 90,
                "unit": "%",
            },
        },
        {
            "id": "wid_table-001",
            "kind": "table",
            "title": "Runs",
            "subtitle": "simulated queue",
            "description": "Run summaries generated from scenario distributions.",
            "refresh": {"mode": "interval", "intervalSeconds": 25},
            "density": "comfortable",
            "pinned": False,
            "hidden": False,
            "config": {
                "columns": [
                    {"key": "id", "label": "Run ID", "align": "left", "width": 180, "sortable": True, "truncation": "line"},
                    {
                        "key": "name",
                        "label": "Name",
                        "align": "left",
                        "width": 260,
                        "sortable": True,
                        "truncation": "line",
                    },
                    {
                        "key": "status",
                        "label": "Status",
                        "align": "center",
                        "width": 120,
                        "sortable": True,
                        "truncation": "none",
                    },
                    {
                        "key": "priority",
                        "label": "Priority",
                        "align": "center",
                        "width": 120,
                        "sortable": True,
                        "truncation": "none",
                    },
                    {
                        "key": "percent",
                        "label": "Progress %",
                        "align": "right",
                        "width": 140,
                        "sortable": True,
                        "truncation": "none",
                    },
                ],
                "rowKey": "id",
                "maxRows": max(20, min(250, len(runs))),
                "striped": True,
                "stickyHeader": True,
            },
        },
        {
            "id": "wid_feed-001",
            "kind": "feed",
            "title": "Activity",
            "subtitle": "events",
            "description": "Recent event feed for operational timeline.",
            "refresh": {"mode": "interval", "intervalSeconds": 12},
            "density": "comfortable",
            "pinned": True,
            "hidden": False,
            "config": {
                "source": "activity",
                "maxItems": 60,
                "showSeverity": True,
                "compactTimestamps": True,
            },
        },
        {
            "id": "wid_chart-001",
            "kind": "chart-placeholder",
            "title": "Latency Envelope",
            "subtitle": "p50/p95/p99",
            "description": "Placeholder chart config with deterministic series names.",
            "refresh": {"mode": "manual", "intervalSeconds": None},
            "density": "spacious",
            "pinned": False,
            "hidden": False,
            "config": {
                "chartFamily": "line",
                "xLabel": "minute",
                "yLabel": "ms",
                "seriesNames": ["p50", "p95", "p99"],
                "supportsStacking": False,
            },
        },
    ]

    extra_stats = min(6, max(0, len(runs) // 18))
    for idx in range(extra_stats):
        trend_values = queue_values[idx : idx + 12] if idx + 12 <= len(queue_values) else queue_values[-12:]
        widgets.append(
            {
                "id": f"wid_stat-{idx + 3:03d}",
                "kind": "stat",
                "title": f"Queue Window {idx + 1}",
                "subtitle": "rolling",
                "description": "Rolling queue pressure segment.",
                "refresh": {"mode": "interval", "intervalSeconds": 20},
                "density": "compact",
                "pinned": False,
                "hidden": False,
                "config": {
                    "value": round(trend_values[-1], 2),
                    "unit": "%",
                    "trend": "up" if trend_values[-1] >= trend_values[0] else "down",
                    "precision": 2,
                    "sparkline": [round(value, 2) for value in trend_values],
                },
            }
        )

    widgets.sort(key=lambda item: item["id"])
    return widgets


def _generate_layout(widgets: list[dict[str, Any]]) -> dict[str, Any]:
    widget_ids = [widget["id"] for widget in widgets]

    def make_items(columns: int, per_row: int, panel_h: int) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for idx, widget_id in enumerate(widget_ids):
            row = idx // per_row
            col = idx % per_row
            width = max(2, columns // per_row)
            x = col * width
            y = row * panel_h
            items.append(
                {
                    "widgetId": widget_id,
                    "position": {
                        "x": x,
                        "y": y,
                        "w": width,
                        "h": panel_h,
                        "minW": 2,
                        "minH": 2,
                        "maxW": None,
                        "maxH": None,
                    },
                    "locked": False,
                    "resizable": True,
                    "draggable": True,
                    "panelSize": "md",
                }
            )
        return items

    breakpoints = [
        {"breakpoint": "xs", "columns": 4, "rowHeight": 84, "gap": 8, "items": make_items(4, 1, 2)},
        {"breakpoint": "sm", "columns": 6, "rowHeight": 86, "gap": 10, "items": make_items(6, 2, 2)},
        {"breakpoint": "md", "columns": 12, "rowHeight": 92, "gap": 12, "items": make_items(12, 3, 2)},
        {"breakpoint": "lg", "columns": 16, "rowHeight": 96, "gap": 12, "items": make_items(16, 4, 2)},
        {"breakpoint": "xl", "columns": 20, "rowHeight": 98, "gap": 12, "items": make_items(20, 5, 2)},
    ]
    return {
        "version": 1,
        "breakpoints": breakpoints,
        "compactType": "vertical",
        "bounded": True,
        "allowOverlap": False,
    }


def generate_simulation(config: SimulationConfig) -> SimulationBundle:
    if config.scenario.run_count <= 0:
        raise ValueError("scenario run_count must be > 0")
    if config.scenario.duration_minutes <= 0:
        raise ValueError("scenario duration_minutes must be > 0")

    rng = DeterministicRng(seed=config.seed)
    series = _build_series(config=config, rng=rng)
    runs = _generate_runs(config=config, series=series, rng=rng)
    activity = _generate_activity(config=config, series=series, runs=runs, rng=rng)
    widgets = _generate_widgets(series=series, runs=runs, rng=rng)
    layout = _generate_layout(widgets=widgets)

    metadata = {
        "scenario": config.scenario.name,
        "description": config.scenario.description,
        "seed": config.seed,
        "generatedAt": _iso(config.start_at),
        "durationMinutes": config.scenario.duration_minutes,
        "runCount": len(runs),
        "activityCount": len(activity),
        "widgetCount": len(widgets),
        "seriesCount": len(series),
    }

    raw_payload = {
        "metadata": metadata,
        "series": series,
        "runs": runs,
        "activity": activity,
        "widgets": widgets,
        "layout": layout,
    }
    metadata["determinismHash"] = hash_json_stable(raw_payload)

    return SimulationBundle(
        metadata=metadata,
        series=series,
        runs=runs,
        activity=activity,
        widgets=widgets,
        layout=layout,
    )
