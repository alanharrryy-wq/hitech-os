"""Neutral customer-facing change intelligence contracts.

This package composes evidence-bearing repository intelligence without owning
repository discovery, authority resolution, graphs, snapshots, indexing or drift.
"""

from .authority_pack import build_authority_pack, validate_authority_pack
from .connectors import build_connector_envelope, validate_connector_envelope
from .evidence import normalize_evidence_answer
from .policy import validate_policy_pack
from .roi import build_roi_event, derive_financial_estimate
from .sessions import normalize_agent_session
from .verification import verify_change

__all__ = [
    "build_authority_pack",
    "validate_authority_pack",
    "build_connector_envelope",
    "validate_connector_envelope",
    "normalize_evidence_answer",
    "validate_policy_pack",
    "build_roi_event",
    "derive_financial_estimate",
    "normalize_agent_session",
    "verify_change",
]
