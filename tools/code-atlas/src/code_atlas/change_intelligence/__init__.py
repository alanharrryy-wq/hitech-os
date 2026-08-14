"""Neutral customer-facing change intelligence contracts.

This package composes evidence-bearing repository intelligence without owning
repository discovery, authority resolution, graphs, snapshots, indexing or drift.
"""

from .architecture_delta import normalize_architecture_delta
from .authority_pack import build_authority_pack, validate_authority_pack
from .bundle import build_portable_bundle_manifest
from .change_studio import compose_change_model
from .connector_parsers import normalize_ci_result, parse_codeowners, parse_coverage_summary, parse_junit_xml, parse_sarif
from .connectors import build_connector_envelope, validate_connector_envelope
from .evidence import normalize_evidence_answer
from .policy import validate_policy_pack
from .reporting import render_change_model_markdown, render_verification_markdown
from .roi import build_roi_event, derive_financial_estimate
from .sessions import normalize_agent_session
from .verification import verify_change

__all__ = [
    "build_authority_pack",
    "validate_authority_pack",
    "build_connector_envelope",
    "validate_connector_envelope",
    "compose_change_model",
    "normalize_architecture_delta",
    "parse_junit_xml",
    "parse_sarif",
    "parse_codeowners",
    "parse_coverage_summary",
    "normalize_ci_result",
    "normalize_evidence_answer",
    "validate_policy_pack",
    "render_change_model_markdown",
    "render_verification_markdown",
    "build_portable_bundle_manifest",
    "build_roi_event",
    "derive_financial_estimate",
    "normalize_agent_session",
    "verify_change",
]
