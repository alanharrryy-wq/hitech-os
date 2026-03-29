#!/usr/bin/env python3
from __future__ import annotations

from tools.hos.data.simulator_core import ScenarioDefinition

SCENARIO = ScenarioDefinition(
    name="recovery",
    description="Post-incident recovery with improving success rates and dropping queue pressure.",
    run_count=88,
    duration_minutes=360,
    baseline_cpu=66.0,
    baseline_memory_mb=19_300.0,
    baseline_throughput=5_400.0,
    baseline_latency_ms=210.0,
    error_ratio=0.045,
    critical_event_ratio=0.08,
    burst_chance=0.09,
    burst_scale=0.85,
    queue_pressure_base=0.57,
    recovery_bias=0.34,
)

