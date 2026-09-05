from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from .control_plane import (
    BROAD_REDISCOVERY_REASON,
    CURRENT_CENSUS_REASON,
    MATERIALITY_POLICY,
    ControlPlaneError,
    detect_collisions,
    validate_candidate,
)

REGISTRY_SCHEMA = "prisma.visual-promotion.intake-registry.v1"
GLOBAL_CERT_SCHEMA = "prisma.visual-promotion.global-candidate-certification.v1"
CURRENT_TRUTH_SCHEMA = "prisma.visual-promotion.certified-current-truth.v1"
SURFACE_READINESS_SCHEMA = "prisma.visual-promotion.certified-surface-readiness.v1"
SEMANTIC_REVIEW_SCHEMA = "prisma.visual-promotion.semantic-review-groups.v1"
COLLISION_SCHEMA = "prisma.visual-promotion.corpus-collisions.v1"
EXPECTED_SURFACES = ("tablet", "pc", "mobile", "shared-ui")
EXPECTED_CORPUS_COUNT = 2097
AUTHORITY_DOMAINS = {
    "ndc", "atlasfin", "identity", "rifat", "visual-control", "target-index",
    "projection-manifest", "factory-ledger", "code-atlas", "work-entry-gate", "gvae",
}


class CorpusCertificationError(RuntimeError):
    pass


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_registry(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != REGISTRY_SCHEMA:
        raise CorpusCertificationError("INTAKE_REGISTRY_SCHEMA_INVALID")
    if data.get("materialityCatalogPolicy") != MATERIALITY_POLICY:
        raise CorpusCertificationError("MATERIALITY_POLICY_MUST_REMAIN_STANDBY")
    if data.get("broadRediscoveryAllowed") is not False:
        raise CorpusCertificationError("BROAD_REDISCOVERY_MUST_REMAIN_FORBIDDEN")
    if tuple(data.get("surfaceOrder") or ()) != EXPECTED_SURFACES:
        raise CorpusCertificationError("SURFACE_ORDER_INVALID")
    surfaces = data.get("surfaces")
    if not isinstance(surfaces, dict) or set(surfaces) != set(EXPECTED_SURFACES):
        raise CorpusCertificationError("INTAKE_REGISTRY_SURFACES_INVALID")
    return data


def lane(registry: Mapping[str, Any], surface_key: str) -> Mapping[str, Any]:
    surfaces = registry.get("surfaces")
    if surface_key not in EXPECTED_SURFACES or not isinstance(surfaces, Mapping) or surface_key not in surfaces:
        raise CorpusCertificationError(f"UNREGISTERED_SURFACE:{surface_key}")
    row = surfaces[surface_key]
    if not isinstance(row, Mapping):
        raise CorpusCertificationError(f"INTAKE_LANE_OBJECT_REQUIRED:{surface_key}")
    return row


def verify_registered_head(registry: Mapping[str, Any], surface_key: str, *, kind: str, head: str) -> None:
    field = {"worker": "workerHead", "certification": "certificationHead"}.get(kind)
    if field is None:
        raise CorpusCertificationError(f"INTAKE_KIND_INVALID:{kind}")
    expected = lane(registry, surface_key).get(field)
    if head != expected:
        raise CorpusCertificationError(f"UNREGISTERED_{kind.upper()}_HEAD:{surface_key}:{head}")


def verify_registered_file(
    registry: Mapping[str, Any], surface_key: str, *, kind: str, head: str,
    file_name: str, content: bytes, git_blob_sha: str | None = None,
) -> dict[str, Any]:
    verify_registered_head(registry, surface_key, kind=kind, head=head)
    bucket_name = {"worker": "workerFiles", "certification": "certificationFiles"}[kind]
    bucket = lane(registry, surface_key).get(bucket_name)
    if not isinstance(bucket, Mapping) or file_name not in bucket:
        raise CorpusCertificationError(f"UNREGISTERED_{kind.upper()}_FILE:{surface_key}:{file_name}")
    expected = bucket[file_name]
    digest = sha256_bytes(content)
    if digest != expected.get("sha256"):
        raise CorpusCertificationError(f"INTAKE_SHA256_MISMATCH:{surface_key}:{kind}:{file_name}")
    if git_blob_sha is not None and git_blob_sha != expected.get("gitBlobSha"):
        raise CorpusCertificationError(f"INTAKE_GIT_BLOB_MISMATCH:{surface_key}:{kind}:{file_name}")
    expected_count = expected.get("recordCount")
    if expected_count is not None and file_name.endswith(".jsonl"):
        actual = len([x for x in content.decode("utf-8").splitlines() if x.strip()])
        if actual != expected_count:
            raise CorpusCertificationError(
                f"INTAKE_RECORD_COUNT_MISMATCH:{surface_key}:{kind}:{file_name}:{actual}:{expected_count}"
            )
    return {"status": "PASS_REGISTERED_INTAKE", "surfaceKey": surface_key, "kind": kind,
            "head": head, "file": file_name, "sha256": digest, "gitBlobSha": expected.get("gitBlobSha"),
            "recordCount": expected_count}


def verify_registered_atlasfin_file(
    registry: Mapping[str, Any], *, kind: str, head: str, file_name: str,
    content: bytes, git_blob_sha: str | None = None,
) -> dict[str, Any]:
    af = registry.get("atlasfin")
    if not isinstance(af, Mapping):
        raise CorpusCertificationError("ATLASFIN_REGISTRY_SECTION_REQUIRED")
    pair = {"bridge": ("bridgeHead", "bridgeFiles"), "certification": ("certificationHead", "certificationFiles")}.get(kind)
    if pair is None:
        raise CorpusCertificationError(f"ATLASFIN_INTAKE_KIND_INVALID:{kind}")
    head_field, files_field = pair
    if head != af.get(head_field):
        raise CorpusCertificationError(f"UNREGISTERED_ATLASFIN_{kind.upper()}_HEAD:{head}")
    files = af.get(files_field)
    if not isinstance(files, Mapping) or file_name not in files:
        raise CorpusCertificationError(f"UNREGISTERED_ATLASFIN_{kind.upper()}_FILE:{file_name}")
    expected = files[file_name]
    digest = sha256_bytes(content)
    if digest != expected.get("sha256"):
        raise CorpusCertificationError(f"ATLASFIN_INTAKE_SHA256_MISMATCH:{kind}:{file_name}")
    if git_blob_sha is not None and git_blob_sha != expected.get("gitBlobSha"):
        raise CorpusCertificationError(f"ATLASFIN_INTAKE_GIT_BLOB_MISMATCH:{kind}:{file_name}")
    expected_count = expected.get("recordCount")
    if expected_count is not None and file_name.endswith(".jsonl"):
        actual = len([x for x in content.decode("utf-8").splitlines() if x.strip()])
        if actual != expected_count:
            raise CorpusCertificationError(f"ATLASFIN_INTAKE_RECORD_COUNT_MISMATCH:{actual}:{expected_count}")
    return {"status": "PASS_REGISTERED_ATLASFIN_INTAKE", "kind": kind, "head": head,
            "file": file_name, "sha256": digest, "gitBlobSha": expected.get("gitBlobSha"),
            "recordCount": expected_count}


def _evidence_ref(value: Any, *, base_head: str) -> Any:
    if isinstance(value, Mapping):
        return copy.deepcopy(value)
    if not isinstance(value, str):
        raise CorpusCertificationError("EVIDENCE_REF_SHAPE_INVALID")
    if "::" in value and value.split("::", 1)[0] in AUTHORITY_DOMAINS:
        return value
    if value.startswith("prisma-html/authority/rifat/prisma-ui/visual-control/target-index/"):
        return {"authorityDomain": "target-index", "id": value}
    if value.startswith("prisma-html/authority/rifat/prisma-ui/visual-control/expanded/"):
        return {"authorityDomain": "visual-control", "id": value}
    if value.startswith("prisma-html/authority/rifat/"):
        return {"authorityDomain": "rifat", "id": f"repo:{value}@{base_head}"}
    if value.startswith("apps/terminal-de-venta-system/products/"):
        return {"authorityDomain": "projection-manifest", "id": f"repo:{value}@{base_head}"}
    raise CorpusCertificationError(f"UNREGISTERED_EVIDENCE_REF_SHAPE:{value}")


def semantic_snapshot(record: Mapping[str, Any]) -> dict[str, Any]:
    ndc = record.get("ndc") if isinstance(record.get("ndc"), Mapping) else {}
    visual = record.get("visual") if isinstance(record.get("visual"), Mapping) else {}
    af = record.get("atlasfin") if isinstance(record.get("atlasfin"), Mapping) else {}
    identity = record.get("identity") if isinstance(record.get("identity"), Mapping) else {}
    app = record.get("application") if isinstance(record.get("application"), Mapping) else {}
    refs = [x.split("::", 1)[1] if isinstance(x, str) and x.startswith("ndc::") else x for x in (ndc.get("ndcRefs") or [])]
    adapter = af.get("atlasfinAdapterId")
    if isinstance(adapter, str) and adapter.startswith("atlasfin::"):
        adapter = adapter.split("::", 1)[1]
    return {
        "targetId": record.get("targetId"), "surfaceKey": record.get("surfaceKey"),
        "physicalStatus": record.get("physicalStatus"),
        "ndcPrimaryId": ndc.get("ndcPrimaryId"), "ndcRefs": sorted(refs),
        "ndcResolutionStatus": ndc.get("ndcResolutionStatus"),
        "visualMeaningId": visual.get("visualMeaningId"),
        "visualMeaningCandidate": visual.get("visualMeaningCandidate"),
        "visualMeaningStatus": visual.get("visualMeaningStatus"),
        "atlasfinFamilyId": af.get("atlasfinFamilyId"), "atlasfinPresetId": af.get("atlasfinPresetId"),
        "atlasfinRecipeId": af.get("atlasfinRecipeId"), "atlasfinLegacyRecipeId": af.get("atlasfinLegacyRecipeId"),
        "atlasfinAdapterId": adapter, "atlasfinMatchStatus": af.get("atlasfinMatchStatus"),
        "identityRecipeId": identity.get("identityRecipeId"), "existingBindingId": identity.get("existingBindingId"),
        "bindingStatus": identity.get("bindingStatus"), "projectionStatus": app.get("projectionStatus"),
        "promotionStatus": app.get("promotionStatus"), "workEntryDecision": app.get("workEntryDecision"),
    }


def normalize_registered_raw_record(
    registry: Mapping[str, Any], surface_key: str, record: Mapping[str, Any], *, source_head: str,
) -> tuple[dict[str, Any], list[str]]:
    verify_registered_head(registry, surface_key, kind="worker", head=source_head)
    allowed = set(lane(registry, surface_key).get("allowedRawTransforms") or [])
    out = copy.deepcopy(dict(record))
    before = semantic_snapshot(out)
    transforms: list[str] = []

    if out.get("schema") is None:
        if "EXPLICIT_STRICT_SCHEMA_TAG" in allowed:
            out["schema"] = "prisma.visual-promotion.candidate.v1"
            transforms.append("EXPLICIT_STRICT_SCHEMA_TAG")
        elif surface_key not in {"tablet", "pc"}:
            raise CorpusCertificationError(f"UNREGISTERED_SCHEMA_SHAPE:{surface_key}")

    projection = out.get("projection")
    if projection is not None:
        name = "FLATTEN_PROJECTION_OBJECT_TO_STRICT_TOP_LEVEL_FIELDS"
        if name not in allowed or not isinstance(projection, Mapping):
            raise CorpusCertificationError(f"UNREGISTERED_PROJECTION_SHAPE:{surface_key}")
        for key in ("canonicalSourcePath", "generatedOutputPath", "sourceSha256", "outputSha256", "projectionMode"):
            if key in projection:
                if key in out and out[key] != projection[key]:
                    raise CorpusCertificationError(f"PROJECTION_FLATTEN_COLLISION:{key}")
                out[key] = projection[key]
        del out["projection"]
        transforms.append(name)

    ndc = out.get("ndc")
    if isinstance(ndc, dict) and any(isinstance(x, str) and x.startswith("ndc::") for x in (ndc.get("ndcRefs") or [])):
        name = "NORMALIZE_NDC_REFS_TO_DOMAIN_SCOPED_RAW_IDS"
        if name not in allowed:
            raise CorpusCertificationError(f"UNREGISTERED_NDC_REF_SHAPE:{surface_key}")
        ndc["ndcRefs"] = [x.split("::", 1)[1] if isinstance(x, str) and x.startswith("ndc::") else x for x in ndc.get("ndcRefs") or []]
        transforms.append(name)

    af = out.get("atlasfin")
    if isinstance(af, dict) and isinstance(af.get("atlasfinAdapterId"), str) and af["atlasfinAdapterId"].startswith("atlasfin::"):
        name = "NORMALIZE_ATLASFIN_ADAPTER_TO_DOMAIN_SCOPED_RAW_ID" if surface_key == "mobile" else "QUALIFIED_ATLASFIN_ADAPTER_TO_STRICT_RAW_REGISTRY_ID"
        if name not in allowed:
            raise CorpusCertificationError(f"UNREGISTERED_ATLASFIN_ADAPTER_SHAPE:{surface_key}")
        af["atlasfinAdapterId"] = af["atlasfinAdapterId"].split("::", 1)[1]
        transforms.append(name)

    refs = out.get("evidenceRefs")
    if isinstance(refs, list) and any(isinstance(x, str) and "::" not in x for x in refs):
        name = "NORMALIZE_UNQUALIFIED_EVIDENCE_REFS_TO_STRICT_AUTHORITY_REFS"
        if name not in allowed:
            raise CorpusCertificationError(f"UNREGISTERED_EVIDENCE_REF_SHAPE:{surface_key}")
        base = str(out.get("baseHead") or registry.get("sourceBaseHead") or "")
        out["evidenceRefs"] = [_evidence_ref(x, base_head=base) for x in refs]
        transforms.append(name)

    if semantic_snapshot(out) != before:
        raise CorpusCertificationError(f"SEMANTIC_MUTATION_DETECTED:{surface_key}:{out.get('targetId')}")
    if set(transforms) - allowed:
        raise CorpusCertificationError("UNREGISTERED_TRANSFORM")
    validate_candidate(out, expected_head=str(registry.get("sourceBaseHead") or ""))
    return out, transforms


def semantic_review_payload(record: Mapping[str, Any]) -> dict[str, Any] | None:
    ndc = record.get("ndc") if isinstance(record.get("ndc"), Mapping) else {}
    visual = record.get("visual") if isinstance(record.get("visual"), Mapping) else {}
    af = record.get("atlasfin") if isinstance(record.get("atlasfin"), Mapping) else {}
    identity = record.get("identity") if isinstance(record.get("identity"), Mapping) else {}
    payload = {
        "ndcPrimaryId": ndc.get("ndcPrimaryId"), "ndcRefs": sorted(ndc.get("ndcRefs") or []),
        "visualMeaningId": visual.get("visualMeaningId"), "visualMeaningCandidate": visual.get("visualMeaningCandidate"),
        "atlasfinFamilyId": af.get("atlasfinFamilyId"), "atlasfinPresetId": af.get("atlasfinPresetId"),
        "atlasfinRecipeId": af.get("atlasfinRecipeId"), "atlasfinLegacyRecipeId": af.get("atlasfinLegacyRecipeId"),
        "identityRecipeId": identity.get("identityRecipeId"),
    }
    values = [payload["ndcPrimaryId"], *payload["ndcRefs"], payload["visualMeaningId"], payload["visualMeaningCandidate"],
              payload["atlasfinFamilyId"], payload["atlasfinPresetId"], payload["atlasfinRecipeId"],
              payload["atlasfinLegacyRecipeId"], payload["identityRecipeId"]]
    return payload if any(x not in (None, "") for x in values) else None


def semantic_review_key(record: Mapping[str, Any]) -> str | None:
    payload = semantic_review_payload(record)
    return None if payload is None else sha256_text(stable_json(payload))


def build_semantic_review_groups(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    payloads: dict[str, dict[str, Any]] = {}
    no_signal = 0
    for row in records:
        key = semantic_review_key(row)
        if key is None:
            no_signal += 1
            continue
        grouped[key].append(row)
        payloads[key] = semantic_review_payload(row) or {}
    groups = []
    for key, rows in sorted(grouped.items()):
        if len(rows) < 2:
            continue
        surfaces = sorted({str(r.get("surfaceKey")) for r in rows})
        groups.append({
            "reviewKey": key, "semanticEvidence": payloads[key], "recordCount": len(rows),
            "surfaceKeys": surfaces, "crossSurface": len(surfaces) > 1,
            "targetIds": sorted(str(r.get("targetId")) for r in rows),
            "resolutionStatus": "REVIEW_ONLY_NOT_CANONICAL_AUTHORITY",
        })
    return {
        "schema": SEMANTIC_REVIEW_SCHEMA, "status": "SEMANTIC_REVIEW_GROUPS_READY",
        "reviewKeyIncludesSurfaceKey": False, "reviewKeyIncludesTargetId": False,
        "collisionFingerprintChanged": False, "recordCount": len(records), "noSemanticSignalCount": no_signal,
        "groupCount": len(groups), "crossSurfaceGroupCount": sum(1 for x in groups if x["crossSurface"]),
        "groups": groups,
    }


def expected_certification_status(candidate: Mapping[str, Any]) -> str:
    app = candidate.get("application") if isinstance(candidate.get("application"), Mapping) else {}
    promotion = app.get("promotionStatus")
    work = app.get("workEntryDecision")
    if work == "BLOCKED" or promotion == "BLOCKED":
        return "VALID_BLOCKED"
    if promotion == "NOT_APPLICABLE":
        return "VALID_NOT_APPLICABLE"
    if promotion == "ELIGIBLE_CANDIDATE":
        return "VALID_ELIGIBLE_CANDIDATE"
    return "VALID_REGISTER_TARGET_FIRST"


def lane_semantic_mutation(row: Mapping[str, Any]) -> bool:
    if isinstance(row.get("semanticMutation"), bool):
        return bool(row["semanticMutation"])
    norm = row.get("normalization")
    if isinstance(norm, Mapping) and isinstance(norm.get("semanticMutation"), bool):
        return bool(norm["semanticMutation"])
    return False


def build_global_certification(
    records_by_surface: Mapping[str, Sequence[tuple[str, Mapping[str, Any]]]],
    lane_certifications: Mapping[str, Sequence[tuple[str, Mapping[str, Any]]]],
    registry: Mapping[str, Any],
) -> list[dict[str, Any]]:
    out = []
    for surface in EXPECTED_SURFACES:
        candidates = list(records_by_surface.get(surface) or [])
        cert_rows = list(lane_certifications.get(surface) or [])
        count = int(lane(registry, surface).get("recordCount") or -1)
        if len(candidates) != count or len(cert_rows) != count:
            raise CorpusCertificationError(f"LANE_CERTIFICATION_COUNT_MISMATCH:{surface}")
        by_target = {}
        for line_no, (raw, row) in enumerate(cert_rows, start=1):
            target = str(row.get("targetId") or "")
            if not target or target in by_target:
                raise CorpusCertificationError(f"LANE_CERTIFICATION_TARGET_INVALID:{surface}:{target}")
            by_target[target] = (line_no, raw, row)
        seen = set()
        for normalized_line, candidate in candidates:
            validate_candidate(candidate, expected_head=str(registry.get("sourceBaseHead") or ""))
            target = str(candidate.get("targetId") or "")
            if target in seen:
                raise CorpusCertificationError(f"DUPLICATE_TARGET_IDS:{target}")
            seen.add(target)
            if target not in by_target:
                raise CorpusCertificationError(f"CERTIFICATION_MISSING_TARGET:{surface}:{target}")
            line_no, lane_raw, lane_row = by_target[target]
            if lane_semantic_mutation(lane_row):
                raise CorpusCertificationError(f"SEMANTIC_MUTATION_CERTIFIED:{surface}:{target}")
            expected = expected_certification_status(candidate)
            lane_status = lane_row.get("certificationStatus")
            if isinstance(lane_status, str) and lane_status != expected:
                raise CorpusCertificationError(f"CERTIFICATION_STATUS_MISMATCH:{surface}:{target}:{lane_status}:{expected}")
            meta = lane(registry, surface)
            out.append({
                "schema": GLOBAL_CERT_SCHEMA, "surfaceKey": surface, "targetId": target,
                "certificationStatus": expected, "candidateRecordSha256": sha256_text(normalized_line),
                "candidateSource": {
                    "workerHead": meta.get("workerHead"), "sourceBaseHead": registry.get("sourceBaseHead"),
                    "certificationHead": meta.get("certificationHead"),
                    "normalizedFile": f"prisma-html/governance/visual-promotion/candidates/{surface}/certification/NORMALIZED.jsonl",
                },
                "laneCertification": {
                    "file": f"prisma-html/governance/visual-promotion/candidates/{surface}/certification/CERTIFICATION.jsonl",
                    "line": line_no, "recordSha256": sha256_text(lane_raw),
                },
                "strictCandidateSchemaValid": True, "closedVocabularyValid": True, "referenceValid": True,
                "provenanceValid": True, "semanticMutation": False,
                "currentlyAuthorizedCanonicalPromotion": False, "runtimeVisualGreen": False,
            })
        extras = set(by_target) - seen
        if extras:
            raise CorpusCertificationError(f"CERTIFICATION_EXTRA_TARGETS:{surface}:{len(extras)}")
    return out


def counter(rows: Sequence[Mapping[str, Any]], getter) -> dict[str, int]:
    return dict(sorted(Counter(str(getter(row)) for row in rows).items()))


def build_current_truth_from_corpus(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = []
    for row in records:
        app = row.get("application") if isinstance(row.get("application"), Mapping) else {}
        physical = str(row.get("physicalStatus") or "")
        drift = physical in {"DRIFT", "STALE", "MISSING"} or app.get("projectionStatus") == "DRIFT"
        rows.append({
            "surfaceKey": row.get("surfaceKey"), "targetId": row.get("targetId"),
            "recordKind": row.get("recordKind"), "enforcement": row.get("enforcement"),
            "physicalStatus": physical, "projectionStatus": app.get("projectionStatus"),
            "promotionStatus": app.get("promotionStatus"), "workEntryDecision": app.get("workEntryDecision"),
            "currentCensusReusable": row.get("recordKind") == "VISUAL_CONTROL_CENSUS_TARGET" and row.get("enforcement") == "DISCOVERY_ONLY",
            "genuineDiscoveryNeeded": drift, "discoveryScope": "TARGETED_ONLY" if drift else "NONE",
            "broadRediscoveryAllowed": False, "nextStepReason": CURRENT_CENSUS_REASON,
            "blockers": list(row.get("blockers") or []), "runtimeVisualGreen": False,
        })
    return {
        "schema": CURRENT_TRUTH_SCHEMA, "status": "CERTIFIED_CORPUS_CURRENT_TRUTH",
        "recordCount": len(rows), "runtimeVisualGreen": False, "currentlyAuthorizedCanonicalPromotions": 0,
        "broadRediscoveryAllowed": False, "broadRediscoveryReason": BROAD_REDISCOVERY_REASON, "records": rows,
    }


def build_surface_readiness_from_corpus(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    surfaces = []
    for surface in EXPECTED_SURFACES:
        rows = [x for x in records if x.get("surfaceKey") == surface]
        surfaces.append({
            "surfaceKey": surface, "recordCount": len(rows),
            "physicalStatusCounts": counter(rows, lambda r: r.get("physicalStatus")),
            "projectionStatusCounts": counter(rows, lambda r: (r.get("application") or {}).get("projectionStatus")),
            "promotionStatusCounts": counter(rows, lambda r: (r.get("application") or {}).get("promotionStatus")),
            "workEntryDecisionCounts": counter(rows, lambda r: (r.get("application") or {}).get("workEntryDecision")),
            "blockedRecordCount": sum(1 for r in rows if (r.get("application") or {}).get("workEntryDecision") == "BLOCKED"),
            "wholeSurfaceApplyReady": False, "runtimeVisualGreen": False, "broadRediscoveryAllowed": False,
            "broadRediscoveryReason": BROAD_REDISCOVERY_REASON, "status": "CANDIDATE_CORPUS_CERTIFIED_NOT_APPLY_READY",
        })
    return {
        "schema": SURFACE_READINESS_SCHEMA, "status": "CERTIFIED_CORPUS_SURFACE_READINESS",
        "runtimeVisualGreen": False, "wholeSurfaceApplyReadyCount": 0,
        "currentlyAuthorizedCanonicalPromotions": 0, "surfaces": surfaces,
    }


def validate_global_corpus(
    records: Sequence[Mapping[str, Any]], certifications: Sequence[Mapping[str, Any]], *,
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    errors = []
    if len(records) != EXPECTED_CORPUS_COUNT:
        errors.append(f"CORPUS_COUNT:{len(records)}:{EXPECTED_CORPUS_COUNT}")
    if len(certifications) != EXPECTED_CORPUS_COUNT:
        errors.append(f"CERTIFICATION_COUNT:{len(certifications)}:{EXPECTED_CORPUS_COUNT}")
    expected_counts = {s: int(lane(registry, s).get("recordCount") or 0) for s in EXPECTED_SURFACES}
    actual_counts = Counter(str(x.get("surfaceKey")) for x in records)
    if dict(actual_counts) != expected_counts:
        errors.append(f"SURFACE_COUNTS:{dict(actual_counts)}:{expected_counts}")
    targets = [str(x.get("targetId") or "") for x in records]
    cert_targets = [str(x.get("targetId") or "") for x in certifications]
    missing = set(targets) - set(cert_targets)
    extra = set(cert_targets) - set(targets)
    duplicate_count = len(targets) - len(set(targets))
    if duplicate_count:
        errors.append(f"DUPLICATE_TARGET_IDS:{duplicate_count}")
    if missing:
        errors.append(f"MISSING_CERTIFICATION_TARGETS:{len(missing)}")
    if extra:
        errors.append(f"EXTRA_CERTIFICATION_TARGETS:{len(extra)}")
    semantic_mutations = sum(1 for x in certifications if x.get("semanticMutation") is True)
    exact_apply = sum(1 for x in records if (x.get("application") or {}).get("workEntryDecision") == "GVAE_EXACT_APPLY")
    authorized = sum(1 for x in certifications if x.get("currentlyAuthorizedCanonicalPromotion") is True)
    if semantic_mutations:
        errors.append(f"SEMANTIC_MUTATION_COUNT:{semantic_mutations}")
    if exact_apply:
        errors.append(f"GVAE_EXACT_APPLY:{exact_apply}")
    if authorized:
        errors.append(f"CURRENTLY_AUTHORIZED_CANONICAL_PROMOTIONS:{authorized}")
    for row in records:
        try:
            validate_candidate(row, expected_head=str(registry.get("sourceBaseHead") or ""))
        except (ControlPlaneError, TypeError, ValueError) as exc:
            errors.append(f"CANDIDATE_INVALID:{row.get('targetId')}:{exc}")
            if len(errors) >= 20:
                break
    return {
        "status": "PASS_CANDIDATE_CORPUS_VALIDATION" if not errors else "BLOCKED_CANDIDATE_CORPUS_VALIDATION",
        "recordCount": len(records), "certificationCount": len(certifications), "missing": len(missing),
        "extra": len(extra), "duplicateTargetIds": duplicate_count, "semanticMutationCount": semantic_mutations,
        "currentlyAuthorizedCanonicalPromotions": authorized, "GVAE_EXACT_APPLY": exact_apply,
        "runtimeVisualGreen": False, "errors": errors,
    }


def collision_report(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    collisions = detect_collisions(records)
    duplicates = [x for x in collisions if x.get("kind") == "DUPLICATE_TARGET"]
    bindings = [x for x in collisions if x.get("kind") == "BINDING_CANDIDATE_KEY_COLLISION"]
    reviews = [x for x in collisions if x.get("kind") == "CROSS_SURFACE_FINGERPRINT_REVIEW"]
    return {
        "schema": COLLISION_SCHEMA,
        "status": "PASS_NO_HARD_COLLISIONS" if not duplicates and not bindings else "BLOCKED_HARD_COLLISIONS",
        "recordCount": len(records), "duplicateTargetIds": len(duplicates),
        "bindingCandidateKeyCollisions": len(bindings), "crossSurfaceFingerprintReviews": len(reviews),
        "collisionFingerprintChanged": False, "collisions": collisions,
    }
