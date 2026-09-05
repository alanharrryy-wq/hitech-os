#!/usr/bin/env python3
"""Read-only Atlasfin bridge for the PRISMA visual-promotion cohort.

This module intentionally consumes authority and candidate evidence without
mutating Atlasfin registries, Identity/RIFAT authority, product runtime, or
generated product projections.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

BRIDGE_SCHEMA = "prisma.atlasfin.visual-promotion-bridge.v1"
BRIDGE_VERSION = "1.0.0"
SURFACE_KEYS = ("tablet", "pc", "mobile", "shared-ui")
ALLOWED_AUTHORITY_DOMAINS = {
    "ndc",
    "atlasfin",
    "identity",
    "rifat",
    "visual-control",
    "target-index",
    "projection-manifest",
    "factory-ledger",
    "code-atlas",
    "work-entry-gate",
    "gvae",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

ATLAS_DATA = Path("prisma-html/extras/atlasfin/assets/data")
BRIDGE_ROOT = Path("prisma-html/extras/atlasfin/bridge")
CANDIDATE_ROOT = Path("prisma-html/governance/visual-promotion/candidates")
MATERIALITY_CATALOG = Path(
    "apps/terminal-de-venta-system/products/pc/app/public/"
    "surface-visual-governor/reference-visual/latest/materiality-catalog.registry.json"
)
VISUAL_CORE_FEEDS = (
    Path("prisma-html/extras/atlasfin/assets/data/visual-core.status.json"),
    Path("prisma-html/reports/visual-core/VISUAL_CORE_STATUS.json"),
)

REGISTRIES: dict[str, tuple[str, str, str | None]] = {
    "properties": ("visual-property.registry.json", "id", None),
    "families": ("visual-family.registry.json", "familyId", "atlasfinFamilyId"),
    "presets": ("visual-preset.registry.json", "presetId", "atlasfinPresetId"),
    "recipes": ("visual-recipe.registry.json", "recipeId", "atlasfinRecipeId"),
    "states": ("visual-state.registry.json", "id", None),
    "variants": ("visual-variant.registry.json", "id", None),
    "adapters": ("surface-adapter.registry.json", "id", "atlasfinAdapterId"),
    "assets": ("visual-asset.registry.json", "id", None),
}

WORKER_OUTCOME_FILES = ("CANDIDATES.jsonl", "UNRESOLVED.jsonl", "CONFLICTS.jsonl")


class BridgeError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _contained(repo: Path, rel: Path) -> Path:
    if rel == MATERIALITY_CATALOG:
        raise BridgeError("MATERIALITY_CATALOG_STANDBY_FORBIDS_READ")
    repo = repo.resolve()
    path = (repo / rel).resolve()
    try:
        path.relative_to(repo)
    except ValueError as exc:
        raise BridgeError(f"PATH_ESCAPES_REPOSITORY:{rel.as_posix()}") from exc
    return path


def _read_json(repo: Path, rel: Path) -> dict[str, Any]:
    path = _contained(repo, rel)
    if not path.is_file():
        raise BridgeError(f"REQUIRED_JSON_MISSING:{rel.as_posix()}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BridgeError(f"INVALID_JSON:{rel.as_posix()}:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise BridgeError(f"JSON_OBJECT_REQUIRED:{rel.as_posix()}")
    return value


def _optional_json(repo: Path, rel: Path) -> dict[str, Any] | None:
    path = _contained(repo, rel)
    if not path.is_file():
        return None
    return _read_json(repo, rel)


def _git_head(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=20,
    )
    if proc.returncode:
        raise BridgeError("BASE_HEAD_UNAVAILABLE")
    head = proc.stdout.strip().lower()
    if not HEX40.fullmatch(head):
        raise BridgeError(f"BASE_HEAD_INVALID:{head}")
    return head


def _resolve_base_head(repo: Path, base_head: str | None) -> str:
    if base_head is not None:
        head = base_head.strip().lower()
        if not HEX40.fullmatch(head):
            raise BridgeError("BASE_HEAD_MUST_BE_40_HEX")
        return head
    return _git_head(repo)


def authority_ref(
    authority_domain: str,
    raw_id: str,
    *,
    version: str | None = None,
    sha256: str | None = None,
) -> dict[str, Any]:
    domain = str(authority_domain or "").strip()
    identifier = str(raw_id or "").strip()
    if domain not in ALLOWED_AUTHORITY_DOMAINS:
        raise BridgeError(f"AUTHORITY_DOMAIN_INVALID:{domain}")
    if not identifier:
        raise BridgeError("AUTHORITY_ID_REQUIRED")
    if sha256 is not None and not HEX64.fullmatch(str(sha256).lower()):
        raise BridgeError("AUTHORITY_SHA256_INVALID")
    out: dict[str, Any] = {"authorityDomain": domain, "id": identifier}
    if version:
        out["version"] = str(version)
    if sha256:
        out["sha256"] = str(sha256).lower()
    return out


def _source_descriptor(repo: Path, rel: Path) -> dict[str, Any]:
    path = _contained(repo, rel)
    if not path.is_file():
        return {"path": rel.as_posix(), "availabilityState": "PENDING_NOT_PRESENT", "sha256": None}
    return {
        "path": rel.as_posix(),
        "availabilityState": "PRESENT",
        "sha256": sha256_file(path),
    }


def _flatten_catalog(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    sections = manifest.get("sections")
    if not isinstance(sections, list):
        raise BridgeError("ATLAS_SECTIONS_LIST_REQUIRED")
    for section in sections:
        if not isinstance(section, dict):
            raise BridgeError("ATLAS_SECTION_OBJECT_REQUIRED")
        section_letter = section.get("letter")
        page = section.get("page")
        items = section.get("items")
        if not isinstance(items, list):
            raise BridgeError(f"ATLAS_SECTION_ITEMS_REQUIRED:{section_letter}")
        for item in items:
            if not isinstance(item, dict):
                raise BridgeError(f"ATLAS_CATALOG_ITEM_OBJECT_REQUIRED:{section_letter}")
            raw_id = str(item.get("id") or "").strip()
            if not raw_id:
                raise BridgeError(f"ATLAS_CATALOG_ITEM_ID_REQUIRED:{section_letter}")
            records.append(
                {
                    "recordKind": "atlasfinCatalogElement",
                    "atlasfinCatalogElementId": raw_id,
                    "authorityRef": authority_ref("atlasfin", raw_id),
                    "section": section_letter,
                    "page": page,
                    "index": item.get("index"),
                    "name": item.get("name"),
                    "description": item.get("description"),
                    "slug": item.get("slug"),
                }
            )
    declared = manifest.get("total_items")
    if isinstance(declared, int) and declared != len(records):
        raise BridgeError(f"ATLAS_CATALOG_COUNT_DRIFT:{declared}:{len(records)}")
    return records


def _registry_records(
    registry_name: str,
    registry: dict[str, Any],
    id_key: str,
    canonical_field: str | None,
) -> list[dict[str, Any]]:
    items = registry.get("items")
    if not isinstance(items, list):
        raise BridgeError(f"ATLASFIN_REGISTRY_ITEMS_REQUIRED:{registry_name}")
    version = registry.get("version")
    records: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise BridgeError(f"ATLASFIN_REGISTRY_ITEM_OBJECT_REQUIRED:{registry_name}:{index}")
        raw_id = str(item.get(id_key) or "").strip()
        if not raw_id:
            raise BridgeError(f"ATLASFIN_REGISTRY_ITEM_ID_REQUIRED:{registry_name}:{index}:{id_key}")
        record: dict[str, Any] = {
            "recordKind": f"atlasfin{registry_name[:-1].capitalize()}",
            "authorityRef": authority_ref("atlasfin", raw_id, version=str(version) if version else None),
            "payload": copy.deepcopy(item),
        }
        if canonical_field:
            record[canonical_field] = raw_id
        records.append(record)
    return records


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return records, [f"READ_ERROR:{path.name}:{type(exc).__name__}"]
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"INVALID_JSONL:{path.name}:{line_no}")
            continue
        if not isinstance(value, dict):
            errors.append(f"JSONL_OBJECT_REQUIRED:{path.name}:{line_no}")
            continue
        records.append(value)
    return records, errors


def _candidate_conformance(record: dict[str, Any], surface_key: str, source: str, line_no: int) -> list[str]:
    errors: list[str] = []
    if record.get("candidateOnly") is not True:
        errors.append(f"CANDIDATE_ONLY_REQUIRED:{source}:{line_no}")
    head = str(record.get("baseHead") or "").lower()
    if not HEX40.fullmatch(head):
        errors.append(f"CANDIDATE_BASE_HEAD_INVALID:{source}:{line_no}")
    if record.get("surfaceKey") != surface_key:
        errors.append(f"CANDIDATE_SURFACE_MISMATCH:{source}:{line_no}")
    if not str(record.get("targetId") or "").strip():
        errors.append(f"CANDIDATE_TARGET_ID_REQUIRED:{source}:{line_no}")
    return errors


def _worker_bridge_record(
    record: dict[str, Any],
    *,
    source_lane: str,
    source_file: str,
    source_line: int,
) -> dict[str, Any]:
    physical = record.get("physical") if isinstance(record.get("physical"), dict) else {}
    ndc = record.get("ndc") if isinstance(record.get("ndc"), dict) else {}
    visual = record.get("visual") if isinstance(record.get("visual"), dict) else {}
    atlasfin = record.get("atlasfin") if isinstance(record.get("atlasfin"), dict) else {}
    identity = record.get("identity") if isinstance(record.get("identity"), dict) else {}
    application = record.get("application") if isinstance(record.get("application"), dict) else {}
    evidence = record.get("evidence") if isinstance(record.get("evidence"), dict) else {}

    return {
        "recordKind": record.get("recordKind"),
        "candidateOnly": True,
        "baseHead": record.get("baseHead"),
        "surfaceKey": record.get("surfaceKey"),
        "targetId": record.get("targetId"),
        "physicalStatus": record.get("physicalStatus"),
        "routeId": physical.get("routeId"),
        "regionId": physical.get("regionId"),
        "slotId": physical.get("slotId"),
        "componentId": physical.get("componentId"),
        "componentUiId": physical.get("componentUiId"),
        "ownerId": physical.get("ownerId"),
        "ownerFile": physical.get("ownerFile"),
        "renderSourceFile": physical.get("renderSourceFile"),
        "styleSourceFile": physical.get("styleSourceFile"),
        "selector": physical.get("selector"),
        "implementationLayerId": physical.get("implementationLayerId"),
        "applicationLayerId": application.get("applicationLayerId"),
        "ndcPrimaryId": ndc.get("ndcPrimaryId"),
        "ndcRefs": ndc.get("ndcRefs", []),
        "ndcResolutionStatus": ndc.get("ndcResolutionStatus"),
        "visualMeaningId": visual.get("visualMeaningId"),
        "visualMeaningCandidate": visual.get("visualMeaningCandidate"),
        "visualMeaningStatus": visual.get("visualMeaningStatus"),
        "atlasfinCatalogElementId": atlasfin.get("atlasfinCatalogElementId"),
        "atlasfinFamilyId": atlasfin.get("atlasfinFamilyId"),
        "atlasfinPresetId": atlasfin.get("atlasfinPresetId"),
        "atlasfinRecipeId": atlasfin.get("atlasfinRecipeId"),
        "atlasfinLegacyRecipeId": atlasfin.get("atlasfinLegacyRecipeId"),
        "atlasfinAdapterId": atlasfin.get("atlasfinAdapterId"),
        "atlasfinMatchStatus": atlasfin.get("atlasfinMatchStatus"),
        "identityProfileId": identity.get("identityProfileId"),
        "identityRecipeId": identity.get("identityRecipeId"),
        "identityAdapterId": identity.get("identityAdapterId"),
        "existingBindingId": identity.get("existingBindingId"),
        "bindingCandidateKey": identity.get("bindingCandidateKey"),
        "bindingStatus": identity.get("bindingStatus"),
        "projectionStatus": application.get("projectionStatus"),
        "promotionStatus": application.get("promotionStatus") or record.get("promotionStatus"),
        "workEntryDecision": application.get("workEntryDecision") or record.get("workEntryDecision"),
        "evidenceRefs": record.get("evidenceRefs") or evidence.get("evidenceRefs") or [],
        "confidence": record.get("confidence") or evidence.get("confidence"),
        "blockers": record.get("blockers") or evidence.get("blockers") or [],
        "notes": record.get("notes") or evidence.get("notes"),
        "workerSource": {
            "surfaceKey": source_lane,
            "file": source_file,
            "line": source_line,
        },
    }


def _load_worker_lane(repo: Path, surface_key: str) -> dict[str, Any]:
    lane_rel = CANDIDATE_ROOT / surface_key
    lane = _contained(repo, lane_rel)
    if not lane.is_dir():
        return {
            "surfaceKey": surface_key,
            "workerDataState": "PENDING_NOT_PRESENT",
            "manifest": None,
            "outcomeCounts": {name: 0 for name in WORKER_OUTCOME_FILES},
            "records": [],
            "blockers": [],
        }

    manifest_rel = lane_rel / "MANIFEST.json"
    manifest = _optional_json(repo, manifest_rel)
    blockers: list[str] = []
    records: list[dict[str, Any]] = []
    counts: dict[str, int] = {}

    for filename in WORKER_OUTCOME_FILES:
        path = lane / filename
        if not path.is_file():
            counts[filename] = 0
            continue
        rows, row_errors = _read_jsonl(path)
        blockers.extend(row_errors)
        counts[filename] = len(rows)
        for idx, row in enumerate(rows, start=1):
            blockers.extend(_candidate_conformance(row, surface_key, filename, idx))
            records.append(
                _worker_bridge_record(
                    row,
                    source_lane=surface_key,
                    source_file=filename,
                    source_line=idx,
                )
            )

    state = "INVALID" if blockers else "PRESENT"
    return {
        "surfaceKey": surface_key,
        "workerDataState": state,
        "manifest": manifest,
        "outcomeCounts": counts,
        "records": records,
        "blockers": sorted(set(blockers)),
    }


def _load_visual_core(repo: Path) -> dict[str, Any]:
    for rel in VISUAL_CORE_FEEDS:
        payload = _optional_json(repo, rel)
        if payload is None:
            continue
        return {
            "feedState": "PRESENT",
            "path": rel.as_posix(),
            "schema": payload.get("schema"),
            "visualCoreStatus": payload.get("status"),
            "selectedProfileId": (
                payload.get("identity", {}).get("selectedProfileId")
                if isinstance(payload.get("identity"), dict)
                else None
            ),
            "applicationEngine": payload.get("applicationEngine"),
            "surfaces": payload.get("surfaces", []),
            "authorityRef": authority_ref(
                "identity",
                str(payload.get("schema") or "prisma.visual.core.status.v1"),
            ),
        }
    return {
        "feedState": "PENDING_NOT_PRESENT",
        "path": VISUAL_CORE_FEEDS[0].as_posix(),
        "schema": None,
        "visualCoreStatus": None,
        "selectedProfileId": None,
        "applicationEngine": None,
        "surfaces": [],
        "authorityRef": None,
    }


def _hash_matches(repo: Path, rel: str | None, expected: str | None) -> tuple[bool | None, str | None]:
    if not rel or not expected:
        return None, None
    path = _contained(repo, Path(rel))
    if not path.is_file():
        return False, None
    actual = sha256_file(path)
    return actual == str(expected).lower(), actual


def _cobrar_reference(repo: Path) -> dict[str, Any]:
    pilot_rel = ATLAS_DATA / "visual-control.cobrar.pilot.json"
    app_rel = ATLAS_DATA / "visual-application.cobrar.current.json"
    pilot = _read_json(repo, pilot_rel)
    application = _read_json(repo, app_rel)

    p = pilot.get("pilot") if isinstance(pilot.get("pilot"), dict) else {}
    recipe = pilot.get("recipe") if isinstance(pilot.get("recipe"), dict) else {}
    plan = pilot.get("plan") if isinstance(pilot.get("plan"), dict) else {}
    after = application.get("after") if isinstance(application.get("after"), dict) else {}

    product_files = application.get("productFiles") if isinstance(application.get("productFiles"), list) else []
    authority_files = application.get("authorityFiles") if isinstance(application.get("authorityFiles"), list) else []
    product_file = str(product_files[0]) if product_files else None
    authority_file = str(authority_files[0]) if authority_files else None
    owner_file = str(p.get("ownerFile") or "") or None

    checks = {
        "product": _hash_matches(repo, product_file, after.get("productCssSha256")),
        "authority": _hash_matches(repo, authority_file, after.get("authorityCssSha256")),
        "owner": _hash_matches(repo, owner_file, after.get("ownerSha256")),
    }
    known_checks = [matched for matched, _ in checks.values() if matched is not None]
    projection_status = "UNRESOLVED"
    confidence = "high"
    blockers: list[str] = []
    if known_checks and all(known_checks):
        projection_status = "CURRENT"
        confidence = "verified"
    elif known_checks and not all(known_checks):
        projection_status = "DRIFT"
        confidence = "verified"
        blockers.append("COBRAR_CURRENT_APPLICATION_HASH_DRIFT")

    evidence_refs = [
        pilot_rel.as_posix(),
        app_rel.as_posix(),
    ]
    mamastrophic = (
        pilot.get("evidence", {}).get("mamastrophic")
        if isinstance(pilot.get("evidence"), dict)
        and isinstance(pilot.get("evidence", {}).get("mamastrophic"), dict)
        else None
    )
    if mamastrophic and mamastrophic.get("artifactName"):
        evidence_refs.append(str(mamastrophic["artifactName"]))

    refs = [
        authority_ref("atlasfin", str(pilot.get("controlId") or "ATLASFIN.CONTROL.TABLET.POS.COBRAR.V1")),
    ]
    if recipe.get("recipeId"):
        refs.append(authority_ref("identity", str(recipe["recipeId"])))
    if p.get("bindingId"):
        refs.append(authority_ref("identity", str(p["bindingId"])))
    if p.get("layerId"):
        refs.append(authority_ref("rifat", str(p["layerId"])))

    return {
        "recordKind": "atlasfinExactTargetReference",
        "candidateOnly": False,
        "surfaceKey": "tablet",
        "targetId": None,
        "physicalStatus": "CURRENT" if projection_status == "CURRENT" else "DRIFT",
        "routeId": p.get("routeId"),
        "regionId": p.get("regionId"),
        "slotId": p.get("slotId"),
        "componentId": p.get("componentId"),
        "componentUiId": p.get("componentUiId"),
        "ownerId": p.get("ownerId"),
        "ownerFile": p.get("ownerFile"),
        "styleSourceFile": p.get("styleSourceFile"),
        "selector": p.get("selector"),
        "implementationLayerId": p.get("implementationLayerId"),
        "applicationLayerId": p.get("layerId"),
        "ndcPrimaryId": None,
        "ndcRefs": [],
        "ndcResolutionStatus": "UNRESOLVED",
        "visualMeaningId": None,
        "visualMeaningCandidate": None,
        "visualMeaningStatus": "UNRESOLVED",
        "atlasfinUiId": pilot.get("controlId"),
        "atlasfinCatalogElementId": None,
        "atlasfinFamilyId": None,
        "atlasfinPresetId": None,
        "atlasfinRecipeId": None,
        "atlasfinAdapterId": plan.get("adapterId"),
        "atlasfinMatchStatus": "NOT_APPLICABLE",
        "identityProfileId": None,
        "identityRecipeId": recipe.get("recipeId"),
        "identityAdapterId": None,
        "existingBindingId": p.get("bindingId"),
        "bindingCandidateKey": None,
        "bindingStatus": "EXISTING_RESOLVED" if p.get("bindingStatus") == "RESOLVED" else "BLOCKED",
        "projectionStatus": projection_status,
        "promotionStatus": "NOT_APPLICABLE",
        "workEntryDecision": None,
        "evidenceRefs": evidence_refs,
        "confidence": confidence,
        "blockers": blockers,
        "notes": (
            "Certified Cobrar evidence is exposed as a read-only Atlasfin reference. "
            "It is not a new authorization or a new canonical Identity record."
        ),
        "authorityRefs": refs,
        "hashEvidence": {
            key: {"matches": match, "actualSha256": actual}
            for key, (match, actual) in checks.items()
        },
        "applicationEvidenceState": application.get("status"),
    }


def build_bridge(repo: Path, *, base_head: str | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    head = _resolve_base_head(repo, base_head)

    atlas_manifest_rel = ATLAS_DATA / "atlas.manifest.json"
    atlas_manifest = _read_json(repo, atlas_manifest_rel)
    catalog = _flatten_catalog(atlas_manifest)

    registries: dict[str, list[dict[str, Any]]] = {}
    registry_sources: dict[str, dict[str, Any]] = {}
    for registry_name, (filename, id_key, canonical_field) in REGISTRIES.items():
        rel = ATLAS_DATA / filename
        payload = _read_json(repo, rel)
        registries[registry_name] = _registry_records(
            registry_name,
            payload,
            id_key,
            canonical_field,
        )
        registry_sources[registry_name] = _source_descriptor(repo, rel)

    worker_lanes = {surface: _load_worker_lane(repo, surface) for surface in SURFACE_KEYS}
    worker_records = [
        row
        for surface in SURFACE_KEYS
        for row in worker_lanes[surface]["records"]
    ]

    source_paths = [
        atlas_manifest_rel,
        ATLAS_DATA / "registry-index.json",
        ATLAS_DATA / "visual-control.cobrar.pilot.json",
        ATLAS_DATA / "visual-application.cobrar.current.json",
    ]

    snapshot = {
        "schema": BRIDGE_SCHEMA,
        "version": BRIDGE_VERSION,
        "baseHead": head,
        "readOnly": True,
        "atlasfinRole": "priority-human-cockpit-reference",
        "authorityPolicy": {
            "atlasfinIsEditableAuthority": False,
            "atlasfinWritesProduct": False,
            "workersProposeCanonicalComposersAssign": True,
            "unknownStaysUnknown": True,
            "broadRediscoveryAllowed": False,
        },
        "materialityCatalog": {
            "policy": "STANDBY_USER_INVOKED_ONLY",
            "inspected": False,
            "automaticFallbackAllowed": False,
            "automaticPromotionAllowed": False,
        },
        "sources": {
            "core": [_source_descriptor(repo, rel) for rel in source_paths],
            "registries": registry_sources,
        },
        "atlasfin": {
            "manifestStatus": atlas_manifest.get("status"),
            "catalogElementCount": len(catalog),
            "catalogElements": catalog,
            "registries": registries,
        },
        "visualCore": _load_visual_core(repo),
        "promotionWorkers": worker_lanes,
        "promotionRecords": worker_records,
        "currentReferences": {
            "cobrar": _cobrar_reference(repo),
        },
        "summary": {
            "catalogElementCount": len(catalog),
            "workerRecordCount": len(worker_records),
            "pendingWorkerCount": sum(
                1 for row in worker_lanes.values()
                if row["workerDataState"] == "PENDING_NOT_PRESENT"
            ),
            "invalidWorkerCount": sum(
                1 for row in worker_lanes.values()
                if row["workerDataState"] == "INVALID"
            ),
        },
    }
    snapshot["integrity"] = {
        "algorithm": "SHA-256",
        "canonicalPayloadSha256": sha256_bytes(canonical_json(snapshot).encode("utf-8")),
    }
    return snapshot


def _walk_authority_refs(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if "authorityDomain" in value and "id" in value:
            yield value
        for child in value.values():
            yield from _walk_authority_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_authority_refs(child)


def validate_bridge(snapshot: dict[str, Any], *, strict_workers: bool = True) -> list[str]:
    errors: list[str] = []
    if snapshot.get("schema") != BRIDGE_SCHEMA:
        errors.append("BRIDGE_SCHEMA_INVALID")
    if snapshot.get("readOnly") is not True:
        errors.append("BRIDGE_MUST_BE_READ_ONLY")
    head = str(snapshot.get("baseHead") or "")
    if not HEX40.fullmatch(head):
        errors.append("BRIDGE_BASE_HEAD_INVALID")
    policy = snapshot.get("materialityCatalog")
    if not isinstance(policy, dict) or policy.get("policy") != "STANDBY_USER_INVOKED_ONLY":
        errors.append("MATERIALITY_POLICY_INVALID")
    elif policy.get("inspected") is not False:
        errors.append("MATERIALITY_MUST_REMAIN_UNINSPECTED")
    if snapshot.get("atlasfin", {}).get("catalogElementCount") != 418:
        errors.append("ATLASFIN_418_ELEMENT_CATALOG_REQUIRED")

    for ref in _walk_authority_refs(snapshot):
        if ref.get("authorityDomain") not in ALLOWED_AUTHORITY_DOMAINS:
            errors.append(f"AUTHORITY_DOMAIN_INVALID:{ref.get('authorityDomain')}")
        if not str(ref.get("id") or "").strip():
            errors.append("AUTHORITY_ID_REQUIRED")

    workers = snapshot.get("promotionWorkers")
    if not isinstance(workers, dict):
        errors.append("PROMOTION_WORKERS_REQUIRED")
    else:
        for surface in SURFACE_KEYS:
            lane = workers.get(surface)
            if not isinstance(lane, dict):
                errors.append(f"WORKER_LANE_REQUIRED:{surface}")
                continue
            state = lane.get("workerDataState")
            if state not in {"PENDING_NOT_PRESENT", "PRESENT", "INVALID"}:
                errors.append(f"WORKER_DATA_STATE_INVALID:{surface}:{state}")
            if strict_workers and state == "INVALID":
                errors.extend(f"WORKER_DATA_INVALID:{surface}:{item}" for item in lane.get("blockers", []))

    cob = snapshot.get("currentReferences", {}).get("cobrar", {})
    if cob.get("identityRecipeId") and cob.get("atlasfinRecipeId") == cob.get("identityRecipeId"):
        errors.append("ATLASFIN_IDENTITY_RECIPE_DOMAIN_COLLAPSE")
    if cob.get("bindingStatus") not in {"EXISTING_RESOLVED", "BLOCKED"}:
        errors.append("COBRAR_BINDING_STATUS_INVALID")
    if cob.get("projectionStatus") not in {"CURRENT", "DRIFT", "UNRESOLVED"}:
        errors.append("COBRAR_PROJECTION_STATUS_INVALID")
    return sorted(set(errors))


def _write_snapshot(repo: Path, out: Path, snapshot: dict[str, Any]) -> None:
    repo = repo.resolve()
    bridge_root = (repo / BRIDGE_ROOT).resolve()
    target = out if out.is_absolute() else (repo / out)
    target = target.resolve()
    try:
        target.relative_to(bridge_root)
    except ValueError as exc:
        raise BridgeError("OUTPUT_MUST_STAY_INSIDE_ATLASFIN_BRIDGE") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRISMA Chat 5 Atlasfin read-only promotion bridge")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--base-head", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Build in memory and fail closed on bridge errors")
    check.add_argument("--allow-invalid-workers", action="store_true")

    snap = sub.add_parser("snapshot", help="Emit deterministic bridge JSON")
    snap.add_argument("--out", default=None)
    snap.add_argument("--allow-invalid-workers", action="store_true")
    return parser


def _find_repo_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).resolve()
        if not (root / "prisma-html").is_dir():
            raise BridgeError("REPO_ROOT_INVALID")
        return root
    start = Path(__file__).resolve()
    for parent in [start.parent, *start.parents]:
        if (parent / "prisma-html").is_dir() and (parent / "AGENTS.md").is_file():
            return parent
    raise BridgeError("REPO_ROOT_NOT_FOUND")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repo = _find_repo_root(args.repo_root)
        snapshot = build_bridge(repo, base_head=args.base_head)
        errors = validate_bridge(snapshot, strict_workers=not args.allow_invalid_workers)
        if errors:
            print(json.dumps({"result": "BLOCKED", "errors": errors}, indent=2), file=sys.stderr)
            return 2
        if args.command == "snapshot":
            if args.out:
                _write_snapshot(repo, Path(args.out), snapshot)
            else:
                print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        else:
            print(
                json.dumps(
                    {
                        "result": "PASS_ATLASFIN_BRIDGE_READ_ONLY",
                        "baseHead": snapshot["baseHead"],
                        "catalogElementCount": snapshot["summary"]["catalogElementCount"],
                        "workerRecordCount": snapshot["summary"]["workerRecordCount"],
                        "pendingWorkerCount": snapshot["summary"]["pendingWorkerCount"],
                        "visualCoreFeedState": snapshot["visualCore"]["feedState"],
                        "materialityCatalogInspected": False,
                        "cobrarProjectionStatus": snapshot["currentReferences"]["cobrar"]["projectionStatus"],
                    },
                    indent=2,
                )
            )
        return 0
    except BridgeError as exc:
        print(json.dumps({"result": "BLOCKED", "errors": [str(exc)]}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
