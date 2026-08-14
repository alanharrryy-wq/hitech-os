from __future__ import annotations

from .final_runner import run_operational_atlas

run_operational_evidence = run_operational_atlas
run_operational_evidence_atlas = run_operational_atlas
run = run_operational_atlas

__all__ = [
    "run_operational_atlas",
    "run_operational_evidence",
    "run_operational_evidence_atlas",
    "run",
]
