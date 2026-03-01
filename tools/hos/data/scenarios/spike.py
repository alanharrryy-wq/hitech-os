#!/usr/bin/env python3
from __future__ import annotations

from tools.hos.data.simulator_core import ScenarioDefinition

SCENARIO = ScenarioDefinition(
    name="spike",
    description="Demand spike with intermittent throughput bursts and temporary queue inflation.",
    run_count=92,
    duration_minutes=300,
    baseline_cpu=58.0,
    baseline_memory_mb=15_900.0,
    baseline_throughput=7_300.0,
    baseline_latency_ms=148.0,
    error_ratio=0.018,
    critical_event_ratio=0.07,
    burst_chance=0.18,
    burst_scale=1.25,
    queue_pressure_base=0.48,
    recovery_bias=0.08,
)

