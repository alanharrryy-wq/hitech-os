from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import (
    ContractError,
    canonical_json,
    ensure_no_raw_secret_values,
    require_nonempty_string,
    sha256_json,
    utc_now_iso,
)

DELTA_STATUSES = {"added", "removed", "changed", "stale", "unknown", "unchanged"}
DELTA_CATEGORIES = {
    "appsServicesPackages",
    "architectureLayers",
    "dependencyEdges",
    "dataSchemaRelationships",
    "authorityOwnership",
    "ciTestGates",
    "protectedSensitiveScope",
    "unknownContradictoryAreas",
}
OBSERVATION_SUPPORT_LEVELS = {"SUPPORTED", "INFERRED", "UNKNOWN", "CONFLICTED"}
OBSERVED_STATE_STATUSES = {"COMPLETE", "PARTIAL", "STALE", "UNSUPPORTED", "CONFLICTED"}


def normalize_architecture_delta(*, base_snapshot: Mapping[str, Any], head_snapshot: Mapping[str, Any], categories: Mapping[str, list[Mapping[str, Any]]], provenance: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(base_snapshot, Mapping) or not isinstance(head_snapshot, Mapping):
        raise ContractError("base_snapshot and head_snapshot must be objects")
    base_repo = base_snapshot.get("repositoryIdentity")
    head_repo = head_snapshot.get("repositoryIdentity")
    if not base_repo or base_repo != head_repo:
        raise ContractError("architecture delta cannot cross repository identities")
    if not provenance:
        raise ContractError("architecture delta requires provenance")
    if not isinstance(categories, Mapping):
        raise ContractError("categories must be an object")
    unknown_categories = sorted(set(categories) - DELTA_CATEGORIES)
    if unknown_categories:
        raise ContractError(f"unsupported delta categories: {unknown_categories}")

    normalized_categories: dict[str, list[dict[str, Any]]] = {}
    material_count = 0
    for category in sorted(DELTA_CATEGORIES):
        rows = categories.get(category, [])
        if not isinstance(rows, list):
            raise ContractError(f"delta category {category} must be a list")
        out: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                raise ContractError(f"{category}[{index}] must be an object")
            status = str(row.get("status", "unknown")).lower()
            if status not in DELTA_STATUSES:
                raise ContractError(f"{category}[{index}] has invalid status")
            item = deepcopy(dict(row))
            item["status"] = status
            out.append(item)
            if status != "unchanged":
                material_count += 1
        normalized_categories[category] = out

    result = {
        "schemaVersion": "code_atlas_architecture_delta.v1",
        "repositoryIdentity": base_repo,
        "baseSnapshot": dict(base_snapshot),
        "headSnapshot": dict(head_snapshot),
        "categories": normalized_categories,
        "materialChangeCount": material_count,
        "provenance": deepcopy(provenance),
        "generatedAt": utc_now_iso(),
        "certifiable": False,
        "productionCertified": False,
    }
    result["deltaDigest"] = sha256_json(result)
    return result


def _normalized_sha256(value: Any, field: str) -> str:
    text = require_nonempty_string(value, field).lower()
    if text.startswith("sha256:"):
        raw = text.split(":", 1)[1]
    else:
        raw = text
    if len(raw) != 64 or any(ch not in "0123456789abcdef" for ch in raw):
        raise ContractError(f"{field} must be a SHA-256 digest")
    return "sha256:" + raw


def _snapshot_lineage(snapshot: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(snapshot, Mapping):
        raise ContractError(f"{field} must be an object")
    return {
        "repositoryIdentity": require_nonempty_string(snapshot.get("repositoryIdentity"), f"{field}.repositoryIdentity"),
        "commitIdentity": require_nonempty_string(snapshot.get("commitIdentity"), f"{field}.commitIdentity"),
        "treeIdentity": require_nonempty_string(snapshot.get("treeIdentity"), f"{field}.treeIdentity"),
        "snapshotDigest": _normalized_sha256(snapshot.get("snapshotDigest"), f"{field}.snapshotDigest"),
    }


def _normalize_provenance(provenance: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(provenance, list) or not provenance:
        raise ContractError("change comparison requires provenance")
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(provenance):
        if not isinstance(row, Mapping):
            raise ContractError(f"provenance[{index}] must be an object")
        item = deepcopy(dict(row))
        require_nonempty_string(item.get("source"), f"provenance[{index}].source")
        ensure_no_raw_secret_values(item, location=f"provenance[{index}]")
        normalized.append(item)
    return sorted(normalized, key=canonical_json)


def _normalize_evidence_references(value: Any, field: str) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ContractError(f"{field} must be a list")
    normalized: list[Any] = []
    for index, item in enumerate(value):
        if not isinstance(item, (str, Mapping)):
            raise ContractError(f"{field}[{index}] must be a string or object")
        if isinstance(item, str):
            normalized_item: Any = require_nonempty_string(item, f"{field}[{index}]")
        else:
            normalized_item = deepcopy(dict(item))
            if not normalized_item:
                raise ContractError(f"{field}[{index}] must not be empty")
        ensure_no_raw_secret_values(normalized_item, location=f"{field}[{index}]")
        normalized.append(normalized_item)
    return sorted(normalized, key=canonical_json)


def _normalize_observed_state(state: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(state, Mapping):
        raise ContractError(f"{field} must be an object")
    status = require_nonempty_string(state.get("stateStatus"), f"{field}.stateStatus").upper()
    if status not in OBSERVED_STATE_STATUSES:
        raise ContractError(f"{field}.stateStatus is unsupported")
    observations = state.get("observations")
    if not isinstance(observations, Mapping):
        raise ContractError(f"{field}.observations must be an object")
    unsupported_categories = sorted(set(observations) - DELTA_CATEGORIES)
    if unsupported_categories:
        raise ContractError(f"{field} has unsupported categories: {unsupported_categories}")

    by_id: dict[str, dict[str, Any]] = {}
    categories: dict[str, list[dict[str, Any]]] = {category: [] for category in sorted(DELTA_CATEGORIES)}
    for category in sorted(DELTA_CATEGORIES):
        rows = observations.get(category, [])
        if not isinstance(rows, list):
            raise ContractError(f"{field}.observations.{category} must be a list")
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                raise ContractError(f"{field}.observations.{category}[{index}] must be an object")
            oid = require_nonempty_string(row.get("id"), f"{field}.observations.{category}[{index}].id")
            if oid in by_id:
                raise ContractError(f"{field} contains duplicate observation identity: {oid}")
            support = require_nonempty_string(
                row.get("supportLevel"), f"{field}.observations.{category}[{index}].supportLevel"
            ).upper()
            if support not in OBSERVATION_SUPPORT_LEVELS:
                raise ContractError(f"{field}.observations.{category}[{index}].supportLevel is unsupported")
            payload = row.get("payload")
            if not isinstance(payload, Mapping):
                raise ContractError(f"{field}.observations.{category}[{index}].payload must be an object")
            payload_copy = deepcopy(dict(payload))
            ensure_no_raw_secret_values(payload_copy, location=f"{field}.observations.{category}[{index}].payload")
            refs = _normalize_evidence_references(
                row.get("evidenceReferences"), f"{field}.observations.{category}[{index}].evidenceReferences"
            )
            item = {
                "id": oid,
                "category": category,
                "payload": payload_copy,
                "payloadDigest": sha256_json(payload_copy),
                "supportLevel": support,
                "evidenceReferences": refs,
            }
            by_id[oid] = item
            categories[category].append(item)
        categories[category].sort(key=lambda item: item["id"])

    deterministic = {
        "stateStatus": status,
        "observations": {
            category: categories[category]
            for category in sorted(categories)
            if categories[category]
        },
    }
    return {
        "stateStatus": status,
        "byId": by_id,
        "stateDigest": sha256_json(deterministic),
    }


def _state_problem(state: Mapping[str, Any], side: str) -> tuple[str | None, str | None]:
    status = str(state.get("stateStatus") or "")
    if status == "STALE":
        return "BLOCKED", f"STALE_STATE:{side}"
    if status == "CONFLICTED":
        return "BLOCKED", f"CONFLICTED_STATE:{side}"
    if status == "PARTIAL":
        return "UNKNOWN", f"PARTIAL_STATE:{side}"
    if status == "UNSUPPORTED":
        return "UNKNOWN", f"UNSUPPORTED_STATE:{side}"
    return None, None


def _observation_problem(observation: Mapping[str, Any], side: str) -> tuple[str | None, list[str]]:
    oid = str(observation.get("id"))
    support = str(observation.get("supportLevel") or "")
    reasons: list[str] = []
    decision: str | None = None
    if support == "CONFLICTED":
        decision = "BLOCKED"
        reasons.append(f"CONFLICTED_EVIDENCE:{side}:{oid}")
    elif support == "UNKNOWN":
        decision = "UNKNOWN"
        reasons.append(f"UNKNOWN_EVIDENCE:{side}:{oid}")
    elif support == "INFERRED":
        decision = "UNKNOWN"
        reasons.append(f"INFERRED_NOT_PROOF:{side}:{oid}")
    if support == "SUPPORTED" and not observation.get("evidenceReferences"):
        decision = "UNKNOWN"
        reasons.append(f"MISSING_CRITICAL_EVIDENCE:{side}:{oid}")
    return decision, reasons


def _append_unknown_row(
    categories: dict[str, list[dict[str, Any]]],
    *,
    oid: str,
    reasons: list[str],
    base: Mapping[str, Any] | None,
    head: Mapping[str, Any] | None,
) -> None:
    categories["unknownContradictoryAreas"].append(
        {
            "id": oid,
            "status": "unknown",
            "reasonCodes": sorted(set(reasons)),
            "basePayloadDigest": base.get("payloadDigest") if base else None,
            "headPayloadDigest": head.get("payloadDigest") if head else None,
        }
    )


def compare_observed_states(
    *,
    base_snapshot: Mapping[str, Any],
    head_snapshot: Mapping[str, Any],
    base_state: Mapping[str, Any],
    head_state: Mapping[str, Any],
    provenance: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compare two bounded evidence states without owning snapshot or authority truth.

    The caller supplies snapshot lineage and evidence-bearing observations. This
    adapter derives a deterministic comparison only; it never authorizes mutation
    and never promotes inferred, missing, stale, partial or conflicted evidence to
    green.
    """
    base_lineage = _snapshot_lineage(base_snapshot, "base_snapshot")
    head_lineage = _snapshot_lineage(head_snapshot, "head_snapshot")
    if base_lineage["repositoryIdentity"] != head_lineage["repositoryIdentity"]:
        raise ContractError("change comparison cannot cross repository identities")
    normalized_provenance = _normalize_provenance(provenance)
    normalized_base = _normalize_observed_state(base_state, "base_state")
    normalized_head = _normalize_observed_state(head_state, "head_state")

    categories: dict[str, list[dict[str, Any]]] = {category: [] for category in sorted(DELTA_CATEGORIES)}
    blocking_reasons: list[str] = []
    unknown_reasons: list[str] = []

    for state, side in ((normalized_base, "base"), (normalized_head, "head")):
        decision, reason = _state_problem(state, side)
        if reason:
            if decision == "BLOCKED":
                blocking_reasons.append(reason)
            else:
                unknown_reasons.append(reason)

    state_is_comparable = not blocking_reasons and not unknown_reasons
    if not state_is_comparable:
        reasons = sorted(set(blocking_reasons + unknown_reasons))
        categories["unknownContradictoryAreas"].append(
            {
                "id": "state-completeness",
                "status": "stale" if blocking_reasons else "unknown",
                "reasonCodes": reasons,
            }
        )
    else:
        base_by_id = normalized_base["byId"]
        head_by_id = normalized_head["byId"]
        for oid in sorted(set(base_by_id) | set(head_by_id)):
            before = base_by_id.get(oid)
            after = head_by_id.get(oid)
            local_blocking: list[str] = []
            local_unknown: list[str] = []
            for observation, side in ((before, "base"), (after, "head")):
                if observation is None:
                    continue
                decision, reasons = _observation_problem(observation, side)
                if decision == "BLOCKED":
                    local_blocking.extend(reasons)
                elif decision == "UNKNOWN":
                    local_unknown.extend(reasons)
            if local_blocking or local_unknown:
                blocking_reasons.extend(local_blocking)
                unknown_reasons.extend(local_unknown)
                _append_unknown_row(
                    categories,
                    oid=oid,
                    reasons=local_blocking + local_unknown,
                    base=before,
                    head=after,
                )
                continue

            if before is None and after is not None:
                categories[after["category"]].append(
                    {
                        "id": oid,
                        "status": "added",
                        "after": deepcopy(after["payload"]),
                        "afterDigest": after["payloadDigest"],
                        "evidenceReferences": deepcopy(after["evidenceReferences"]),
                    }
                )
                continue
            if before is not None and after is None:
                categories[before["category"]].append(
                    {
                        "id": oid,
                        "status": "removed",
                        "before": deepcopy(before["payload"]),
                        "beforeDigest": before["payloadDigest"],
                        "evidenceReferences": deepcopy(before["evidenceReferences"]),
                    }
                )
                continue
            if before is None or after is None:
                raise ContractError("observation comparison invariant violated")
            if before["category"] != after["category"]:
                categories[before["category"]].append(
                    {
                        "id": oid,
                        "status": "removed",
                        "before": deepcopy(before["payload"]),
                        "beforeDigest": before["payloadDigest"],
                        "evidenceReferences": deepcopy(before["evidenceReferences"]),
                        "reason": "observation category changed",
                    }
                )
                categories[after["category"]].append(
                    {
                        "id": oid,
                        "status": "added",
                        "after": deepcopy(after["payload"]),
                        "afterDigest": after["payloadDigest"],
                        "evidenceReferences": deepcopy(after["evidenceReferences"]),
                        "reason": "observation category changed",
                    }
                )
                continue
            merged_refs = sorted(
                deepcopy(before["evidenceReferences"] + after["evidenceReferences"]),
                key=canonical_json,
            )
            if before["payloadDigest"] == after["payloadDigest"]:
                categories[before["category"]].append(
                    {
                        "id": oid,
                        "status": "unchanged",
                        "value": deepcopy(after["payload"]),
                        "valueDigest": after["payloadDigest"],
                        "evidenceReferences": merged_refs,
                    }
                )
            else:
                categories[before["category"]].append(
                    {
                        "id": oid,
                        "status": "changed",
                        "before": deepcopy(before["payload"]),
                        "after": deepcopy(after["payload"]),
                        "beforeDigest": before["payloadDigest"],
                        "afterDigest": after["payloadDigest"],
                        "evidenceReferences": merged_refs,
                    }
                )

    for rows in categories.values():
        rows.sort(key=lambda row: (str(row.get("id") or ""), str(row.get("status") or ""), canonical_json(row)))

    normalized_delta = normalize_architecture_delta(
        base_snapshot=base_lineage,
        head_snapshot=head_lineage,
        categories=categories,
        provenance=normalized_provenance,
    )
    deterministic_delta = {
        "schemaVersion": normalized_delta["schemaVersion"],
        "repositoryIdentity": normalized_delta["repositoryIdentity"],
        "baseSnapshot": normalized_delta["baseSnapshot"],
        "headSnapshot": normalized_delta["headSnapshot"],
        "categories": normalized_delta["categories"],
        "materialChangeCount": normalized_delta["materialChangeCount"],
        "provenance": normalized_delta["provenance"],
        "certifiable": False,
        "productionCertified": False,
    }
    decision = "BLOCKED" if blocking_reasons else "UNKNOWN" if unknown_reasons else "PASS"
    reason_codes = sorted(set(blocking_reasons + unknown_reasons))
    result = {
        "schemaVersion": "code_atlas_observed_change_comparison.v1",
        "decision": decision,
        "repositoryIdentity": base_lineage["repositoryIdentity"],
        "baseSnapshotLineage": base_lineage,
        "headSnapshotLineage": head_lineage,
        "baseStateDigest": normalized_base["stateDigest"],
        "headStateDigest": normalized_head["stateDigest"],
        "reasonCodes": reason_codes,
        "architectureDelta": deterministic_delta,
        "readOnly": True,
        "authorizesMutation": False,
        "impactRadiusIsAuthorization": False,
        "retrievalIsProof": False,
        "certifiable": False,
        "productionCertified": False,
    }
    result["comparisonDigest"] = sha256_json(result)
    return result
