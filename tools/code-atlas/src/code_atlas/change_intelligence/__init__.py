"""Neutral customer-facing change intelligence contracts.

This package composes evidence-bearing repository intelligence without owning
repository discovery, authority resolution, graphs, snapshots, indexing or drift.
"""

from .architecture_delta import compare_observed_states, normalize_architecture_delta
from .assurance_packet import build_change_assurance_packet, render_change_assurance_packet_markdown
from .artifact_hygiene import cleanup_published_artifacts, sanitize_artifact_bytes, sanitize_artifacts_for_egress
from .authority_pack import build_authority_pack, validate_authority_pack
from .bundle import build_hardened_portable_bundle_manifest, build_portable_bundle_manifest
from .change_studio import compose_change_model
from .connector_parsers import normalize_ci_result, parse_codeowners, parse_coverage_summary, parse_junit_xml, parse_sarif
from .connectors import build_connector_envelope, validate_connector_envelope
from .customer_lifecycle import (
    build_customer_lifecycle_policy,
    cleanup_customer_workspace,
    create_customer_workspace,
    customer_workspace_expired,
    validate_cleanup_evidence,
    validate_customer_lifecycle_policy,
)
from .evidence import normalize_evidence_answer
from .policy import validate_policy_pack
from .reporting import render_change_model_markdown, render_verification_markdown
from .roi import build_roi_event, derive_financial_estimate
from .runner_contract import build_rental_runner_plan, build_runner_plan, validate_runner_cleanup, validate_runner_egress
from .sessions import normalize_agent_session
from .universal_binding import prepare_change, verify_prepared_change
from .verification import verify_change

__all__ = [
    "build_change_assurance_packet",
    "render_change_assurance_packet_markdown",
    "build_authority_pack",
    "validate_authority_pack",
    "build_connector_envelope",
    "validate_connector_envelope",
    "compose_change_model",
    "compare_observed_states",
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
    "build_hardened_portable_bundle_manifest",
    "sanitize_artifact_bytes",
    "sanitize_artifacts_for_egress",
    "cleanup_published_artifacts",
    "build_customer_lifecycle_policy",
    "validate_customer_lifecycle_policy",
    "create_customer_workspace",
    "customer_workspace_expired",
    "cleanup_customer_workspace",
    "validate_cleanup_evidence",
    "build_roi_event",
    "derive_financial_estimate",
    "build_runner_plan",
    "build_rental_runner_plan",
    "validate_runner_egress",
    "validate_runner_cleanup",
    "normalize_agent_session",
    "prepare_change",
    "verify_prepared_change",
    "verify_change",
]
