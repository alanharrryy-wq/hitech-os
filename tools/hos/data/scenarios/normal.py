#!/usr/bin/env python3
from __future__ import annotations

from tools.hos.data.simulator_core import ScenarioDefinition

SCENARIO = ScenarioDefinition(
    name="normal",
    description="Nominal steady-state operations with small healthy variance.",
    run_count=64,
    duration_minutes=360,
    baseline_cpu=44.0,
    baseline_memory_mb=12_500.0,
    baseline_throughput=5_600.0,
    baseline_latency_ms=122.0,
    error_ratio=0.009,
    critical_event_ratio=0.03,
    burst_chance=0.045,
    burst_scale=0.6,
    queue_pressure_base=0.31,
    recovery_bias=0.05,
)

