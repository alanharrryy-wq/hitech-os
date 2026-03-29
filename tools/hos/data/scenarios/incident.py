#!/usr/bin/env python3
from __future__ import annotations

from tools.hos.data.simulator_core import ScenarioDefinition

SCENARIO = ScenarioDefinition(
    name="incident",
    description="Live incident window with high queue pressure and critical event density.",
    run_count=108,
    duration_minutes=240,
    baseline_cpu=84.0,
    baseline_memory_mb=27_500.0,
    baseline_throughput=3_200.0,
    baseline_latency_ms=420.0,
    error_ratio=0.13,
    critical_event_ratio=0.26,
    burst_chance=0.26,
    burst_scale=1.8,
    queue_pressure_base=0.82,
    recovery_bias=0.0,
)

