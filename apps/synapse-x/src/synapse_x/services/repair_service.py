from __future__ import annotations

from synapse_x.engine import SynapseEngine


def run_repair(engine: SynapseEngine) -> dict:
    return engine.repair()
