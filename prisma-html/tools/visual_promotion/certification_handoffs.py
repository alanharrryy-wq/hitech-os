from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from .control_plane import MATERIALITY_POLICY, validate_candidate

REGISTRY_SCHEMA = "prisma.visual-promotion.certification-intake.v1"
SURFACE_ORDER = ("tablet", "pc", "mobile", "shared-ui")
SURFACE_FILES = (
    "MANIFEST.json",
    "NORMALIZED.jsonl",
    "CERTIFICATION.jsonl",
    "INVALID.jsonl",
    "SUMMARY.md",
)
ATLASFIN_FILES = (
    "MANIFEST.json",
    "NORMALIZATION_POLICY.json",
    "ATLASFIN_REFERENCE_CERTIFICATION.jsonl",
    "RECIPE_REVIEW_GROUPS.json",
    "INVALID_REFS.jsonl",
    "SUMMARY.md",
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class CertificationHandoffError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha1(value: bytes) -> str:
    header = b"blob " + str(len(value)).encode("ascii") + b"\0"
    return hashlib.sha1(header + value).hexdigest()


def load_certification_registry(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(document, dict) or document.get("schema") != REGISTRY_SCHEMA:
        raise CertificationHandoffError("CERTIFICATION_INTAKE_REGISTRY_SCHEMA_INVALID")
    if document.get("materialityCatalogPolicy") != MATERIALITY_POLICY:
        raise CertificationHandoffError("MATERIALITY_POLICY_MUST_REMAIN_STANDBY")
    if document.get("broadRediscoveryAllowed") is not False:
        raise CertificationHandoffError("BROAD_REDISCOVERY_MUST_REMAIN_FORBIDDEN")
    surfaces = document.get("surfaces")
    if not isinstance(surfaces, dict) or set(surfaces) != set(SURFACE_ORDER):
        raise CertificationHandoffError("CERTIFICATION_SURFACES_INVALID")
    return document


def _profile(registry: Mapping[str, Any], surface: str) -> dict[str, Any]:
    if surface not in SURFACE_ORDER:
        raise CertificationHandoffError(f"CERTIFICATION_SURFACE_UNREGISTERED:{surface}")
    row = registry.get("surfaces", {}).get(surface)
    if not isinstance(row, dict):
        raise CertificationHandoffError(f"CERTIFICATION_PROFILE_MISSING:{surface}")
    if not HEX40.fullmatch(str(row.get("certificationHead") or "")):
        raise CertificationHandoffError(f"CERTIFICATION_HEAD_INVALID:{surface}")
    if not HEX40.fullmatch(str(row.get("rawSourceHead") or "")):
        raise CertificationHandoffError(f"RAW_SOURCE_HEAD_INVALID:{surface}")
    return row


def _pinned_file(
    repo_root: Path,
    root: str,
    pins: Mapping[str, Any],
    filename: str,
) -> tuple[Path, bytes, dict[str, Any]]:
    pin = pins.get(filename)
    if not isinstance(pin, dict):
        raise CertificationHandoffError(f"UNREGISTERED_CERTIFICATION_FILE:{filename}")
    rel = f"{str(root).rstrip('/')}/{filename}"
    path = (repo_root / rel).resolve()
    repo = repo_root.resolve()
    if repo not in path.parents:
        raise CertificationHandoffError(f"CERTIFICATION_PATH_ESCAPE:{rel}")
    if not path.is_file():
        raise CertificationHandoffError(f"CERTIFICATION_FILE_MISSING:{rel}")
    data = path.read_bytes()
    if sha256_bytes(data) != pin.get("sha256"):
        raise CertificationHandoffError(f"CERTIFICATION_FILE_SHA256_MISMATCH:{rel}")
    if git_blob_sha1(data) != pin.get("gitBlobSha"):
        raise CertificationHandoffError(f"CERTIFICATION_GIT_BLOB_MISMATCH:{rel}")
    return path, data, pin


def _jsonl(data: bytes, label: str) -> list[tuple[int, bytes, dict[str, Any]]]:
    rows: list[tuple[int, bytes, dict[str, Any]]] = []
    for line_no, raw in enumerate(data.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CertificationHandoffError(
                f"CERTIFICATION_JSONL_INVALID:{label}:{line_no}:{exc}"
            ) from exc
        if not isinstance(value, dict):
            raise CertificationHandoffError(
                f"CERTIFICATION_JSONL_OBJECT_REQUIRED:{label}:{line_no}"
            )
        rows.append((line_no, raw, value))
    return rows


def _owner_source(row: Mapping[str, Any]) -> dict[str, Any]:
    source = row.get("source") if isinstance(row.get("source"), Mapping) else {}
    provenance = (
        row.get("sourceProvenance")
        if isinstance(row.get("sourceProvenance"), Mapping)
        else {}
    )
    head = row.get("sourceHead") or source.get("head") or provenance.get("sourceHead")
    filename = row.get("sourceFile") or source.get("file") or provenance.get("sourceFile")
    line = row.get("sourceLine") or source.get("line") or provenance.get("sourceLine")
    record_hash = (
        row.get("sourceRecordSha256")
        or source.get("recordSha256")
        or source.get("sourceRecordSha256")
        or provenance.get("sourceRecordSha256")
        or provenance.get("sourceRecordHash")
    )
    return {
        "head": head,
        "file": filename,
        "line": line,
        "recordSha256": record_hash,
    }


def _semantic_mutation(row: Mapping[str, Any]) -> Any:
    if "semanticMutation" in row:
        return row.get("semanticMutation")
    normalization = row.get("normalization")
    if isinstance(normalization, Mapping):
        return normalization.get("semanticMutation")
    return None


def _by_target(rows: list[tuple[int, bytes, dict[str, Any]]], label: str) -> dict[str, tuple[int, bytes, dict[str, Any]]]:
    out: dict[str, tuple[int, bytes, dict[str, Any]]] = {}
    for item in rows:
        target = item[2].get("targetId")
        if not isinstance(target, str) or not target:
            raise CertificationHandoffError(f"TARGET_ID_REQUIRED:{label}:{item[0]}")
        if target in out:
            raise CertificationHandoffError(f"DUPLICATE_CERTIFICATION_TARGET:{label}:{target}")
        out[target] = item
    return out


def verify_surface_handoff(
    repo_root: Path,
    registry: Mapping[str, Any],
    *,
    surface: str,
    independent_records: list[dict[str, Any]],
    independent_certifications: list[dict[str, Any]],
) -> dict[str, Any]:
    profile = _profile(registry, surface)
    root = str(profile.get("certificationRoot") or "")
    pins = profile.get("files")
    if not root or not isinstance(pins, Mapping):
        raise CertificationHandoffError(f"CERTIFICATION_PINSET_INVALID:{surface}")

    file_evidence = []
    bodies: dict[str, bytes] = {}
    for filename in SURFACE_FILES:
        _, data, pin = _pinned_file(repo_root, root, pins, filename)
        bodies[filename] = data
        file_evidence.append(
            {
                "file": filename,
                "gitBlobSha": pin["gitBlobSha"],
                "sha256": pin["sha256"],
                "bytes": len(data),
            }
        )
    if bodies["INVALID.jsonl"].strip():
        raise CertificationHandoffError(f"CERTIFICATION_INVALID_NOT_EMPTY:{surface}")

    normalized_rows = _jsonl(bodies["NORMALIZED.jsonl"], f"{surface}:NORMALIZED")
    certification_rows = _jsonl(
        bodies["CERTIFICATION.jsonl"], f"{surface}:CERTIFICATION"
    )
    expected = int(profile.get("expectedCount") or -1)
    if len(normalized_rows) != expected or len(certification_rows) != expected:
        raise CertificationHandoffError(
            f"CERTIFICATION_ZERO_LOSS_FAILED:{surface}:"
            f"{len(normalized_rows)}:{len(certification_rows)}:{expected}"
        )

    owner_normalized = _by_target(normalized_rows, f"{surface}:NORMALIZED")
    owner_certified = _by_target(certification_rows, f"{surface}:CERTIFICATION")
    independent_by_target = {
        row["targetId"]: row for row in independent_records if row.get("surfaceKey") == surface
    }
    independent_cert_by_target = {
        row["targetId"]: row
        for row in independent_certifications
        if row.get("surfaceKey") == surface
    }
    expected_targets = set(independent_by_target)
    if (
        set(owner_normalized) != expected_targets
        or set(owner_certified) != expected_targets
        or set(independent_cert_by_target) != expected_targets
    ):
        raise CertificationHandoffError(f"CERTIFICATION_TARGET_SET_MISMATCH:{surface}")

    owner_meta: dict[str, dict[str, Any]] = {}
    for target in sorted(expected_targets):
        norm_line, norm_raw, norm = owner_normalized[target]
        validate_candidate(norm, expected_head=str(norm.get("baseHead") or ""))
        if canonical_json(norm) != canonical_json(independent_by_target[target]):
            raise CertificationHandoffError(
                f"CERTIFICATION_NORMALIZED_RECORD_MISMATCH:{surface}:{target}"
            )

        cert_line, cert_raw, cert = owner_certified[target]
        status = cert.get("certificationStatus")
        if not isinstance(status, str) or not status.startswith("VALID_"):
            raise CertificationHandoffError(
                f"CERTIFICATION_STATUS_INVALID:{surface}:{target}:{status}"
            )
        if status != independent_cert_by_target[target].get("certificationStatus"):
            raise CertificationHandoffError(
                f"CERTIFICATION_STATUS_MISMATCH:{surface}:{target}"
            )
        if _semantic_mutation(cert) is not False:
            raise CertificationHandoffError(
                f"CERTIFICATION_SEMANTIC_MUTATION:{surface}:{target}"
            )
        source = _owner_source(cert)
        expected_source = independent_cert_by_target[target].get("source", {})
        if source["head"] != profile.get("rawSourceHead"):
            raise CertificationHandoffError(
                f"CERTIFICATION_SOURCE_HEAD_MISMATCH:{surface}:{target}"
            )
        if (
            not isinstance(source["file"], str)
            or Path(source["file"]).name != str(expected_source.get("file") or "")
        ):
            raise CertificationHandoffError(
                f"CERTIFICATION_SOURCE_FILE_MISMATCH:{surface}:{target}"
            )
        if source["line"] != expected_source.get("line"):
            raise CertificationHandoffError(
                f"CERTIFICATION_SOURCE_LINE_MISMATCH:{surface}:{target}"
            )
        if source["recordSha256"] != expected_source.get("recordSha256"):
            raise CertificationHandoffError(
                f"CERTIFICATION_SOURCE_RECORD_HASH_MISMATCH:{surface}:{target}"
            )
        if not HEX64.fullmatch(str(source["recordSha256"] or "")):
            raise CertificationHandoffError(
                f"CERTIFICATION_SOURCE_RECORD_HASH_INVALID:{surface}:{target}"
            )
        owner_meta[target] = {
            "certificationHead": profile["certificationHead"],
            "certificationBranch": profile["certificationBranch"],
            "normalizedFile": f"{root}/NORMALIZED.jsonl",
            "normalizedLine": norm_line,
            "normalizedRecordSha256": sha256_bytes(norm_raw),
            "certificationFile": f"{root}/CERTIFICATION.jsonl",
            "certificationLine": cert_line,
            "certificationRecordSha256": sha256_bytes(cert_raw),
            "certificationStatus": status,
        }

    return {
        "surfaceKey": surface,
        "certificationBranch": profile["certificationBranch"],
        "certificationHead": profile["certificationHead"],
        "rawSourceHead": profile["rawSourceHead"],
        "recordCount": expected,
        "invalidCount": 0,
        "semanticMutationCount": 0,
        "normalizedRecordsExactMatch": True,
        "sourceProvenanceExactMatch": True,
        "files": file_evidence,
        "ownerByTarget": owner_meta,
    }


def verify_atlasfin_handoff(
    repo_root: Path,
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    profile = registry.get("atlasfin")
    if not isinstance(profile, Mapping):
        raise CertificationHandoffError("ATLASFIN_CERTIFICATION_PROFILE_MISSING")
    head = str(profile.get("certificationHead") or "")
    if not HEX40.fullmatch(head):
        raise CertificationHandoffError("ATLASFIN_CERTIFICATION_HEAD_INVALID")
    root = str(profile.get("certificationRoot") or "")
    pins = profile.get("files")
    if not root or not isinstance(pins, Mapping):
        raise CertificationHandoffError("ATLASFIN_CERTIFICATION_PINSET_INVALID")

    bodies: dict[str, bytes] = {}
    file_evidence = []
    for filename in ATLASFIN_FILES:
        _, data, pin = _pinned_file(repo_root, root, pins, filename)
        bodies[filename] = data
        file_evidence.append(
            {
                "file": filename,
                "gitBlobSha": pin["gitBlobSha"],
                "sha256": pin["sha256"],
                "bytes": len(data),
            }
        )
    if bodies["INVALID_REFS.jsonl"].strip():
        raise CertificationHandoffError("ATLASFIN_INVALID_REFS_NOT_EMPTY")

    manifest = json.loads(bodies["MANIFEST.json"].decode("utf-8-sig"))
    policy = json.loads(bodies["NORMALIZATION_POLICY.json"].decode("utf-8-sig"))
    groups = json.loads(bodies["RECIPE_REVIEW_GROUPS.json"].decode("utf-8-sig"))
    refs = _jsonl(
        bodies["ATLASFIN_REFERENCE_CERTIFICATION.jsonl"],
        "atlasfin:REFERENCE_CERTIFICATION",
    )
    expected_refs = int(profile.get("expectedReferenceCount") or -1)
    if len(refs) != expected_refs:
        raise CertificationHandoffError(
            f"ATLASFIN_REFERENCE_COUNT_MISMATCH:{len(refs)}:{expected_refs}"
        )
    cert = manifest.get("certification") if isinstance(manifest, Mapping) else {}
    if (
        cert.get("totalSurfaceOutcomeRecords") != int(registry["expectedSurfaceRecordCount"])
        or cert.get("totalNonNullAtlasfinReferences") != expected_refs
        or cert.get("hardInvalidReferenceCount") != 0
        or cert.get("semanticMutationCount") != 0
        or cert.get("canonicalPromotionPerformed") is not False
        or cert.get("runtimeVisualGreen") is not False
    ):
        raise CertificationHandoffError("ATLASFIN_MANIFEST_INVARIANTS_FAILED")
    authority = manifest.get("atlasfinAuthority") or {}
    if (
        authority.get("materialityCatalogPolicy") != MATERIALITY_POLICY
        or authority.get("materialityCatalogInspected") is not False
    ):
        raise CertificationHandoffError("ATLASFIN_MATERIALITY_POLICY_FAILED")
    if (
        policy.get("materialityCatalogPolicy") != MATERIALITY_POLICY
        or policy.get("materialityCatalogInspected") is not False
        or policy.get("automaticFallbackAllowed") is not False
        or policy.get("canonicalIdMintingAllowed") is not False
        or policy.get("productRuntimeMutationAllowed") is not False
    ):
        raise CertificationHandoffError("ATLASFIN_NORMALIZATION_POLICY_FAILED")
    if (
        groups.get("groupCount") != int(profile.get("expectedRecipeReviewGroupCount") or -1)
        or groups.get("semanticCoalescingAllowed") is not False
        or groups.get("reviewOnly") is not True
    ):
        raise CertificationHandoffError("ATLASFIN_RECIPE_REVIEW_GROUPS_INVALID")
    for group in groups.get("groups", []):
        if (
            not isinstance(group, Mapping)
            or group.get("semanticCoalescingAllowed") is not False
            or group.get("reviewOnly") is not True
        ):
            raise CertificationHandoffError("ATLASFIN_RECIPE_GROUP_AUTO_COALESCE_FORBIDDEN")

    raw_heads = {
        row.get("rawSourceHead")
        for row in registry["surfaces"].values()
        if isinstance(row, Mapping)
    }
    for line_no, _, row in refs:
        if (
            row.get("certificationStatus") != "VALID_REFERENCE"
            or row.get("semanticMutation") is not False
            or row.get("authorityDomain") != "atlasfin"
            or row.get("sourceHead") not in raw_heads
            or not HEX64.fullmatch(str(row.get("sourceRecordSha256") or ""))
        ):
            raise CertificationHandoffError(
                f"ATLASFIN_REFERENCE_ROW_INVALID:{line_no}"
            )

    return {
        "certificationBranch": profile["certificationBranch"],
        "certificationHead": head,
        "sourceBridgeHead": profile["sourceBridgeHead"],
        "referenceCount": expected_refs,
        "hardInvalidReferenceCount": 0,
        "semanticMutationCount": 0,
        "recipeReviewGroupCount": groups["groupCount"],
        "materialityCatalogInspected": False,
        "semanticCoalescingAllowed": False,
        "files": file_evidence,
    }


def verify_all_certification_handoffs(
    repo_root: Path,
    registry: Mapping[str, Any],
    *,
    independent_result: Mapping[str, Any],
) -> dict[str, Any]:
    records = list(independent_result.get("records", []))
    certifications = list(independent_result.get("certifications", []))
    surfaces = {}
    owner_by_target: dict[str, dict[str, Any]] = {}
    for surface in SURFACE_ORDER:
        verification = verify_surface_handoff(
            repo_root,
            registry,
            surface=surface,
            independent_records=records,
            independent_certifications=certifications,
        )
        owner_by_target.update(verification.pop("ownerByTarget"))
        surfaces[surface] = verification
    if len(owner_by_target) != int(registry["expectedSurfaceRecordCount"]):
        raise CertificationHandoffError(
            "CERTIFICATION_OWNER_TARGET_COUNT_MISMATCH"
        )
    atlasfin = verify_atlasfin_handoff(repo_root, registry)
    return {
        "schema": "prisma.visual-promotion.certification-handoff-verification.v1",
        "status": "PASS_ALL_CERTIFICATION_HANDOFFS",
        "surfaceRecordCount": len(owner_by_target),
        "surfaceCertificationCount": len(surfaces),
        "atlasfinCertificationCount": 1,
        "surfaces": surfaces,
        "atlasfin": atlasfin,
        "ownerByTarget": owner_by_target,
        "materialityCatalogInspected": False,
        "broadRediscoveryPerformed": False,
        "runtimeVisualGreen": False,
        "canonicalPromotionAuthorized": False,
    }


def enrich_global_result_with_handoffs(
    result: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> dict[str, Any]:
    out = copy.deepcopy(dict(result))
    owner = verification.get("ownerByTarget")
    if not isinstance(owner, Mapping):
        raise CertificationHandoffError("OWNER_CERTIFICATION_MAP_REQUIRED")
    for cert in out["certifications"]:
        target = cert.get("targetId")
        meta = owner.get(target)
        if not isinstance(meta, Mapping):
            raise CertificationHandoffError(
                f"OWNER_CERTIFICATION_MISSING:{target}"
            )
        cert["ownerCertification"] = copy.deepcopy(dict(meta))

    manifest = out["manifest"]
    manifest["phase"] = "CANDIDATE_CORPUS_FINAL_AGGREGATION"
    manifest["certificationVerificationStatus"] = verification["status"]
    manifest["certificationHeads"] = {
        surface: data["certificationHead"]
        for surface, data in verification["surfaces"].items()
    }
    manifest["atlasfinCertificationHead"] = verification["atlasfin"][
        "certificationHead"
    ]
    manifest["atlasfinSourceBridgeHead"] = verification["atlasfin"][
        "sourceBridgeHead"
    ]
    manifest["acceptedCertificationInputs"] = {
        "surfaces": copy.deepcopy(verification["surfaces"]),
        "atlasfin": copy.deepcopy(verification["atlasfin"]),
    }
    manifest["allCertificationRecordHashesPinned"] = True

    certification_body = b"".join(
        canonical_json(row) + b"\n" for row in out["certifications"]
    )
    manifest["certificationSha256"] = sha256_bytes(certification_body)

    summary = out["summary"]
    summary["certificationHandoffsVerified"] = True
    summary["surfaceCertificationHandoffCount"] = len(
        verification["surfaces"]
    )
    summary["atlasfinCertificationHandoffCount"] = 1
    summary["acceptedSurfaceCertificationRecordCount"] = verification[
        "surfaceRecordCount"
    ]
    summary["atlasfinReferenceCertificationCount"] = verification["atlasfin"][
        "referenceCount"
    ]
    summary["certificationVerificationStatus"] = verification["status"]
    return out


def assert_final_aggregation_invariants(
    result: Mapping[str, Any],
    *,
    expected_count: int = 2097,
) -> None:
    summary = result.get("summary", {})
    manifest = result.get("manifest", {})
    failures = []
    if summary.get("normalizedRecordCount") != expected_count:
        failures.append("NORMALIZED_RECORD_COUNT")
    if summary.get("certificationRecordCount") != expected_count:
        failures.append("CERTIFICATION_RECORD_COUNT")
    if summary.get("invalidRecordCount") != 0:
        failures.append("INVALID_RECORDS")
    if summary.get("semanticMutationCount") != 0:
        failures.append("SEMANTIC_MUTATION")
    if summary.get("duplicateTargetIdCount") != 0:
        failures.append("DUPLICATE_TARGETS")
    if summary.get("currentlyAuthorizedCanonicalPromotions") != 0:
        failures.append("CANONICAL_PROMOTIONS")
    if summary.get("runtimeVisualGreen") is not False:
        failures.append("RUNTIME_VISUAL_GREEN")
    if summary.get("wholeSurfaceApplyReady") is not False:
        failures.append("WHOLE_SURFACE_APPLY_READY")
    if summary.get("certificationHandoffsVerified") is not True:
        failures.append("CERTIFICATION_HANDOFFS")
    if summary.get("surfaceCertificationHandoffCount") != 4:
        failures.append("SURFACE_HANDOFF_COUNT")
    if summary.get("atlasfinCertificationHandoffCount") != 1:
        failures.append("ATLASFIN_HANDOFF_COUNT")
    if manifest.get("allCertificationRecordHashesPinned") is not True:
        failures.append("CERTIFICATION_HASH_PINS")
    if manifest.get("materialityCatalogInspected") is not False:
        failures.append("MATERIALITY_INSPECTED")
    if any(
        not isinstance(row.get("ownerCertification"), Mapping)
        for row in result.get("certifications", [])
    ):
        failures.append("OWNER_CERTIFICATION_PROVENANCE")
    if failures:
        raise CertificationHandoffError(
            "FINAL_AGGREGATION_INVARIANTS_FAILED:" + ",".join(failures)
        )
