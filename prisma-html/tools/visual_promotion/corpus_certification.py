from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from .control_plane import (
    CANDIDATE_SCHEMA,
    MATERIALITY_POLICY,
    ControlPlaneError,
    build_current_truth,
    build_surface_readiness,
    detect_collisions,
    load_atlasfin_indexes,
    load_json,
    ndc_prefixes_from_registry,
    validate_candidate,
)

REGISTRY_SCHEMA = "prisma.visual-promotion.legacy-worker-intake.v1"
CERTIFICATION_SCHEMA = "prisma.visual-promotion.corpus-certification-record.v1"
CORPUS_MANIFEST_SCHEMA = "prisma.visual-promotion.candidate-corpus-manifest.v1"
SEMANTIC_REVIEW_SCHEMA = "prisma.visual-promotion.semantic-review-groups.v1"
COLLISION_SCHEMA = "prisma.visual-promotion.corpus-collisions.v1"

SURFACE_ORDER = ("tablet", "pc", "mobile", "shared-ui")
OUTCOME_FILES = ("CANDIDATES.jsonl", "UNRESOLVED.jsonl", "CONFLICTS.jsonl")
SOURCE_BUCKET = {
    "CANDIDATES.jsonl": "CANDIDATES",
    "UNRESOLVED.jsonl": "UNRESOLVED",
    "CONFLICTS.jsonl": "CONFLICTS",
}
CERTIFICATION_BY_PROMOTION = {
    "ELIGIBLE_CANDIDATE": "VALID_ELIGIBLE_CANDIDATE",
    "REGISTER_TARGET_FIRST": "VALID_REGISTER_TARGET_FIRST",
    "BLOCKED": "VALID_BLOCKED",
    "NOT_APPLICABLE": "VALID_NOT_APPLICABLE",
}
VALID_CERTIFICATIONS = frozenset(CERTIFICATION_BY_PROMOTION.values())
TARGET_INDEX_PATHS = {
    surface: f"prisma-html/authority/rifat/prisma-ui/visual-control/target-index/{surface}.json"
    for surface in SURFACE_ORDER
}
ATLASFIN_PATHS = (
    "prisma-html/extras/atlasfin/assets/data/atlas.manifest.json",
    "prisma-html/extras/atlasfin/assets/data/visual-property.registry.json",
    "prisma-html/extras/atlasfin/assets/data/visual-family.registry.json",
    "prisma-html/extras/atlasfin/assets/data/visual-preset.registry.json",
    "prisma-html/extras/atlasfin/assets/data/visual-recipe.registry.json",
    "prisma-html/extras/atlasfin/assets/data/visual-state.registry.json",
    "prisma-html/extras/atlasfin/assets/data/visual-variant.registry.json",
    "prisma-html/extras/atlasfin/assets/data/surface-adapter.registry.json",
    "prisma-html/extras/atlasfin/assets/data/visual.recipe.registry.json",
)
NDC_PREFIX_PATH = "apps/terminal-de-venta-system/docs/ndc/registry/ndc_prefix_registry.json"
CORPUS_OUTPUTS = (
    "CORPUS_MANIFEST.json",
    "CANDIDATE_CORPUS.jsonl",
    "CERTIFICATION.jsonl",
    "INVALID.jsonl",
    "COLLISIONS.json",
    "SEMANTIC_REVIEW_GROUPS.json",
    "CURRENT_TRUTH.json",
    "SURFACE_READINESS.json",
    "SUMMARY.md",
)


class CorpusCertificationError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def git_blob_sha1(value: bytes) -> str:
    header = b"blob " + str(len(value)).encode("ascii") + b"\0"
    return hashlib.sha1(header + value).hexdigest()


def load_registry(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(document, dict) or document.get("schema") != REGISTRY_SCHEMA:
        raise CorpusCertificationError("INTAKE_REGISTRY_SCHEMA_INVALID")
    surfaces = document.get("surfaces")
    if not isinstance(surfaces, dict):
        raise CorpusCertificationError("INTAKE_REGISTRY_SURFACES_INVALID")
    if tuple(sorted(surfaces)) != tuple(sorted(SURFACE_ORDER)):
        raise CorpusCertificationError("INTAKE_REGISTRY_SURFACES_INVALID")
    if document.get("materialityCatalogPolicy") != MATERIALITY_POLICY:
        raise CorpusCertificationError("MATERIALITY_POLICY_MUST_REMAIN_STANDBY")
    if document.get("broadRediscoveryAllowed") is not False:
        raise CorpusCertificationError("BROAD_REDISCOVERY_MUST_REMAIN_FORBIDDEN")
    return document


def _profile(registry: Mapping[str, Any], surface: str) -> dict[str, Any]:
    if surface not in SURFACE_ORDER:
        raise CorpusCertificationError(f"SURFACE_UNREGISTERED:{surface}")
    raw = registry["surfaces"].get(surface)
    if not isinstance(raw, dict):
        raise CorpusCertificationError(f"SURFACE_PROFILE_MISSING:{surface}")
    return raw


def verify_registered_file(
    repo_root: Path,
    registry: Mapping[str, Any],
    *,
    surface: str,
    source_head: str,
    filename: str,
) -> tuple[Path, bytes, dict[str, Any]]:
    profile = _profile(registry, surface)
    if source_head != profile.get("sourceHead"):
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:UNKNOWN_SOURCE_HEAD:{surface}:{source_head}"
        )
    files = profile.get("files")
    pin = files.get(filename) if isinstance(files, dict) else None
    if not isinstance(pin, dict):
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:UNREGISTERED_FILE:{surface}:{filename}"
        )
    raw_root = str(profile.get("rawRoot") or "").rstrip("/")
    path = (repo_root / raw_root / filename).resolve()
    repo = repo_root.resolve()
    if repo not in path.parents:
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:PATH_ESCAPE:{surface}:{filename}"
        )
    if not path.is_file():
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:SOURCE_FILE_MISSING:{surface}:{filename}"
        )
    data = path.read_bytes()
    if sha256_bytes(data) != pin.get("sha256"):
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:FILE_SHA256_MISMATCH:{surface}:{filename}"
        )
    if git_blob_sha1(data) != pin.get("gitBlobSha"):
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:GIT_BLOB_MISMATCH:{surface}:{filename}"
        )
    return path, data, pin


def _strip_qualified(value: Any, domain: str) -> Any:
    prefix = domain + "::"
    if isinstance(value, str) and value.startswith(prefix):
        return value[len(prefix):]
    return value


def _normalized_projection_view(record: Mapping[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(dict(record))
    projection = out.pop("projection", None)
    if projection is None:
        return out
    if not isinstance(projection, dict):
        raise CorpusCertificationError("INVALID_SCHEMA:PROJECTION_OBJECT_REQUIRED")
    for key in (
        "canonicalSourcePath",
        "generatedOutputPath",
        "sourceSha256",
        "outputSha256",
        "projectionMode",
    ):
        value = projection.get(key)
        if (
            key in out
            and out[key] is not None
            and value is not None
            and out[key] != value
        ):
            raise CorpusCertificationError(
                f"INVALID_PROVENANCE:PROJECTION_FIELD_CONFLICT:{key}"
            )
        if value is not None:
            out[key] = value
    projection_status = projection.get("projectionStatus")
    application = out.get("application")
    if projection_status is not None and isinstance(application, dict):
        if application.get("projectionStatus") != projection_status:
            raise CorpusCertificationError(
                "INVALID_PROVENANCE:PROJECTION_STATUS_CONFLICT"
            )
    return out


def semantic_signature(record: Mapping[str, Any]) -> str:
    out = _normalized_projection_view(record)
    out.pop("schema", None)
    out.pop("candidateFingerprint", None)
    out.pop("evidenceRefs", None)

    ndc = out.get("ndc")
    if isinstance(ndc, dict):
        if isinstance(ndc.get("ndcPrimaryId"), str):
            ndc["ndcPrimaryId"] = _strip_qualified(
                ndc["ndcPrimaryId"], "ndc"
            )
        refs = ndc.get("ndcRefs")
        if isinstance(refs, list):
            ndc["ndcRefs"] = [
                _strip_qualified(item, "ndc") for item in refs
            ]

    atlasfin = out.get("atlasfin")
    if isinstance(atlasfin, dict):
        for field in (
            "atlasfinCatalogElementId",
            "atlasfinUiId",
            "atlasfinFamilyId",
            "atlasfinPresetId",
            "atlasfinRecipeId",
            "atlasfinLegacyRecipeId",
            "atlasfinAdapterId",
        ):
            if isinstance(atlasfin.get(field), str):
                atlasfin[field] = _strip_qualified(
                    atlasfin[field], "atlasfin"
                )
    return sha256_value(out)


def _normalize_evidence_ref(
    ref: Any,
) -> tuple[Any | None, str | None, dict[str, Any] | None]:
    if isinstance(ref, dict):
        return copy.deepcopy(ref), None, None
    if not isinstance(ref, str):
        change = {
            "field": "evidenceRefs",
            "from": ref,
            "to": None,
            "reason": "NON_STRING_EVIDENCE_LIFTED",
        }
        return None, None, change

    prefixes = (
        "ndc::",
        "atlasfin::",
        "identity::",
        "rifat::",
        "visual-control::",
        "target-index::",
        "projection-manifest::",
        "factory-ledger::",
        "code-atlas::",
        "work-entry-gate::",
        "gvae::",
    )
    if ref.startswith(prefixes):
        return ref, None, None
    if "/visual-control/target-index/" in ref:
        mapped = {"authorityDomain": "target-index", "id": ref}
        change = {
            "field": "evidenceRefs",
            "from": ref,
            "to": mapped,
            "reason": "QUALIFY_TARGET_INDEX_PATH",
        }
        return mapped, None, change
    if "/visual-control/expanded/" in ref:
        mapped = {"authorityDomain": "visual-control", "id": ref}
        change = {
            "field": "evidenceRefs",
            "from": ref,
            "to": mapped,
            "reason": "QUALIFY_VISUAL_CONTROL_PATH",
        }
        return mapped, None, change
    if ref.startswith("repo:prisma-html/authority/rifat/"):
        mapped = {"authorityDomain": "rifat", "id": ref[5:]}
        change = {
            "field": "evidenceRefs",
            "from": ref,
            "to": mapped,
            "reason": "QUALIFY_RIFAT_REPO_REF",
        }
        return mapped, None, change
    if ref.startswith("repo:apps/terminal-de-venta-system/products/"):
        change = {
            "field": "evidenceRefs",
            "from": ref,
            "to": None,
            "reason": "LIFT_NON_AUTHORITY_PRODUCT_PROVENANCE",
        }
        return None, ref, change
    if ref.startswith("git:"):
        change = {
            "field": "evidenceRefs",
            "from": ref,
            "to": None,
            "reason": "LIFT_NON_AUTHORITY_GIT_PROVENANCE",
        }
        return None, ref, change
    change = {
        "field": "evidenceRefs",
        "from": ref,
        "to": None,
        "reason": "LIFT_UNKNOWN_NON_AUTHORITY_PROVENANCE",
    }
    return None, ref, change


def normalize_record(
    raw_record: Mapping[str, Any],
    *,
    surface: str,
    source_head: str,
    source_file: str,
    source_line: int,
    source_record_sha256: str,
    registry: Mapping[str, Any],
    atlasfin_indexes: Mapping[str, set[str]] | None = None,
    ndc_prefixes: set[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    profile = _profile(registry, surface)
    if source_head != profile.get("sourceHead"):
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:UNKNOWN_SOURCE_HEAD:{surface}:{source_head}"
        )
    if source_file not in OUTCOME_FILES:
        raise CorpusCertificationError(
            f"INVALID_PROVENANCE:UNEXPECTED_OUTCOME_FILE:{source_file}"
        )
    if not isinstance(raw_record, Mapping):
        raise CorpusCertificationError(
            "INVALID_SCHEMA:RECORD_OBJECT_REQUIRED"
        )
    if raw_record.get("surfaceKey") != surface:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:SURFACE_MISMATCH"
        )

    before = semantic_signature(raw_record)
    row = _normalized_projection_view(raw_record)
    changes: list[dict[str, Any]] = []
    lifted: list[str] = []

    if row.get("schema") is None:
        row["schema"] = CANDIDATE_SCHEMA
        changes.append(
            {
                "field": "schema",
                "from": None,
                "to": CANDIDATE_SCHEMA,
                "reason": "DECLARE_CANONICAL_CANDIDATE_SCHEMA",
            }
        )

    ndc = row.get("ndc")
    if isinstance(ndc, dict) and isinstance(ndc.get("ndcRefs"), list):
        normalized_refs = []
        for value in ndc["ndcRefs"]:
            new_value = _strip_qualified(value, "ndc")
            normalized_refs.append(new_value)
            if new_value != value:
                changes.append(
                    {
                        "field": "ndc.ndcRefs",
                        "from": value,
                        "to": new_value,
                        "reason": "RAW_NDC_FIELD_REQUIRES_UNQUALIFIED_ID",
                    }
                )
        ndc["ndcRefs"] = normalized_refs
        if isinstance(ndc.get("ndcPrimaryId"), str):
            old = ndc["ndcPrimaryId"]
            new = _strip_qualified(old, "ndc")
            ndc["ndcPrimaryId"] = new
            if old != new:
                changes.append(
                    {
                        "field": "ndc.ndcPrimaryId",
                        "from": old,
                        "to": new,
                        "reason": "RAW_NDC_FIELD_REQUIRES_UNQUALIFIED_ID",
                    }
                )

    atlasfin = row.get("atlasfin")
    if isinstance(atlasfin, dict):
        for field in (
            "atlasfinCatalogElementId",
            "atlasfinUiId",
            "atlasfinFamilyId",
            "atlasfinPresetId",
            "atlasfinRecipeId",
            "atlasfinLegacyRecipeId",
            "atlasfinAdapterId",
        ):
            if isinstance(atlasfin.get(field), str):
                old = atlasfin[field]
                new = _strip_qualified(old, "atlasfin")
                atlasfin[field] = new
                if old != new:
                    changes.append(
                        {
                            "field": f"atlasfin.{field}",
                            "from": old,
                            "to": new,
                            "reason": "RAW_ATLASFIN_FIELD_REQUIRES_UNQUALIFIED_ID",
                        }
                    )

    evidence = row.get("evidenceRefs")
    if not isinstance(evidence, list):
        raise CorpusCertificationError(
            "INVALID_SCHEMA:EVIDENCE_REFS_ARRAY_REQUIRED"
        )
    normalized_evidence = []
    for ref in evidence:
        mapped, lifted_ref, change = _normalize_evidence_ref(ref)
        if mapped is not None:
            normalized_evidence.append(mapped)
        if lifted_ref is not None:
            lifted.append(lifted_ref)
        if change is not None:
            changes.append(change)
    row["evidenceRefs"] = normalized_evidence

    after = semantic_signature(row)
    if before != after:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:SEMANTIC_MUTATION_DETECTED"
        )

    try:
        validate_candidate(
            row,
            expected_head=str(raw_record.get("baseHead") or ""),
            atlasfin=(
                dict(atlasfin_indexes)
                if atlasfin_indexes is not None
                else None
            ),
            ndc_prefixes=ndc_prefixes,
        )
    except ControlPlaneError as exc:
        message = str(exc)
        reference_tokens = (
            "AUTHORITY_",
            "ATLASFIN_REFERENCE_",
            "NDC_ID_",
            "NDC_PREFIX_",
        )
        code = (
            "INVALID_REFERENCE"
            if any(token in message for token in reference_tokens)
            else "INVALID_SCHEMA"
        )
        raise CorpusCertificationError(
            f"{code}:{message}"
        ) from exc

    cert_status = CERTIFICATION_BY_PROMOTION.get(
        row["application"]["promotionStatus"]
    )
    if cert_status is None:
        raise CorpusCertificationError(
            "INVALID_SCHEMA:PROMOTION_STATUS_UNCERTIFIABLE"
        )

    certification = {
        "schema": CERTIFICATION_SCHEMA,
        "surfaceKey": surface,
        "targetId": row["targetId"],
        "certificationStatus": cert_status,
        "source": {
            "head": source_head,
            "file": source_file,
            "line": source_line,
            "recordSha256": source_record_sha256,
            "sourceBucket": SOURCE_BUCKET[source_file],
        },
        "normalization": {
            "profile": profile.get("normalizationProfile"),
            "changed": bool(changes),
            "semanticMutation": False,
            "semanticSignatureBefore": before,
            "semanticSignatureAfter": after,
            "changes": changes,
            "liftedProvenanceRefs": lifted,
        },
        "sourceTruth": {
            "physicalStatus": raw_record.get("physicalStatus"),
            "projectionStatus": (
                raw_record.get("application") or {}
            ).get("projectionStatus"),
            "promotionStatus": (
                raw_record.get("application") or {}
            ).get("promotionStatus"),
            "workEntryDecision": (
                raw_record.get("application") or {}
            ).get("workEntryDecision"),
            "bindingStatus": (
                raw_record.get("identity") or {}
            ).get("bindingStatus"),
            "ndcResolutionStatus": (
                raw_record.get("ndc") or {}
            ).get("ndcResolutionStatus"),
        },
        "normalizedRecordSha256": sha256_value(row),
        "runtimeVisualGreen": False,
        "canonicalPromotionAuthorized": False,
    }
    return row, certification


def _invalid_certification(
    *,
    raw: bytes,
    parsed: Any,
    surface: str,
    source_head: str,
    source_file: str,
    source_line: int,
    error: Exception,
) -> dict[str, Any]:
    message = str(error)
    status = "INVALID_PROVENANCE"
    if message.startswith("INVALID_REFERENCE:"):
        status = "INVALID_REFERENCE"
    elif message.startswith("INVALID_SCHEMA:"):
        status = "INVALID_SCHEMA"
    target = (
        parsed.get("targetId")
        if isinstance(parsed, dict)
        else None
    )
    return {
        "schema": CERTIFICATION_SCHEMA,
        "surfaceKey": surface,
        "targetId": target,
        "certificationStatus": status,
        "source": {
            "head": source_head,
            "file": source_file,
            "line": source_line,
            "recordSha256": sha256_bytes(raw),
            "sourceBucket": SOURCE_BUCKET.get(source_file),
        },
        "errors": [message],
        "runtimeVisualGreen": False,
        "canonicalPromotionAuthorized": False,
    }


def semantic_review_keys(
    record: Mapping[str, Any],
) -> list[dict[str, str]]:
    keys: list[dict[str, str]] = []
    ndc = (
        record.get("ndc")
        if isinstance(record.get("ndc"), Mapping)
        else {}
    )
    visual = (
        record.get("visual")
        if isinstance(record.get("visual"), Mapping)
        else {}
    )
    atlasfin = (
        record.get("atlasfin")
        if isinstance(record.get("atlasfin"), Mapping)
        else {}
    )

    if (
        ndc.get("ndcResolutionStatus") == "RESOLVED_EXISTING"
        and ndc.get("ndcPrimaryId")
    ):
        keys.append(
            {
                "kind": "EXISTING_NDC_MEANING",
                "key": f"ndc:{ndc['ndcPrimaryId']}",
            }
        )
    if (
        visual.get("visualMeaningStatus") == "RESOLVED_EXISTING"
        and visual.get("visualMeaningId")
    ):
        keys.append(
            {
                "kind": "EXISTING_VISUAL_MEANING",
                "key": f"visual:{visual['visualMeaningId']}",
            }
        )
    if (
        visual.get("visualMeaningStatus")
        == "CANDIDATE_REVIEW_REQUIRED"
        and visual.get("visualMeaningCandidate")
    ):
        label = " ".join(
            str(visual["visualMeaningCandidate"]).split()
        ).casefold()
        keys.append(
            {
                "kind": "CANDIDATE_LABEL_REVIEW_ONLY",
                "key": f"label:{label}",
            }
        )
    if (
        atlasfin.get("atlasfinMatchStatus") == "MATCHED_RECIPE"
        and atlasfin.get("atlasfinRecipeId")
    ):
        keys.append(
            {
                "kind": "ATLASFIN_RECIPE_REVIEW_ONLY",
                "key": f"recipe:{atlasfin['atlasfinRecipeId']}",
            }
        )
    return keys


def build_semantic_review_groups(
    records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    grouped: dict[
        tuple[str, str], list[Mapping[str, Any]]
    ] = defaultdict(list)
    for row in records:
        for item in semantic_review_keys(row):
            grouped[(item["kind"], item["key"])].append(row)

    groups = []
    for (kind, key), rows in sorted(grouped.items()):
        surfaces = sorted(
            {str(row.get("surfaceKey")) for row in rows}
        )
        if kind == "ATLASFIN_RECIPE_REVIEW_ONLY":
            notes = [
                "Atlasfin recipe equality is visual recipe evidence only; "
                "it does not imply one neutral meaning."
            ]
        else:
            notes = [
                "Review key is deterministic review evidence only; "
                "it does not assign canonical authority."
            ]
        groups.append(
            {
                "kind": kind,
                "reviewKey": key,
                "recordCount": len(rows),
                "surfaceKeys": surfaces,
                "crossSurface": len(surfaces) > 1,
                "targetIds": sorted(
                    str(row.get("targetId")) for row in rows
                ),
                "canonicalMeaningResolvedByGroup": False,
                "canAutoCoalesce": False,
                "notes": notes,
            }
        )
    return {
        "schema": SEMANTIC_REVIEW_SCHEMA,
        "groups": groups,
        "allNullNoMatchGroupsExcluded": True,
        "candidateFingerprintUsedAsSemanticUniquenessProof": False,
        "canonicalIdsAssigned": False,
        "runtimeVisualGreen": False,
    }


def certify_registered_corpus(
    repo_root: Path,
    *,
    registry: Mapping[str, Any],
    target_indexes: Mapping[
        str, Mapping[str, Any]
    ] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    atlasfin_indexes = load_atlasfin_indexes(
        [repo_root / path for path in ATLASFIN_PATHS]
    )
    ndc_prefixes = ndc_prefixes_from_registry(
        load_json(repo_root / NDC_PREFIX_PATH)
    )

    normalized: list[dict[str, Any]] = []
    certifications: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    source_file_evidence: list[dict[str, Any]] = []
    source_bucket_counts: Counter[str] = Counter()

    for surface in SURFACE_ORDER:
        profile = _profile(registry, surface)
        source_head = str(profile["sourceHead"])
        surface_count = 0
        for filename in OUTCOME_FILES:
            _, data, pin = verify_registered_file(
                repo_root,
                registry,
                surface=surface,
                source_head=source_head,
                filename=filename,
            )
            source_file_evidence.append(
                {
                    "surfaceKey": surface,
                    "head": source_head,
                    "file": filename,
                    "gitBlobSha": pin["gitBlobSha"],
                    "sha256": pin["sha256"],
                    "bytes": len(data),
                }
            )
            for line_no, raw_line in enumerate(
                data.splitlines(), 1
            ):
                if not raw_line.strip():
                    continue
                surface_count += 1
                source_bucket_counts[
                    SOURCE_BUCKET[filename]
                ] += 1
                parsed: Any = None
                try:
                    parsed = json.loads(
                        raw_line.decode("utf-8")
                    )
                    row, cert = normalize_record(
                        parsed,
                        surface=surface,
                        source_head=source_head,
                        source_file=filename,
                        source_line=line_no,
                        source_record_sha256=sha256_bytes(
                            raw_line
                        ),
                        registry=registry,
                        atlasfin_indexes=atlasfin_indexes,
                        ndc_prefixes=ndc_prefixes,
                    )
                    normalized.append(row)
                    certifications.append(cert)
                except (
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                    CorpusCertificationError,
                    ControlPlaneError,
                ) as exc:
                    bad = _invalid_certification(
                        raw=raw_line,
                        parsed=parsed,
                        surface=surface,
                        source_head=source_head,
                        source_file=filename,
                        source_line=line_no,
                        error=exc,
                    )
                    certifications.append(bad)
                    invalid.append(bad)

        expected = int(profile["inputCount"])
        if surface_count != expected:
            raise CorpusCertificationError(
                "INVALID_PROVENANCE:"
                f"SURFACE_ZERO_LOSS_FAILED:{surface}:"
                f"{surface_count}:{expected}"
            )

    expected_total = int(
        registry.get("expectedCorpusCount") or 0
    )
    if len(certifications) != expected_total:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:"
            "CERTIFICATION_COUNT_MISMATCH:"
            f"{len(certifications)}:{expected_total}"
        )

    expected_buckets = registry.get(
        "expectedAggregate", {}
    ).get("sourceOutcomeCounts", {})
    if dict(source_bucket_counts) != expected_buckets:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:"
            "SOURCE_BUCKET_COUNTS_MISMATCH:"
            f"{dict(source_bucket_counts)}:{expected_buckets}"
        )

    target_ids = [row["targetId"] for row in normalized]
    duplicate_targets = sorted(
        target
        for target, count in Counter(target_ids).items()
        if count > 1
    )
    if duplicate_targets:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:DUPLICATE_TARGET_IDS:"
            + ",".join(duplicate_targets[:20])
        )

    collisions = {
        "schema": COLLISION_SCHEMA,
        "recordCount": len(normalized),
        "collisions": detect_collisions(normalized),
        "duplicateTargetIds": duplicate_targets,
        "runtimeVisualGreen": False,
        "canonicalPromotionAuthorized": False,
    }
    review_groups = build_semantic_review_groups(
        normalized
    )

    if target_indexes is None:
        target_indexes = {
            surface: json.loads(
                (repo_root / rel).read_text(
                    encoding="utf-8-sig"
                )
            )
            for surface, rel in TARGET_INDEX_PATHS.items()
        }

    wanted = set(target_ids)
    index_records: list[dict[str, Any]] = []
    for surface in SURFACE_ORDER:
        document = target_indexes.get(surface)
        if not isinstance(document, Mapping):
            raise CorpusCertificationError(
                "INVALID_PROVENANCE:"
                f"TARGET_INDEX_MISSING:{surface}"
            )
        for record in document.get("records", []):
            if (
                isinstance(record, dict)
                and record.get("targetId") in wanted
            ):
                index_records.append(record)

    current_truth = build_current_truth(
        {
            "schema":
                "prisma.visual.application.target-index.corpus.v1",
            "records": index_records,
        },
        normalized,
    )
    if current_truth.get("recordCount") != len(normalized):
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:"
            "CURRENT_TRUTH_COUNT_MISMATCH:"
            f"{current_truth.get('recordCount')}:"
            f"{len(normalized)}"
        )
    readiness = build_surface_readiness(current_truth)

    promotion_counts = Counter(
        cert.get("sourceTruth", {}).get(
            "promotionStatus"
        )
        for cert in certifications
        if cert.get("certificationStatus")
        in VALID_CERTIFICATIONS
    )
    work_entry_counts = Counter(
        cert.get("sourceTruth", {}).get(
            "workEntryDecision"
        )
        for cert in certifications
        if cert.get("certificationStatus")
        in VALID_CERTIFICATIONS
    )
    cert_counts = Counter(
        cert["certificationStatus"]
        for cert in certifications
    )
    semantic_mutations = sum(
        1
        for cert in certifications
        if cert.get("normalization", {}).get(
            "semanticMutation"
        )
        is True
    )

    expected_promotion = {
        key: value
        for key, value in registry.get(
            "expectedAggregate", {}
        ).get("promotionStatus", {}).items()
        if value
    }
    if dict(promotion_counts) != expected_promotion:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:"
            "PROMOTION_COUNTS_MISMATCH:"
            f"{dict(promotion_counts)}:"
            f"{expected_promotion}"
        )
    expected_work = {
        key: value
        for key, value in registry.get(
            "expectedAggregate", {}
        ).get("workEntryDecision", {}).items()
        if value
    }
    if dict(work_entry_counts) != expected_work:
        raise CorpusCertificationError(
            "INVALID_PROVENANCE:"
            "WORK_ENTRY_COUNTS_MISMATCH:"
            f"{dict(work_entry_counts)}:"
            f"{expected_work}"
        )

    corpus_body = b"".join(
        canonical_json(row) + b"\n"
        for row in normalized
    )
    certification_body = b"".join(
        canonical_json(row) + b"\n"
        for row in certifications
    )
    manifest = {
        "schema": CORPUS_MANIFEST_SCHEMA,
        "phase": "CANDIDATE_CORPUS_CERTIFICATION_PARALLEL",
        "candidateOnly": True,
        "expectedCorpusCount": expected_total,
        "normalizedRecordCount": len(normalized),
        "certificationRecordCount": len(certifications),
        "invalidRecordCount": len(invalid),
        "semanticMutationCount": semantic_mutations,
        "sourceFiles": source_file_evidence,
        "sourceHeads": {
            surface: _profile(
                registry, surface
            )["sourceHead"]
            for surface in SURFACE_ORDER
        },
        "materialityCatalogPolicy": MATERIALITY_POLICY,
        "materialityCatalogInspected": False,
        "broadRediscoveryPerformed": False,
        "currentlyAuthorizedCanonicalPromotions": 0,
        "runtimeVisualGreen": False,
        "wholeSurfaceApplyReady": False,
        "candidateCorpusSha256": sha256_bytes(
            corpus_body
        ),
        "certificationSha256": sha256_bytes(
            certification_body
        ),
    }
    summary = {
        "schema":
            "prisma.visual-promotion.candidate-corpus-summary.v1",
        "normalizedRecordCount": len(normalized),
        "certificationRecordCount": len(
            certifications
        ),
        "invalidRecordCount": len(invalid),
        "duplicateTargetIdCount": len(
            duplicate_targets
        ),
        "collisionCount": len(
            collisions["collisions"]
        ),
        "semanticMutationCount": semantic_mutations,
        "certificationStatusCounts": dict(
            sorted(cert_counts.items())
        ),
        "promotionStatusCounts": dict(
            sorted(promotion_counts.items())
        ),
        "workEntryDecisionCounts": dict(
            sorted(work_entry_counts.items())
        ),
        "currentlyAuthorizedCanonicalPromotions": 0,
        "runtimeVisualGreen": False,
        "wholeSurfaceApplyReady": False,
        "materialityCatalogInspected": False,
        "broadRediscoveryPerformed": False,
    }
    return {
        "manifest": manifest,
        "records": normalized,
        "certifications": certifications,
        "invalid": invalid,
        "collisions": collisions,
        "semanticReviewGroups": review_groups,
        "currentTruth": current_truth,
        "surfaceReadiness": readiness,
        "summary": summary,
    }


def _summary_markdown(
    result: Mapping[str, Any],
) -> str:
    summary = result["summary"]
    readiness = result["surfaceReadiness"]
    status = (
        "PASS_CANDIDATE_CORPUS_CERTIFIED_SOURCE_STATIC"
        if not result["invalid"]
        else "BLOCKED_INVALID_CORPUS"
    )
    lines = [
        "# Candidate Corpus Certification",
        "",
        f"Status: {status}",
        "",
        f"- normalized records: {summary['normalizedRecordCount']}",
        f"- certification records: {summary['certificationRecordCount']}",
        f"- invalid records: {summary['invalidRecordCount']}",
        f"- semantic mutations: {summary['semanticMutationCount']}",
        f"- duplicate target IDs: {summary['duplicateTargetIdCount']}",
        (
            "- currently authorized canonical promotions: "
            f"{summary['currentlyAuthorizedCanonicalPromotions']}"
        ),
        "- runtime visual green: false",
        "- whole-surface APPLY_READY: false",
        "- broad rediscovery: false",
        "- Materiality Catalog inspected: false",
        "",
        "## Surface readiness",
        "",
    ]
    for row in readiness.get("surfaces", []):
        lines.append(
            f"- {row['surfaceKey']}: "
            f"{row['readinessStatus']}; "
            f"inputs={row['inputTargetCount']}, "
            f"discovery="
            f"{row['genuineDiscoveryNeededCount']}, "
            f"eligibleCandidates="
            f"{row['eligibleCandidateCount']}, "
            "wholeSurfaceApplyReady=false"
        )
    lines.extend(
        [
            "",
            (
                "Candidate-corpus certification proves "
                "record/provenance validity only. It does "
                "not promote Identity, RIFAT, NDC, "
                "Target Index or runtime/product authority."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_corpus_outputs(
    result: Mapping[str, Any],
    out_root: Path,
) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    json_files = {
        "CORPUS_MANIFEST.json": result["manifest"],
        "COLLISIONS.json": result["collisions"],
        "SEMANTIC_REVIEW_GROUPS.json":
            result["semanticReviewGroups"],
        "CURRENT_TRUTH.json": result["currentTruth"],
        "SURFACE_READINESS.json":
            result["surfaceReadiness"],
    }
    for name, payload in json_files.items():
        (out_root / name).write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    for name, rows in (
        ("CANDIDATE_CORPUS.jsonl", result["records"]),
        (
            "CERTIFICATION.jsonl",
            result["certifications"],
        ),
        ("INVALID.jsonl", result["invalid"]),
    ):
        body = b"".join(
            canonical_json(row) + b"\n"
            for row in rows
        )
        (out_root / name).write_bytes(body)
    (out_root / "SUMMARY.md").write_text(
        _summary_markdown(result),
        encoding="utf-8",
    )


def assert_completion_invariants(
    result: Mapping[str, Any],
    *,
    expected_count: int = 2097,
) -> None:
    summary = result["summary"]
    failures = []
    if summary["normalizedRecordCount"] != expected_count:
        failures.append("NORMALIZED_RECORD_COUNT")
    if summary["certificationRecordCount"] != expected_count:
        failures.append("CERTIFICATION_RECORD_COUNT")
    if summary["invalidRecordCount"] != 0:
        failures.append("INVALID_RECORDS")
    if summary["semanticMutationCount"] != 0:
        failures.append("SEMANTIC_MUTATION")
    if summary["duplicateTargetIdCount"] != 0:
        failures.append("DUPLICATE_TARGETS")
    if (
        summary[
            "currentlyAuthorizedCanonicalPromotions"
        ]
        != 0
    ):
        failures.append("CANONICAL_PROMOTION_AUTHORIZED")
    if summary["runtimeVisualGreen"] is not False:
        failures.append("RUNTIME_VISUAL_GREEN")
    if summary["wholeSurfaceApplyReady"] is not False:
        failures.append("WHOLE_SURFACE_APPLY_READY")
    if (
        result["manifest"].get(
            "materialityCatalogInspected"
        )
        is not False
    ):
        failures.append("MATERIALITY_INSPECTED")
    if any(
        row.get("wholeSurfaceApplyReady")
        for row in result["surfaceReadiness"].get(
            "surfaces", []
        )
    ):
        failures.append("SURFACE_APPLY_READY")
    if failures:
        raise CorpusCertificationError(
            "CORPUS_COMPLETION_INVARIANTS_FAILED:"
            + ",".join(failures)
        )
