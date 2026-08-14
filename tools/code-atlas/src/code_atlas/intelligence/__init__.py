"""Repository-neutral intelligence primitives.

The package discovers repository facts, authority candidates, system graphs,
coverage, derived query indexes, and portable snapshots without selecting any
product adapter.
"""
from .engine import IntelligenceRequest, run_intelligence
from .authority import AUTHORITY_STATES, AuthorityRequirementError
from .snapshot import assess_snapshot_freshness

__all__ = [
    "AUTHORITY_STATES",
    "AuthorityRequirementError",
    "IntelligenceRequest",
    "assess_snapshot_freshness",
    "run_intelligence",
]
