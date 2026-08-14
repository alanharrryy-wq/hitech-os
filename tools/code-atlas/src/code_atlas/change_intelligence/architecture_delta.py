from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .contracts import ContractError, sha256_json, utc_now_iso

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
