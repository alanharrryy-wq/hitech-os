from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Mapping

from .contracts import (
    DECISIONS,
    ContractError,
    decision_precedence,
    ensure_no_raw_secret_values,
    normalize_scope,
    require_exact_digest,
    require_nonempty_string,
    require_string_list,
    sha256_json,
    utc_now_iso,
)

PACKET_SCHEMA = "prisma.change_assurance.packet.v1"
PRODUCT_NAME = "PRISMA Change Assurance"
ENGINE_NAME = "Code Atlas"
PRINCIPLE = "No evidence. No green."
STAGES = ("UNDERSTAND", "RESOLVE", "AUTHORIZE", "OBSERVE", "VERIFY", "PROVE")
DRIFT_CLASSIFICATIONS = {
    "PASS_ALREADY_CURRENT",
    "PASS_NO_RELEVANT_DRIFT",
    "BLOCKED_RELEVANT_DRIFT",
    "BLOCKED_NON_ANCESTOR_DRIFT",
}
CLAIM_STATES = {"SUPPORTED", "BLOCKED", "UNKNOWN"}
EXTERNAL_STATES = {"DONE", "PARTIAL", "BLOCKED", "NOT_EVALUATED"}
EXPECTED_CHAIN = (
    ("Code Atlas", "PRISMA Change Assurance"),
    ("PRISMA Change Assurance", "Authority Mesh"),
    ("Authority Mesh", "gates"),
    ("gates", "Evidence Bundle"),
    ("Evidence Bundle", "Factory Ledger"),
)


def _sha(value: Any, field: str, *, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    text = require_nonempty_string(value, field)
    if not re.fullmatch(r"[0-9a-f]{40}", text):
        raise ContractError(f"{field} must be an exact 40-character lowercase Git SHA")
    return text


def _snapshot(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{field} must be an object")
    normalized = {
        "repositoryIdentity": require_nonempty_string(value.get("repositoryIdentity"), f"{field}.repositoryIdentity"),
        "commitIdentity": _sha(value.get("commitIdentity"), f"{field}.commitIdentity"),
        "treeIdentity": _sha(value.get("treeIdentity"), f"{field}.treeIdentity"),
    }
    ensure_no_raw_secret_values(normalized, location=field)
    return normalized


def _evidence(values: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(values, list) or not values:
        raise ContractError("evidence must contain at least one evidence descriptor")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(values):
        if not isinstance(raw, Mapping):
            raise ContractError(f"evidence[{index}] must be an object")
        evidence_id = require_nonempty_string(raw.get("id"), f"evidence[{index}].id")
        if evidence_id in seen:
            raise ContractError(f"duplicate evidence id: {evidence_id}")
        seen.add(evidence_id)
        row = {
            "id": evidence_id,
            "kind": require_nonempty_string(raw.get("kind"), f"evidence[{index}].kind"),
            "reference": require_nonempty_string(raw.get("reference"), f"evidence[{index}].reference"),
        }
        if raw.get("digest") is not None:
            row["digest"] = require_exact_digest(raw.get("digest"), f"evidence[{index}].digest")
        normalized.append(row)
    ensure_no_raw_secret_values(normalized, location="evidence")
    return sorted(normalized, key=lambda row: row["id"])


def _verification(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError("verification must be an object")
    decision = require_nonempty_string(value.get("decision"), "verification.decision").upper()
    if decision not in DECISIONS:
        raise ContractError(f"unsupported verification decision: {decision}")
    refs = sorted(set(require_string_list(value.get("evidenceReferences"), "verification.evidenceReferences")))
    if decision == "PASS" and not refs:
        raise ContractError("PASS verification requires evidenceReferences")
    normalized: dict[str, Any] = {"decision": decision, "evidenceReferences": refs}
    if value.get("reportDigest") is not None:
        normalized["reportDigest"] = require_exact_digest(value.get("reportDigest"), "verification.reportDigest")
    ensure_no_raw_secret_values(normalized, location="verification")
    return normalized


def _integration_chain(values: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(values, list) or len(values) != len(EXPECTED_CHAIN):
        raise ContractError("integrationChain must contain the five canonical producer/consumer hops")
    normalized: list[dict[str, Any]] = []
    for index, ((expected_producer, expected_consumer), raw) in enumerate(zip(EXPECTED_CHAIN, values)):
        if not isinstance(raw, Mapping):
            raise ContractError(f"integrationChain[{index}] must be an object")
        producer = require_nonempty_string(raw.get("producer"), f"integrationChain[{index}].producer")
        consumer = require_nonempty_string(raw.get("consumer"), f"integrationChain[{index}].consumer")
        if (producer, consumer) != (expected_producer, expected_consumer):
            raise ContractError(
                f"integrationChain[{index}] must be {expected_producer} -> {expected_consumer}"
            )
        refs = sorted(set(require_string_list(
            raw.get("evidenceReferences"),
            f"integrationChain[{index}].evidenceReferences",
            allow_empty=False,
        )))
        normalized.append({
            "producer": producer,
            "consumer": consumer,
            "contract": require_nonempty_string(raw.get("contract"), f"integrationChain[{index}].contract"),
            "binding": require_nonempty_string(raw.get("binding"), f"integrationChain[{index}].binding"),
            "evidenceReferences": refs,
        })
    ensure_no_raw_secret_values(normalized, location="integrationChain")
    return normalized


def _claim_evidence(values: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise ContractError("claimEvidence must be a list")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(values):
        if not isinstance(raw, Mapping):
            raise ContractError(f"claimEvidence[{index}] must be an object")
        claim = require_nonempty_string(raw.get("claim"), f"claimEvidence[{index}].claim")
        if claim in seen:
            raise ContractError(f"duplicate commercial claim: {claim}")
        seen.add(claim)
        status = require_nonempty_string(raw.get("status"), f"claimEvidence[{index}].status").upper()
        if status not in CLAIM_STATES:
            raise ContractError(f"unsupported claim status: {status}")
        refs = sorted(set(require_string_list(raw.get("evidenceReferences"), f"claimEvidence[{index}].evidenceReferences")))
        if status == "SUPPORTED" and not refs:
            raise ContractError(f"SUPPORTED commercial claim requires evidence: {claim}")
        row = {"claim": claim, "status": status, "evidenceReferences": refs}
        if status != "SUPPORTED":
            row["reason"] = require_nonempty_string(raw.get("reason"), f"claimEvidence[{index}].reason")
        normalized.append(row)
    ensure_no_raw_secret_values(normalized, location="claimEvidence")
    return normalized


def _external_validation(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError("externalValidation must be an object")
    normalized: dict[str, Any] = {}
    for gate in ("G", "J"):
        raw = value.get(gate)
        if not isinstance(raw, Mapping):
            raise ContractError(f"externalValidation.{gate} must be an object")
        status = require_nonempty_string(raw.get("status"), f"externalValidation.{gate}.status").upper()
        if status not in EXTERNAL_STATES:
            raise ContractError(f"unsupported external validation status for {gate}: {status}")
        refs = sorted(set(require_string_list(
            raw.get("evidenceReferences"),
            f"externalValidation.{gate}.evidenceReferences",
        )))
        if status == "DONE" and not refs:
            raise ContractError(f"external validation {gate}=DONE requires evidence")
        normalized[gate] = {"status": status, "evidenceReferences": refs}
    ensure_no_raw_secret_values(normalized, location="externalValidation")
    return normalized


def _post_merge_proof(value: Mapping[str, Any] | None, merge_sha: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ContractError("postMergeProof must be an object")
    proof_merge = _sha(value.get("mergeSha"), "postMergeProof.mergeSha")
    if merge_sha is None or proof_merge != merge_sha:
        raise ContractError("postMergeProof.mergeSha must match mergeSha")
    decision = require_nonempty_string(value.get("decision"), "postMergeProof.decision").upper()
    if decision not in DECISIONS:
        raise ContractError(f"unsupported post-merge decision: {decision}")
    refs = sorted(set(require_string_list(
        value.get("evidenceReferences"),
        "postMergeProof.evidenceReferences",
        allow_empty=False,
    )))
    normalized = {"mergeSha": proof_merge, "decision": decision, "evidenceReferences": refs}
    if value.get("digest") is not None:
        normalized["digest"] = require_exact_digest(value.get("digest"), "postMergeProof.digest")
    ensure_no_raw_secret_values(normalized, location="postMergeProof")
    return normalized


def _derive_readiness(
    decision: str,
    exact_pr_sha: str | None,
    merge_sha: str | None,
    post_merge: Mapping[str, Any] | None,
    external: Mapping[str, Any],
) -> str:
    if decision == "BLOCKED":
        return "BLOCKED"
    if decision == "UNKNOWN":
        return "UNKNOWN"
    post_merge_pass = bool(
        exact_pr_sha
        and merge_sha
        and post_merge
        and post_merge.get("decision") == "PASS"
        and post_merge.get("mergeSha") == merge_sha
    )
    if not post_merge_pass:
        return "TECHNICAL_COMMERCIALIZATION_CANDIDATE"
    if external["G"]["status"] == "DONE" and external["J"]["status"] == "DONE":
        return "COMMERCIALIZATION_READY"
    return "TECHNICAL_COMMERCIALIZATION_READY"


def build_change_assurance_packet(
    *,
    analyzed_change: Mapping[str, Any],
    impact_radius: Mapping[str, Any],
    authorized_snapshot: Mapping[str, Any],
    current_snapshot: Mapping[str, Any],
    drift_classification: str,
    affected_authority: list[str],
    protected_scope: list[str],
    provenance: Mapping[str, Any],
    evidence: list[Mapping[str, Any]],
    unknowns: list[str],
    verification: Mapping[str, Any],
    integration_chain: list[Mapping[str, Any]],
    claim_evidence: list[Mapping[str, Any]],
    external_validation: Mapping[str, Any],
    exact_pr_sha: str | None = None,
    merge_sha: str | None = None,
    post_merge_proof: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not isinstance(analyzed_change, Mapping):
        raise ContractError("analyzedChange must be an object")
    if not isinstance(impact_radius, Mapping):
        raise ContractError("impactRadius must be an object")
    if not isinstance(provenance, Mapping) or not provenance:
        raise ContractError("provenance must be a non-empty object")

    analyzed = deepcopy(dict(analyzed_change))
    analyzed["summary"] = require_nonempty_string(analyzed.get("summary"), "analyzedChange.summary")
    analyzed["repositoryIdentity"] = require_nonempty_string(
        analyzed.get("repositoryIdentity"), "analyzedChange.repositoryIdentity"
    )
    analyzed["changedPaths"] = normalize_scope(analyzed.get("changedPaths") or [])
    ensure_no_raw_secret_values(analyzed, location="analyzedChange")

    impact = deepcopy(dict(impact_radius))
    impact["summary"] = require_nonempty_string(impact.get("summary"), "impactRadius.summary")
    impact["affectedPaths"] = normalize_scope(impact.get("affectedPaths") or [])
    ensure_no_raw_secret_values(impact, location="impactRadius")

    authorized = _snapshot(authorized_snapshot, "authorizedSnapshot")
    current = _snapshot(current_snapshot, "currentSnapshot")
    classification = require_nonempty_string(drift_classification, "driftClassification").upper()
    if classification not in DRIFT_CLASSIFICATIONS:
        raise ContractError(f"unsupported drift classification: {classification}")
    if classification == "PASS_ALREADY_CURRENT" and authorized != current:
        raise ContractError("PASS_ALREADY_CURRENT requires authorizedSnapshot == currentSnapshot")

    affected = sorted(set(require_string_list(affected_authority, "affectedAuthority")))
    protected = normalize_scope(protected_scope)
    normalized_unknowns = sorted(set(require_string_list(unknowns, "unknowns")))
    normalized_verification = _verification(verification)
    normalized_evidence = _evidence(evidence)
    normalized_chain = _integration_chain(integration_chain)
    normalized_claims = _claim_evidence(claim_evidence)
    normalized_external = _external_validation(external_validation)

    exact_pr = _sha(exact_pr_sha, "exactPrSha", allow_none=True)
    merge = _sha(merge_sha, "mergeSha", allow_none=True)
    post_merge = _post_merge_proof(post_merge_proof, merge)

    drift_decision = "BLOCKED" if classification.startswith("BLOCKED_") else "PASS"
    unknown_decision = "UNKNOWN" if normalized_unknowns else "PASS"
    decision = decision_precedence(normalized_verification["decision"], drift_decision, unknown_decision)
    readiness = _derive_readiness(decision, exact_pr, merge, post_merge, normalized_external)

    if not isinstance(provenance, Mapping):
        raise ContractError("provenance must be an object")
    normalized_provenance = deepcopy(dict(provenance))
    ensure_no_raw_secret_values(normalized_provenance, location="provenance")

    packet = {
        "schemaVersion": PACKET_SCHEMA,
        "product": {
            "productName": PRODUCT_NAME,
            "engineName": ENGINE_NAME,
            "principle": PRINCIPLE,
            "stages": list(STAGES),
        },
        "decision": decision,
        "readiness": readiness,
        "analyzedChange": analyzed,
        "impactRadius": impact,
        "authorizedSnapshot": authorized,
        "currentSnapshot": current,
        "driftClassification": classification,
        "affectedAuthority": affected,
        "protectedScope": protected,
        "provenance": normalized_provenance,
        "evidence": normalized_evidence,
        "unknowns": normalized_unknowns,
        "verification": normalized_verification,
        "integrationChain": normalized_chain,
        "claimEvidence": normalized_claims,
        "exactPrSha": exact_pr,
        "mergeSha": merge,
        "postMergeProof": post_merge,
        "externalValidation": normalized_external,
        "externalValidationPending": [
            gate for gate in ("G", "J") if normalized_external[gate]["status"] != "DONE"
        ],
        "productionCertified": False,
        "generatedAt": generated_at or utc_now_iso(),
    }
    ensure_no_raw_secret_values(packet)
    packet["packetDigest"] = sha256_json(packet)
    return packet


def render_change_assurance_packet_markdown(packet: Mapping[str, Any]) -> str:
    if not isinstance(packet, Mapping) or packet.get("schemaVersion") != PACKET_SCHEMA:
        raise ContractError("unsupported Change Assurance Packet")
    lines = [
        "# PRISMA Change Assurance Packet V1",
        "",
        f"Decision: **{packet.get('decision', 'UNKNOWN')}**",
        f"Readiness: **{packet.get('readiness', 'UNKNOWN')}**",
        f"Drift: **{packet.get('driftClassification', 'UNKNOWN')}**",
        f"Exact PR SHA: `{packet.get('exactPrSha') or 'PENDING'}`",
        f"Merge SHA: `{packet.get('mergeSha') or 'PENDING'}`",
        "",
        "## Change",
        str(packet.get("analyzedChange", {}).get("summary", "")),
        "",
        "## Impact radius",
        str(packet.get("impactRadius", {}).get("summary", "")),
        "",
        "## Protected scope",
    ]
    lines.extend([f"- `{path}`" for path in packet.get("protectedScope", [])] or ["- None"])
    lines += ["", "## Unknowns"]
    lines.extend([f"- {value}" for value in packet.get("unknowns", [])] or ["- None"])
    lines += ["", "## Commercial claims"]
    claims = packet.get("claimEvidence", [])
    lines.extend(
        [f"- **{row.get('status')}**: {row.get('claim')}" for row in claims]
        or ["- None"]
    )
    lines += [
        "",
        "## External validation",
        f"- G: **{packet.get('externalValidation', {}).get('G', {}).get('status', 'NOT_EVALUATED')}**",
        f"- J: **{packet.get('externalValidation', {}).get('J', {}).get('status', 'NOT_EVALUATED')}**",
        "",
        f"Packet digest: `{packet.get('packetDigest', '')}`",
        "",
    ]
    return "\n".join(lines)


__all__ = [
    "PACKET_SCHEMA",
    "build_change_assurance_packet",
    "render_change_assurance_packet_markdown",
]
