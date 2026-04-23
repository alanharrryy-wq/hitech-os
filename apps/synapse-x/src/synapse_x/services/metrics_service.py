from __future__ import annotations

from dataclasses import dataclass

from synapse_x.engine import SynapseEngine


@dataclass(slots=True)
class MetricsRequest:
    days: int = 7


def run_metrics(engine: SynapseEngine, request: MetricsRequest | None = None) -> dict:
    payload = request or MetricsRequest()
    return engine.get_metrics(days=payload.days)
