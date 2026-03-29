#!/usr/bin/env python3
from __future__ import annotations

from tools.hos.data.simulator_core import ScenarioDefinition

SCENARIO = ScenarioDefinition(
    name="degraded",
    description="Sustained degraded behavior with elevated latency and moderate failure pressure.",
    run_count=74,
    duration_minutes=420,
    baseline_cpu=71.0,
    baseline_memory_mb=21_800.0,
    baseline_throughput=4_600.0,
    baseline_latency_ms=238.0,
    error_ratio=0.052,
    critical_event_ratio=0.12,
    burst_chance=0.14,
    burst_scale=1.05,
    queue_pressure_base=0.63,
    recovery_bias=0.04,
)

