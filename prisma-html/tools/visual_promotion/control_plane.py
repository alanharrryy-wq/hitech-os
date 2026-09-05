from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

CANDIDATE_SCHEMA = "prisma.visual-promotion.candidate.v1"
SHARD_SCHEMA = "prisma.visual-promotion.candidate-shard.v1"
TRUTH_SCHEMA = "prisma.visual-promotion.current-truth.v1"
READINESS_SCHEMA = "prisma.visual-promotion.surface-readiness.v1"
COMPOSER_SCHEMA = "prisma.visual-promotion.composer-plan.v1"

SURFACES = ("tablet", "pc", "mobile", "shared-ui")
PROTECTED_SURFACES = ("web", "chart-lab", "control-center")
AUTHORITY_DOMAINS = (
    "ndc", "atlasfin", "identity", "rifat", "visual-control", "target-index",
    "projection-manifest", "factory-ledger", "code-atlas", "work-entry-gate", "gvae",
)
PHYSICAL = ("CURRENT", "STALE", "DRIFT", "MISSING", "NOT_APPLICABLE")
ATLASFIN_MATCH = (
    "MATCHED_EXACT", "MATCHED_FAMILY", "MATCHED_PRESET", "MATCHED_RECIPE",
    "AMBIGUOUS", "NO_MATCH", "NOT_APPLICABLE",
)
RESOLUTION = ("RESOLVED_EXISTING", "CANDIDATE_REVIEW_REQUIRED", "UNRESOLVED", "NOT_APPLICABLE")
BINDING = ("EXISTING_RESOLVED", "CANDIDATE", "BLOCKED", "NOT_APPLICABLE")
PROJECTION = ("CURRENT", "DRIFT", "MISSING", "NOT_REQUIRED", "UNRESOLVED")
PROMOTION = ("ELIGIBLE_CANDIDATE", "REGISTER_TARGET_FIRST", "BLOCKED", "NOT_APPLICABLE")
CONFIDENCE = ("low", "medium", "high", "verified")
WORK_ENTRY = ("GVAE_EXACT_APPLY", "SURFACE_BATCH_PLAN", "REGISTER_TARGET_FIRST", "BLOCKED")
NDC_EDGES = (
    "belongs_to", "scoped_by", "claims_slot", "enables", "requires", "emits", "writes", "reads",
    "updates", "projects_to", "represented_by", "derived_from", "evidenced_by", "observed_by",
    "validated_by", "curated_by", "conflicts_with", "reconciles", "monetized_by", "owned_by",
    "blocks", "supersedes", "aliases", "implements", "exports", "imports",
)

MATERIALITY_POLICY = "STANDBY_USER_INVOKED_ONLY"
MATERIALITY_BASENAME = "materiality-catalog.registry.json"
CURRENT_CENSUS_REASON = "REUSE_EXISTING_CENSUS_SEMANTIC_PROMOTION_REQUIRED"
BROAD_REDISCOVERY_REASON = "BROAD_REDISCOVERY_FORBIDDEN_CURRENT_CENSUS"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
NDC_ID = re.compile(r"^[A-Z][A-Z0-9_]*\.[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$")
QUALIFIED_REF = re.compile(r"^([a-z][a-z0-9-]*)::(.+)$")

CANDIDATE_WRITE_ROOTS = {
    "tablet": "prisma-html/governance/visual-promotion/candidates/tablet/",
    "pc": "prisma-html/governance/visual-promotion/candidates/pc/",
    "mobile": "prisma-html/governance/visual-promotion/candidates/mobile/",
    "shared-ui": "prisma-html/governance/visual-promotion/candidates/shared-ui/",
}
LANE_WRITE_ROOTS = {
    "chat1-tablet": CANDIDATE_WRITE_ROOTS["tablet"],
    "chat2-pc": CANDIDATE_WRITE_ROOTS["pc"],
    "chat3-mobile": CANDIDATE_WRITE_ROOTS["mobile"],
    "chat4-shared-ui": CANDIDATE_WRITE_ROOTS["shared-ui"],
    "chat5-atlasfin-bridge": "prisma-html/extras/atlasfin/bridge/",
    "chat6-control-plane-tools": "prisma-html/tools/visual_promotion/",
    "chat6-control-plane-contracts": "prisma-html/governance/visual-promotion/contracts/",
}


class ControlPlaneError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    if MATERIALITY_BASENAME in path.name.lower():
        raise ControlPlaneError("MATERIALITY_CATALOG_STANDBY_USER_INVOKED_ONLY")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ControlPlaneError(f"JSONL_OBJECT_REQUIRED:{path}:{line_no}")
        rows.append(value)
    return rows


def _dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ControlPlaneError(f"{label}_OBJECT_REQUIRED")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ControlPlaneError(f"{label}_ARRAY_REQUIRED")
    return value


def _enum(value: Any, allowed: Iterable[str], label: str) -> None:
    if value not in set(allowed):
        raise ControlPlaneError(f"{label}_INVALID:{value}")


def _null_or_str(value: Any, label: str) -> None:
    if value is not None and not isinstance(value, str):
        raise ControlPlaneError(f"{label}_STRING_OR_NULL_REQUIRED")


def _repo_path(value: str) -> str:
    path = str(value or "").replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    if not path or path.startswith("/") or ".." in path.split("/"):
        raise ControlPlaneError(f"UNSAFE_REPO_PATH:{value}")
    return path


def validate_authority_ref(ref: Any) -> None:
    if isinstance(ref, str):
        match = QUALIFIED_REF.fullmatch(ref)
        if not match:
            raise ControlPlaneError(f"AUTHORITY_QUALIFIED_REF_REQUIRED:{ref}")
        domain, raw_id = match.groups()
        _enum(domain, AUTHORITY_DOMAINS, "AUTHORITY_DOMAIN")
        if not raw_id.strip():
            raise ControlPlaneError("AUTHORITY_ID_REQUIRED")
        return
    obj = _dict(ref, "AUTHORITY_REF")
    unknown = set(obj) - {"authorityDomain", "id", "version", "sha256"}
    if unknown:
        raise ControlPlaneError("AUTHORITY_REF_UNKNOWN_FIELDS:" + ",".join(sorted(unknown)))
    _enum(obj.get("authorityDomain"), AUTHORITY_DOMAINS, "AUTHORITY_DOMAIN")
    if not isinstance(obj.get("id"), str) or not obj["id"].strip():
        raise ControlPlaneError("AUTHORITY_ID_REQUIRED")
    if obj.get("version") is not None and not isinstance(obj["version"], str):
        raise ControlPlaneError("AUTHORITY_VERSION_STRING_REQUIRED")
    if obj.get("sha256") is not None and not HEX64.fullmatch(str(obj["sha256"])):
        raise ControlPlaneError("AUTHORITY_SHA256_INVALID")


def validate_ndc_id(value: str, prefixes: set[str] | None = None) -> None:
    if not isinstance(value, str) or not NDC_ID.fullmatch(value):
        raise ControlPlaneError(f"NDC_ID_INVALID:{value}")
    if prefixes is not None and value.split(".", 1)[0] not in prefixes:
        raise ControlPlaneError(f"NDC_PREFIX_UNKNOWN:{value}")


def validate_edge_type(value: str, allowed_edges: set[str] | None = None) -> None:
    if value not in (allowed_edges if allowed_edges is not None else set(NDC_EDGES)):
        raise ControlPlaneError(f"NDC_EDGE_TYPE_INVALID:{value}")


def ndc_prefixes_from_registry(document: Any) -> set[str]:
    rows = _list(_dict(document, "NDC_PREFIX_REGISTRY").get("prefixes"), "NDC_PREFIXES")
    out = {str(row["prefix"]) for row in rows if isinstance(row, dict) and isinstance(row.get("prefix"), str)}
    if not out:
        raise ControlPlaneError("NDC_PREFIX_REGISTRY_EMPTY")
    return out


def ndc_edges_from_registry(document: Any) -> set[str]:
    rows = _list(_dict(document, "NDC_EDGE_REGISTRY").get("edge_types"), "NDC_EDGE_TYPES")
    out = {str(row["edge_type"]) for row in rows if isinstance(row, dict) and isinstance(row.get("edge_type"), str)}
    if not out:
        raise ControlPlaneError("NDC_EDGE_REGISTRY_EMPTY")
    return out


def validate_owned_output(surface: str, path: str) -> None:
    _enum(surface, SURFACES, "SURFACE_KEY")
    normalized = _repo_path(path)
    if not normalized.startswith(CANDIDATE_WRITE_ROOTS[surface]):
        raise ControlPlaneError(f"WRITE_OWNERSHIP_VIOLATION:{surface}:{normalized}")


def validate_disjoint_write_ownership(roots: Mapping[str, str] | None = None) -> dict[str, Any]:
    values = {lane: _repo_path(root).rstrip("/") + "/" for lane, root in dict(roots or LANE_WRITE_ROOTS).items()}
    pairs = sorted(values.items())
    for index, (lane_a, root_a) in enumerate(pairs):
        for lane_b, root_b in pairs[index + 1:]:
            if root_a.startswith(root_b) or root_b.startswith(root_a):
                raise ControlPlaneError(f"WRITE_OWNERSHIP_ROOT_COLLISION:{lane_a}:{lane_b}")
    return {"status": "PASS_DISJOINT_WRITE_OWNERSHIP", "roots": values}


def _validate_source_hash(
    candidate: dict[str, Any],
    repo_root: Path,
    path_field: str,
    hash_field: str,
    fallback_path: str | None = None,
) -> None:
    expected = candidate.get(hash_field)
    if expected is None:
        return
    if not isinstance(expected, str) or not HEX64.fullmatch(expected):
        raise ControlPlaneError(f"{hash_field.upper()}_INVALID")
    raw = candidate.get(path_field) or fallback_path
    if not isinstance(raw, str) or not raw:
        raise ControlPlaneError(f"{hash_field.upper()}_PATH_REQUIRED")
    rel = _repo_path(raw)
    path = (repo_root / rel).resolve()
    root = repo_root.resolve()
    if path != root and root not in path.parents:
        raise ControlPlaneError(f"SOURCE_PATH_ESCAPE:{rel}")
    if not path.is_file():
        raise ControlPlaneError(f"SOURCE_FILE_MISSING:{rel}")
    actual = file_sha256(path)
    if actual != expected:
        raise ControlPlaneError(f"{hash_field.upper()}_MISMATCH:{rel}")


def validate_candidate(
    candidate: Any,
    *,
    expected_head: str | None = None,
    repo_root: Path | None = None,
    atlasfin: dict[str, set[str]] | None = None,
    ndc_prefixes: set[str] | None = None,
) -> dict[str, Any]:
    c = _dict(candidate, "CANDIDATE")
    required = {
        "candidateOnly", "baseHead", "surfaceKey", "targetId", "physicalStatus", "physical",
        "ndc", "visual", "atlasfin", "identity", "application", "confidence",
        "evidenceRefs", "blockers", "notes",
    }
    missing = sorted(required - set(c))
    if missing:
        raise ControlPlaneError("CANDIDATE_MISSING_FIELDS:" + ",".join(missing))
    allowed = required | {
        "schema", "candidateFingerprint", "recordKind", "enforcement",
        "canonicalSourcePath", "generatedOutputPath", "sourceSha256",
        "outputSha256", "projectionMode",
    }
    unknown = sorted(set(c) - allowed)
    if unknown:
        raise ControlPlaneError("CANDIDATE_UNKNOWN_FIELDS:" + ",".join(unknown))
    if c.get("schema") is not None and c["schema"] != CANDIDATE_SCHEMA:
        raise ControlPlaneError("CANDIDATE_SCHEMA_INVALID")
    if c["candidateOnly"] is not True:
        raise ControlPlaneError("CANDIDATE_ONLY_REQUIRED")
    if not HEX40.fullmatch(str(c.get("baseHead") or "")):
        raise ControlPlaneError("BASE_HEAD_INVALID")
    if expected_head is not None and c["baseHead"] != expected_head:
        raise ControlPlaneError(f"BASE_HEAD_MISMATCH:{c['baseHead']}:{expected_head}")
    _enum(c.get("surfaceKey"), SURFACES, "SURFACE_KEY")
    if not isinstance(c.get("targetId"), str) or not c["targetId"]:
        raise ControlPlaneError("TARGET_ID_REQUIRED")
    _enum(c["physicalStatus"], PHYSICAL, "PHYSICAL_STATUS")
    _enum(c["confidence"], CONFIDENCE, "CONFIDENCE")

    if c["targetId"].startswith("TGT.CENSUS."):
        if c.get("recordKind") not in (None, "VISUAL_CONTROL_CENSUS_TARGET"):
            raise ControlPlaneError("CENSUS_RECORD_KIND_CONFLICT")
        if c.get("enforcement") not in (None, "DISCOVERY_ONLY"):
            raise ControlPlaneError("CENSUS_ENFORCEMENT_CONFLICT")

    physical = _dict(c["physical"], "PHYSICAL")
    physical_allowed = {
        "routeId", "regionId", "slotId", "componentId", "componentUiId", "ownerId",
        "ownerFile", "renderSourceFile", "styleSourceFile", "selector", "implementationLayerId",
    }
    if set(physical) - physical_allowed:
        raise ControlPlaneError("PHYSICAL_UNKNOWN_FIELDS:" + ",".join(sorted(set(physical) - physical_allowed)))
    for key in physical_allowed:
        _null_or_str(physical.get(key), f"PHYSICAL_{key.upper()}")

    ndc = _dict(c["ndc"], "NDC")
    if set(ndc) - {"ndcPrimaryId", "ndcRefs", "ndcResolutionStatus"}:
        raise ControlPlaneError("NDC_UNKNOWN_FIELDS")
    _null_or_str(ndc.get("ndcPrimaryId"), "NDC_PRIMARY_ID")
    refs = _list(ndc.get("ndcRefs"), "NDC_REFS")
    if any(not isinstance(value, str) for value in refs):
        raise ControlPlaneError("NDC_REFS_STRING_ARRAY_REQUIRED")
    _enum(ndc.get("ndcResolutionStatus"), RESOLUTION, "NDC_RESOLUTION_STATUS")
    for value in [x for x in [ndc.get("ndcPrimaryId"), *refs] if x is not None]:
        validate_ndc_id(value, prefixes=ndc_prefixes)

    visual = _dict(c["visual"], "VISUAL")
    if set(visual) - {"visualMeaningId", "visualMeaningCandidate", "visualMeaningStatus"}:
        raise ControlPlaneError("VISUAL_UNKNOWN_FIELDS")
    _null_or_str(visual.get("visualMeaningId"), "VISUAL_MEANING_ID")
    _null_or_str(visual.get("visualMeaningCandidate"), "VISUAL_MEANING_CANDIDATE")
    _enum(visual.get("visualMeaningStatus"), RESOLUTION, "VISUAL_MEANING_STATUS")

    af = _dict(c["atlasfin"], "ATLASFIN")
    af_fields = {
        "atlasfinCatalogElementId": "catalog", "atlasfinUiId": "ui",
        "atlasfinFamilyId": "family", "atlasfinPresetId": "preset",
        "atlasfinRecipeId": "recipe", "atlasfinLegacyRecipeId": "legacyRecipe",
        "atlasfinAdapterId": "adapter",
    }
    if set(af) - {*af_fields, "atlasfinMatchStatus"}:
        raise ControlPlaneError("ATLASFIN_UNKNOWN_FIELDS")
    for field in af_fields:
        _null_or_str(af.get(field), f"ATLASFIN_{field.upper()}")
    _enum(af.get("atlasfinMatchStatus"), ATLASFIN_MATCH, "ATLASFIN_MATCH_STATUS")
    if atlasfin is not None:
        for field, bucket in af_fields.items():
            value = af.get(field)
            if value is not None and value not in atlasfin.get(bucket, set()):
                raise ControlPlaneError(f"ATLASFIN_REFERENCE_UNKNOWN:{field}:{value}")

    identity = _dict(c["identity"], "IDENTITY")
    identity_fields = {"identityProfileId", "identityRecipeId", "identityAdapterId", "existingBindingId", "bindingCandidateKey"}
    if set(identity) - {*identity_fields, "bindingStatus"}:
        raise ControlPlaneError("IDENTITY_UNKNOWN_FIELDS")
    for field in identity_fields:
        _null_or_str(identity.get(field), f"IDENTITY_{field.upper()}")
    _enum(identity.get("bindingStatus"), BINDING, "BINDING_STATUS")

    app = _dict(c["application"], "APPLICATION")
    if set(app) - {"applicationLayerId", "projectionStatus", "promotionStatus", "workEntryDecision"}:
        raise ControlPlaneError("APPLICATION_UNKNOWN_FIELDS")
    _null_or_str(app.get("applicationLayerId"), "APPLICATION_LAYER_ID")
    _enum(app.get("projectionStatus"), PROJECTION, "PROJECTION_STATUS")
    _enum(app.get("promotionStatus"), PROMOTION, "PROMOTION_STATUS")
    _enum(app.get("workEntryDecision"), WORK_ENTRY, "WORK_ENTRY_DECISION")
    if c["targetId"].startswith("TGT.CENSUS.") and app["workEntryDecision"] == "GVAE_EXACT_APPLY":
        raise ControlPlaneError("CENSUS_CANNOT_SELF_PROMOTE_TO_APPLY_AUTHORITY")

    for field in ("evidenceRefs", "blockers", "notes"):
        values = _list(c[field], field.upper())
        if field == "evidenceRefs":
            for ref in values:
                validate_authority_ref(ref)
        elif any(not isinstance(value, str) for value in values):
            raise ControlPlaneError(f"{field.upper()}_STRING_ARRAY_REQUIRED")

    for key in ("canonicalSourcePath", "generatedOutputPath", "projectionMode"):
        _null_or_str(c.get(key), key.upper())
    for key in ("sourceSha256", "outputSha256", "candidateFingerprint"):
        value = c.get(key)
        if value is not None and (not isinstance(value, str) or not HEX64.fullmatch(value)):
            raise ControlPlaneError(f"{key.upper()}_INVALID")

    if repo_root is not None:
        root = repo_root.resolve()
        _validate_source_hash(c, root, "canonicalSourcePath", "sourceSha256", physical.get("styleSourceFile"))
        _validate_source_hash(c, root, "generatedOutputPath", "outputSha256")
    return c


def build_atlasfin_indexes(documents: Iterable[Any]) -> dict[str, set[str]]:
    indexes = {
        "catalog": set(), "ui": set(), "family": set(), "preset": set(),
        "recipe": set(), "legacyRecipe": set(), "adapter": set(),
    }
    for raw in documents:
        doc = _dict(raw, "ATLASFIN_REGISTRY")
        for section in doc.get("sections", []) if isinstance(doc.get("sections"), list) else []:
            for item in section.get("items", []) if isinstance(section, dict) else []:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    indexes["catalog"].add(item["id"])
        schema = str(doc.get("schema") or "")
        rows = doc.get("items")
        if isinstance(rows, list):
            mapping = {
                "PRISMA_VISUAL_FAMILY_REGISTRY_V1": ("family", "familyId"),
                "PRISMA_VISUAL_PRESET_REGISTRY_V1": ("preset", "presetId"),
                "PRISMA_VISUAL_RECIPE_REGISTRY_V4": ("recipe", "recipeId"),
                "PRISMA_SURFACE_ADAPTER_REGISTRY_V2": ("adapter", "id"),
            }.get(schema)
            if mapping:
                bucket, key = mapping
                indexes[bucket].update(str(row[key]) for row in rows if isinstance(row, dict) and isinstance(row.get(key), str))
        for element in doc.get("elements", []) if isinstance(doc.get("elements"), list) else []:
            if not isinstance(element, dict):
                continue
            for key, bucket in (("ui_id", "ui"), ("recipe_id", "legacyRecipe"), ("preset_id", "preset")):
                if isinstance(element.get(key), str):
                    indexes[bucket].add(element[key])
            for binding in element.get("target_bindings", []):
                if isinstance(binding, dict) and isinstance(binding.get("adapter_id"), str):
                    indexes["adapter"].add(binding["adapter_id"])
    return indexes


def load_atlasfin_indexes(paths: Iterable[Path]) -> dict[str, set[str]]:
    documents = []
    for path in paths:
        if MATERIALITY_BASENAME in path.name.lower():
            raise ControlPlaneError("MATERIALITY_CATALOG_STANDBY_USER_INVOKED_ONLY")
        documents.append(load_json(path))
    return build_atlasfin_indexes(documents)


def normalize_atlasfin(candidate: dict[str, Any], indexes: dict[str, set[str]]) -> dict[str, Any]:
    af = _dict(candidate.get("atlasfin"), "ATLASFIN")
    status = af.get("atlasfinMatchStatus")
    _enum(status, ATLASFIN_MATCH, "ATLASFIN_MATCH_STATUS")
    if status in {"AMBIGUOUS", "NO_MATCH", "NOT_APPLICABLE"}:
        return {"matchStatus": status, "qualifiedRefs": [], "materialityFallbackUsed": False}
    choices = {
        "MATCHED_EXACT": (("atlasfinCatalogElementId", "catalog"), ("atlasfinUiId", "ui")),
        "MATCHED_FAMILY": (("atlasfinFamilyId", "family"),),
        "MATCHED_PRESET": (("atlasfinPresetId", "preset"),),
        "MATCHED_RECIPE": (("atlasfinRecipeId", "recipe"), ("atlasfinLegacyRecipeId", "legacyRecipe")),
    }[status]
    matched = [
        af[field] for field, bucket in choices
        if isinstance(af.get(field), str) and af[field] in indexes.get(bucket, set())
    ]
    if not matched:
        raise ControlPlaneError(f"ATLASFIN_MATCH_UNPROVEN:{status}")
    return {
        "matchStatus": status,
        "qualifiedRefs": [{"authorityDomain": "atlasfin", "id": value} for value in sorted(set(matched))],
        "materialityFallbackUsed": False,
    }


def candidate_fingerprint(candidate: dict[str, Any]) -> str:
    return digest({
        "surfaceKey": candidate.get("surfaceKey"),
        "targetId": candidate.get("targetId"),
        "ndcPrimaryId": candidate.get("ndc", {}).get("ndcPrimaryId"),
        "ndcRefs": sorted(candidate.get("ndc", {}).get("ndcRefs") or []),
        "visualMeaningId": candidate.get("visual", {}).get("visualMeaningId"),
        "visualMeaningCandidate": candidate.get("visual", {}).get("visualMeaningCandidate"),
        "atlasfinCatalogElementId": candidate.get("atlasfin", {}).get("atlasfinCatalogElementId"),
        "atlasfinFamilyId": candidate.get("atlasfin", {}).get("atlasfinFamilyId"),
        "atlasfinPresetId": candidate.get("atlasfin", {}).get("atlasfinPresetId"),
        "atlasfinRecipeId": candidate.get("atlasfin", {}).get("atlasfinRecipeId"),
        "routeId": candidate.get("physical", {}).get("routeId"),
        "regionId": candidate.get("physical", {}).get("regionId"),
        "slotId": candidate.get("physical", {}).get("slotId"),
        "selector": candidate.get("physical", {}).get("selector"),
    })


def accounting_bucket(candidate: dict[str, Any]) -> str:
    app = candidate["application"]
    if app["promotionStatus"] == "ELIGIBLE_CANDIDATE":
        return "candidateResolved"
    if (
        candidate["ndc"]["ndcResolutionStatus"] == "UNRESOLVED"
        or candidate["visual"]["visualMeaningStatus"] == "UNRESOLVED"
        or app["projectionStatus"] == "UNRESOLVED"
    ):
        return "unresolved"
    return "blockedNotApplicable"


def validate_shard(
    manifest: Any,
    outcomes: Iterable[Any],
    *,
    expected_head: str | None = None,
    repo_root: Path | None = None,
    atlasfin: dict[str, set[str]] | None = None,
    ndc_prefixes: set[str] | None = None,
    changed_paths: Iterable[str] = (),
) -> dict[str, Any]:
    m = _dict(manifest, "SHARD_MANIFEST")
    surface = m.get("surfaceKey")
    _enum(surface, SURFACES, "SURFACE_KEY")
    if m.get("schema") is not None and m["schema"] != SHARD_SCHEMA:
        raise ControlPlaneError("SHARD_SCHEMA_INVALID")
    if m.get("candidateOnly", True) is not True:
        raise ControlPlaneError("SHARD_CANDIDATE_ONLY_REQUIRED")
    if not HEX40.fullmatch(str(m.get("baseHead") or "")):
        raise ControlPlaneError("SHARD_BASE_HEAD_INVALID")
    if expected_head is not None and m["baseHead"] != expected_head:
        raise ControlPlaneError("SHARD_BASE_HEAD_MISMATCH")
    owned_root = str(m.get("ownedRoot") or CANDIDATE_WRITE_ROOTS[surface]).rstrip("/") + "/"
    if owned_root != CANDIDATE_WRITE_ROOTS[surface]:
        raise ControlPlaneError(f"SHARD_OWNED_ROOT_INVALID:{owned_root}")
    if m.get("materialityCatalogPolicy", MATERIALITY_POLICY) != MATERIALITY_POLICY:
        raise ControlPlaneError("MATERIALITY_POLICY_MUST_REMAIN_STANDBY")
    if m.get("broadRediscoveryPerformed", False) is not False:
        raise ControlPlaneError("BROAD_REDISCOVERY_FORBIDDEN")
    for path in changed_paths:
        validate_owned_output(surface, path)
    for ref in m.get("sourceAuthorityRefs", []) or []:
        validate_authority_ref(ref)
    for raw_path, expected in (m.get("sourceHashes") or {}).items():
        if MATERIALITY_BASENAME in str(raw_path).lower():
            raise ControlPlaneError("MATERIALITY_CATALOG_STANDBY_USER_INVOKED_ONLY")
        if not isinstance(expected, str) or not HEX64.fullmatch(expected):
            raise ControlPlaneError(f"SHARD_SOURCE_HASH_INVALID:{raw_path}")
        if repo_root is not None:
            rel = _repo_path(str(raw_path))
            source = repo_root.resolve() / rel
            if not source.is_file() or file_sha256(source) != expected:
                raise ControlPlaneError(f"SHARD_SOURCE_HASH_MISMATCH:{rel}")

    rows = [
        validate_candidate(
            row,
            expected_head=m["baseHead"],
            repo_root=repo_root,
            atlasfin=atlasfin,
            ndc_prefixes=ndc_prefixes,
        )
        for row in outcomes
    ]
    if any(row["surfaceKey"] != surface for row in rows):
        raise ControlPlaneError("SHARD_CROSS_SURFACE_RECORD")
    target_ids = [row["targetId"] for row in rows]
    duplicates = sorted(target for target, count in Counter(target_ids).items() if count > 1)
    if duplicates:
        raise ControlPlaneError("DUPLICATE_TARGET_IDS:" + ",".join(duplicates))
    counts = [value for value in (m.get("inputCensusCount"), m.get("inputTargetCount")) if value is not None]
    if not counts or len(set(counts)) != 1 or not isinstance(counts[0], int) or counts[0] < 0:
        raise ControlPlaneError("INPUT_CENSUS_COUNT_INVALID")
    if counts[0] != len(rows):
        raise ControlPlaneError(f"ZERO_LOSS_ACCOUNTING_FAILED:{counts[0]}:{len(rows)}")
    buckets = Counter(accounting_bucket(row) for row in rows)
    return {
        "schema": "prisma.visual-promotion.shard-validation.v1",
        "status": "PASS_CANDIDATE_SHARD_VALIDATION",
        "surfaceKey": surface,
        "baseHead": m["baseHead"],
        "inputCensusCount": counts[0],
        "outputCount": len(rows),
        "accounting": dict(sorted(buckets.items())),
        "statusCounts": {
            "physicalStatus": dict(sorted(Counter(row["physicalStatus"] for row in rows).items())),
            "atlasfinMatchStatus": dict(sorted(Counter(row["atlasfin"]["atlasfinMatchStatus"] for row in rows).items())),
            "ndcResolutionStatus": dict(sorted(Counter(row["ndc"]["ndcResolutionStatus"] for row in rows).items())),
            "bindingStatus": dict(sorted(Counter(row["identity"]["bindingStatus"] for row in rows).items())),
            "projectionStatus": dict(sorted(Counter(row["application"]["projectionStatus"] for row in rows).items())),
            "promotionStatus": dict(sorted(Counter(row["application"]["promotionStatus"] for row in rows).items())),
            "blockerRecords": sum(1 for row in rows if row["blockers"]),
        },
        "targetDigest": digest(sorted(target_ids)),
        "materialityCatalogPolicy": MATERIALITY_POLICY,
        "broadRediscoveryPerformed": False,
        "runtimeVisualGreen": False,
        "canonicalPromotionPerformed": False,
        "productionReady": False,
    }


def detect_collisions(candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = list(candidates)
    collisions: list[dict[str, Any]] = []
    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_binding: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_fingerprint: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_target[str(row.get("targetId"))].append(row)
        binding_key = row.get("identity", {}).get("bindingCandidateKey")
        if binding_key:
            by_binding[str(binding_key)].append(row)
        by_fingerprint[candidate_fingerprint(row)].append(row)
    for target, group in sorted(by_target.items()):
        if target and len(group) > 1:
            collisions.append({"kind": "DUPLICATE_TARGET", "targetId": target})
    for key, group in sorted(by_binding.items()):
        targets = sorted({str(row["targetId"]) for row in group})
        if len(targets) > 1:
            collisions.append({"kind": "BINDING_CANDIDATE_KEY_COLLISION", "bindingCandidateKey": key, "targetIds": targets})
    for fingerprint, group in sorted(by_fingerprint.items()):
        targets = sorted({str(row["targetId"]) for row in group})
        surfaces = sorted({str(row["surfaceKey"]) for row in group})
        if len(targets) > 1 and len(surfaces) > 1:
            collisions.append({
                "kind": "CROSS_SURFACE_FINGERPRINT_REVIEW",
                "candidateFingerprint": fingerprint,
                "targetIds": targets,
                "surfaces": surfaces,
            })
    return collisions


def reconciliation_candidates(candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = list(candidates)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[candidate_fingerprint(row)].append(row)
    proposals = []
    for fingerprint, group in sorted(grouped.items()):
        proposals.append({
            "candidateFingerprint": fingerprint,
            "targetIds": sorted({row["targetId"] for row in group}),
            "surfaceKeys": sorted({row["surfaceKey"] for row in group}),
            "ndcPrimaryIds": sorted({row["ndc"]["ndcPrimaryId"] for row in group if row["ndc"]["ndcPrimaryId"]}),
            "visualMeaningIds": sorted({row["visual"]["visualMeaningId"] for row in group if row["visual"]["visualMeaningId"]}),
            "visualMeaningCandidates": sorted({row["visual"]["visualMeaningCandidate"] for row in group if row["visual"]["visualMeaningCandidate"]}),
            "atlasfinMatchStatuses": sorted({row["atlasfin"]["atlasfinMatchStatus"] for row in group}),
            "requiresReview": len(group) > 1,
            "canonicalIdAssigned": False,
        })
    return proposals


def composer_plan(candidates: Iterable[dict[str, Any]], *, revalidated_equivalent_base: bool = False) -> dict[str, Any]:
    rows = list(candidates)
    heads = sorted({str(row.get("baseHead")) for row in rows})
    collisions = detect_collisions(rows)
    blockers = []
    if len(heads) > 1 and not revalidated_equivalent_base:
        blockers.append("MIXED_BASE_REQUIRES_REVALIDATION")
    if collisions:
        blockers.append("CANDIDATE_COLLISIONS_REQUIRE_REVIEW")
    return {
        "schema": COMPOSER_SCHEMA,
        "status": "PLAN_READY_FOR_REVIEW" if not blockers else "BLOCKED_COMPOSER_PLAN",
        "baseHeads": heads,
        "mixedBase": len(heads) > 1,
        "baseEquivalenceRevalidated": bool(revalidated_equivalent_base),
        "reconciliationCandidates": reconciliation_candidates(rows),
        "collisions": collisions,
        "blockers": blockers,
        "canonicalMutationPerformed": False,
        "canonicalIdsAssigned": False,
        "materialityCatalogPolicy": MATERIALITY_POLICY,
        "runtimeVisualGreen": False,
        "productionReady": False,
    }


def _physical_status(index_row: dict[str, Any], candidate: dict[str, Any] | None) -> str:
    if candidate and candidate.get("physicalStatus") in PHYSICAL:
        return str(candidate["physicalStatus"])
    blockers = [str(value).lower() for value in index_row.get("blockers", [])]
    if any("drift" in value for value in blockers):
        return "DRIFT"
    if index_row.get("recordKind") == "VISUAL_CONTROL_CENSUS_TARGET" or index_row.get("enforcement") == "DISCOVERY_ONLY":
        return "CURRENT"
    return "CURRENT" if index_row.get("targetId") else "MISSING"


def build_current_truth(target_index: dict[str, Any], candidates: Iterable[dict[str, Any]] = ()) -> dict[str, Any]:
    candidate_rows = list(candidates)
    duplicates = sorted(target for target, count in Counter(str(row.get("targetId")) for row in candidate_rows).items() if target and count > 1)
    if duplicates:
        raise ControlPlaneError("CURRENT_TRUTH_DUPLICATE_CANDIDATE_TARGETS:" + ",".join(duplicates))
    by_target = {str(row["targetId"]): row for row in candidate_rows if row.get("targetId")}
    seen: set[str] = set()
    records = []
    for row in target_index.get("records", []):
        if not isinstance(row, dict) or row.get("surface") not in (*SURFACES, *PROTECTED_SURFACES):
            continue
        target_id = str(row.get("targetId") or "")
        if not target_id:
            continue
        if target_id in seen:
            raise ControlPlaneError(f"CURRENT_TRUTH_TARGET_INDEX_DUPLICATE:{target_id}")
        seen.add(target_id)
        candidate = by_target.get(target_id)
        physical_status = _physical_status(row, candidate)
        census = row.get("recordKind") == "VISUAL_CONTROL_CENSUS_TARGET" or row.get("enforcement") == "DISCOVERY_ONLY"
        reusable = bool(census and physical_status == "CURRENT")
        discovery = physical_status in {"STALE", "DRIFT", "MISSING"}
        records.append({
            "surfaceKey": row.get("surface"),
            "targetId": target_id,
            "recordKind": row.get("recordKind"),
            "enforcement": row.get("enforcement"),
            "physicalStatus": physical_status,
            "currentCensusReusable": reusable,
            "genuineDiscoveryNeeded": discovery,
            "discoveryScope": "TARGETED_ONLY" if discovery else "NONE",
            "nextStepReason": CURRENT_CENSUS_REASON if reusable else None,
            "candidatePresent": candidate is not None,
            "promotionStatus": candidate.get("application", {}).get("promotionStatus") if candidate else None,
            "bindingStatus": candidate.get("identity", {}).get("bindingStatus") if candidate else None,
            "atlasfinMatchStatus": candidate.get("atlasfin", {}).get("atlasfinMatchStatus") if candidate else None,
            "ndcResolutionStatus": candidate.get("ndc", {}).get("ndcResolutionStatus") if candidate else None,
            "runtimeVisualGreen": False,
        })
    orphan = sorted(set(by_target) - seen)
    if orphan:
        raise ControlPlaneError("CURRENT_TRUTH_CANDIDATE_WITHOUT_TARGET_INDEX:" + ",".join(orphan))
    return {
        "schema": TRUTH_SCHEMA,
        "targetIndexSchema": target_index.get("schema"),
        "recordCount": len(records),
        "records": records,
        "materialityCatalogPolicy": MATERIALITY_POLICY,
        "broadRediscoveryAllowed": False,
        "canonicalMutationPerformed": False,
        "runtimeVisualGreen": False,
        "productionReady": False,
    }


def build_surface_readiness(current_truth: dict[str, Any]) -> dict[str, Any]:
    rows = current_truth.get("records", [])
    surfaces = []
    for surface in SURFACES:
        group = [row for row in rows if row.get("surfaceKey") == surface]
        current = [row for row in group if row.get("currentCensusReusable")]
        discovery = [row for row in group if row.get("genuineDiscoveryNeeded")]
        candidates = [row for row in group if row.get("candidatePresent")]
        eligible = [row for row in group if row.get("promotionStatus") == "ELIGIBLE_CANDIDATE"]
        if not group:
            status = "NO_CURRENT_TARGET_INDEX_INPUT"
        elif discovery:
            status = "TARGETED_DISCOVERY_OR_DRIFT_REVIEW_REQUIRED"
        elif len(candidates) < len(group):
            status = "CANDIDATE_PROMOTION_PENDING"
        elif len(eligible) < len(group):
            status = "SEMANTIC_BINDING_REVIEW_PENDING"
        else:
            status = "CANDIDATE_RECONCILIATION_READY_FOR_REVIEW"
        surfaces.append({
            "surfaceKey": surface,
            "readinessStatus": status,
            "inputTargetCount": len(group),
            "currentCensusReusableCount": len(current),
            "genuineDiscoveryNeededCount": len(discovery),
            "targetedDiscoveryOnly": bool(discovery),
            "candidatePresentCount": len(candidates),
            "eligibleCandidateCount": len(eligible),
            "semanticPromotionPendingCount": max(0, len(group) - len(eligible)),
            "broadRediscoveryAllowed": False,
            "broadRediscoveryReason": BROAD_REDISCOVERY_REASON if current else None,
            "wholeSurfaceApplyReady": False,
            "runtimeVisualGreen": False,
        })
    return {
        "schema": READINESS_SCHEMA,
        "surfaces": surfaces,
        "protectedSurfaces": list(PROTECTED_SURFACES),
        "materialityCatalogPolicy": MATERIALITY_POLICY,
        "canonicalPromotionPerformed": False,
        "runtimeVisualGreen": False,
        "productionReady": False,
    }
