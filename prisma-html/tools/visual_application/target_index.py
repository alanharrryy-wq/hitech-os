from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .hashing import canonical_json_bytes, pretty_json_bytes, sha256_bytes, sha256_file

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
RIFAT = ROOT / "authority" / "rifat"
OUT = RIFAT / "prisma-ui" / "visual-control" / "target-index"
EXPANDED = RIFAT / "prisma-ui" / "visual-control" / "expanded"
SURFACES = ("tablet", "pc", "mobile", "web", "chart-lab", "control-center", "shared-ui")
SUPPORTED_PROJECTION_MODES = {"exact-byte-copy", "existing-rifat-tablet-generator"}
EXACT_KIND = "EXACT_APPLICATION_TARGET"
CENSUS_KIND = "VISUAL_CONTROL_CENSUS_TARGET"
ENFORCED = "GVAE_ENFORCED"
DISCOVERY_ONLY = "DISCOVERY_ONLY"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL object required: {path}:{number}")
        rows.append(value)
    return rows


def _manifest_match(entries: list[dict[str, Any]], evidence_path: str | None, surface: str | None) -> list[dict[str, Any]]:
    if not evidence_path or not surface:
        return []
    normalized = evidence_path.replace("\\", "/").lstrip("/")
    candidates = {normalized, f"apps/terminal-de-venta-system/{normalized}"}
    return [
        entry
        for entry in entries
        if entry.get("surface") == surface
        and str(entry.get("output", "")).replace("\\", "/") in candidates
    ]


def _actual_hash(repo_root: Path, raw: Any) -> str | None:
    if not isinstance(raw, str) or not raw:
        return None
    path = repo_root / raw
    try:
        resolved = path.resolve(strict=False)
        resolved.relative_to(repo_root.resolve())
    except Exception:
        return None
    if not path.is_file() or path.is_symlink():
        return None
    return sha256_file(path)


def _projection_fields(repo_root: Path, entries: list[dict[str, Any]], surface: str, product_path: str | None) -> tuple[dict[str, Any] | None, list[str]]:
    matches = _manifest_match(entries, product_path, surface)
    missing: list[str] = []
    entry = matches[0] if len(matches) == 1 else None
    if len(matches) != 1:
        missing.append("projection")
        return None, missing

    if entry.get("manualEditsForbidden") is not True:
        missing.append("projection-policy")
    if entry.get("projectionMode") not in SUPPORTED_PROJECTION_MODES:
        missing.append("projection-mode")
    src_actual = _actual_hash(repo_root, entry.get("source"))
    out_actual = _actual_hash(repo_root, entry.get("output"))
    if src_actual is None or src_actual.lower() != str(entry.get("sourceSha256") or "").lower():
        missing.append("source-hash-drift")
    if out_actual is None or out_actual.lower() != str(entry.get("outputSha256") or "").lower():
        missing.append("projection-hash-drift")
    return entry, missing


def _projection_payload(entry: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "canonicalSourcePath": entry.get("source") if entry else None,
        "generatedOutputPath": entry.get("output") if entry else None,
        "sourceSha256": entry.get("sourceSha256") if entry else None,
        "outputSha256": entry.get("outputSha256") if entry else None,
        "projectionMode": entry.get("projectionMode") if entry else None,
        "manualEditsForbidden": entry.get("manualEditsForbidden") if entry else None,
    }


def _exact_records(
    *,
    repo_root: Path,
    entries: list[dict[str, Any]],
    bindings: dict[str, Any],
    recipes: dict[str, Any],
    adapters: dict[str, Any],
    layers: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    recipe_rows = {row.get("recipeId"): row for row in recipes.get("recipes", []) if row.get("recipeId")}
    adapter_rows = {row.get("id"): row for row in adapters.get("adapters", []) if row.get("id")}
    layer_rows: dict[str, list[dict[str, Any]]] = {}
    for row in layers.get("certifiedLayers", []):
        layer_id = row.get("layer_id")
        if layer_id:
            layer_rows.setdefault(layer_id, []).append(row)

    records: list[dict[str, Any]] = []
    target_ids: list[str] = []

    for binding in bindings.get("bindings", []):
        selector = binding.get("selector") or {}
        surface = selector.get("surfaceId")
        recipe_id = selector.get("recipePresetId")
        semantic = selector.get("neutralMeaningId")
        for target in binding.get("targets", []):
            target_id = target.get("targetId")
            target_ids.append(target_id)
            evidence = target.get("evidence") or {}
            manifest_entry, projection_missing = _projection_fields(
                repo_root,
                entries,
                str(surface or ""),
                evidence.get("sourceCssPath"),
            )
            missing: list[str] = list(projection_missing)

            if binding.get("status") != "RESOLVED" or target.get("status") != "RESOLVED":
                missing.append("binding")
            layer_id = target.get("layerId")
            if not layer_id:
                missing.append("layer")
            if not semantic or semantic == "*":
                missing.append("semantic")
            if recipe_id in (None, "*") or recipe_id not in recipe_rows:
                missing.append("recipe")
            elif recipe_rows[recipe_id].get("recipeCoverageStatus") not in (None, "COMPLETE"):
                missing.append("recipe-coverage")

            adapter_id = target.get("adapterId")
            adapter = adapter_rows.get(adapter_id) if adapter_id else None
            if not adapter:
                missing.append("adapter")
            elif adapter.get("surface") != surface:
                missing.append("adapter-surface")
            elif adapter.get("readiness") not in {"BINDING_READY_SOURCE_ONLY", "NEUTRAL_SOURCE_READY"}:
                missing.append("adapter-readiness")

            layer_matches = layer_rows.get(layer_id, []) if layer_id else []
            layer = layer_matches[0] if len(layer_matches) == 1 else None
            if layer_id:
                if len(layer_matches) != 1:
                    missing.append("layer-certification")
                else:
                    expected_pairs = {
                        "surface": surface,
                        "selector": target.get("selector"),
                        "implementationLayerId": target.get("implementationLayerId"),
                        "neutralMeaningId": semantic,
                    }
                    for key, value in expected_pairs.items():
                        if layer.get(key) != value:
                            missing.append("layer-authority-mismatch")
                    if layer.get("certificationStatus") != "CERTIFIED_EXACT_SOURCE_MATCH":
                        missing.append("layer-certification")
                    if layer.get("runtimeMutationAllowed") is not True or layer.get("productApplicationAllowed") is not True:
                        missing.append("layer-application-policy")

            record = {
                "targetId": target_id,
                "recordKind": EXACT_KIND,
                "enforcement": ENFORCED,
                "surface": surface,
                "selector": target.get("selector"),
                "jsonRoot": target.get("jsonRoot"),
                "bindingId": binding.get("bindingId"),
                "layerId": layer_id,
                "implementationLayerId": target.get("implementationLayerId"),
                "semanticMeaningId": semantic,
                "recipeId": recipe_id,
                "adapterId": adapter_id,
                **_projection_payload(manifest_entry),
                "status": "APPLY_READY" if not missing else "BLOCKED",
                "blockers": sorted(set(missing)),
            }
            records.append(record)

    duplicates = sorted(str(value) for value, count in Counter(target_ids).items() if value and count > 1)
    return records, duplicates


def _census_target_id(surface: str, row: dict[str, Any]) -> str:
    coordinate = {
        "surface": surface,
        "file": row.get("file"),
        "selector": row.get("selector"),
        "layerId": row.get("layer_id"),
    }
    digest = hashlib.sha256(canonical_json_bytes(coordinate)).hexdigest()[:20].upper()
    surface_id = surface.upper().replace("-", "_")
    return f"TGT.CENSUS.{surface_id}.{digest}.V1"


def _census_records(
    *,
    repo_root: Path,
    entries: list[dict[str, Any]],
    adapters: dict[str, Any],
) -> list[dict[str, Any]]:
    adapter_by_surface = {
        row.get("surface"): row
        for row in adapters.get("adapters", [])
        if row.get("surface") and row.get("id")
    }
    records: list[dict[str, Any]] = []
    seen_coordinates: set[tuple[str, str, str, str]] = set()

    for surface in SURFACES:
        for row in load_jsonl(EXPANDED / surface / "layers.jsonl"):
            file_path = row.get("file")
            selector = row.get("selector")
            layer_id = row.get("layer_id")
            if row.get("surface") != surface:
                continue
            if row.get("evidenceClass") != "activeRuntime":
                continue
            if not isinstance(file_path, str) or not file_path.lower().endswith((".css", ".scss")):
                continue
            if not isinstance(selector, str) or not selector.strip():
                continue
            if not isinstance(layer_id, str) or not layer_id:
                continue

            coordinate = (surface, file_path, selector, layer_id)
            if coordinate in seen_coordinates:
                continue
            seen_coordinates.add(coordinate)

            manifest_entry, projection_missing = _projection_fields(
                repo_root,
                entries,
                surface,
                file_path,
            )
            adapter = adapter_by_surface.get(surface)
            blockers = {
                "semantic",
                "recipe",
                "exact-binding",
                "layer-application-policy",
                *projection_missing,
            }
            if not adapter:
                blockers.add("adapter")
                adapter_id = None
            else:
                adapter_id = adapter.get("id")
                if adapter.get("readiness") not in {"BINDING_READY_SOURCE_ONLY", "NEUTRAL_SOURCE_READY"}:
                    blockers.add("adapter-readiness")

            records.append(
                {
                    "targetId": _census_target_id(surface, row),
                    "recordKind": CENSUS_KIND,
                    "enforcement": DISCOVERY_ONLY,
                    "surface": surface,
                    "selector": selector,
                    "jsonRoot": None,
                    "bindingId": None,
                    "layerId": layer_id,
                    "implementationLayerId": layer_id,
                    "semanticMeaningId": None,
                    "recipeId": None,
                    "adapterId": adapter_id,
                    "visualRegion": row.get("visualRegion"),
                    "layerType": row.get("layer"),
                    "safetyClassification": row.get("safetyClassification"),
                    "ownerCss": row.get("ownerCss") or file_path,
                    **_projection_payload(manifest_entry),
                    "status": "BLOCKED",
                    "blockers": sorted(blockers),
                }
            )

    return records


def _coverage(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_surface: dict[str, Any] = {}
    for surface in SURFACES:
        rows = [row for row in records if row.get("surface") == surface]
        exact = [row for row in rows if row.get("recordKind") == EXACT_KIND]
        census = [row for row in rows if row.get("recordKind") == CENSUS_KIND]
        by_surface[surface] = {
            "recordCount": len(rows),
            "exactApplicationTargetCount": len(exact),
            "censusTargetCount": len(census),
            "applyReadyCount": sum(1 for row in exact if row.get("status") == "APPLY_READY"),
            "blockedExactCount": sum(1 for row in exact if row.get("status") == "BLOCKED"),
            "discoveryOnlyCount": len(census),
            "wholeSurfaceApplyReady": bool(rows)
            and bool(exact)
            and not census
            and all(row.get("status") == "APPLY_READY" for row in exact),
        }
    return {
        "surfaceCount": len(SURFACES),
        "bySurface": by_surface,
        "allSurfacesRepresented": all(by_surface[surface]["recordCount"] > 0 for surface in SURFACES),
        "wholeSurfaceApplyReadyCount": sum(
            1 for surface in SURFACES if by_surface[surface]["wholeSurfaceApplyReady"]
        ),
    }


def build_index(root: Path = ROOT) -> dict[str, Any]:
    repo_root = root.parent
    rifat = root / "authority" / "rifat"
    manifest = load(rifat / "visual-source-manifest.json")
    bindings = load(rifat / "identity" / "registries" / "element-bindings.registry.json")
    recipes = load(rifat / "identity" / "registries" / "recipe.registry.json")
    adapters = load(rifat / "identity" / "registries" / "surface-adapters.registry.json")
    layers = load(rifat / "prisma-ui" / "visual-control" / "layers.json")
    expanded_manifest = load(rifat / "prisma-ui" / "visual-control" / "expanded" / "manifest.json")
    entries = manifest.get("entries", [])

    global_blockers: list[str] = []
    bad_modes = sorted(
        {
            str(entry.get("projectionMode"))
            for entry in entries
            if entry.get("projectionMode") not in SUPPORTED_PROJECTION_MODES
        }
    )
    if bad_modes:
        global_blockers.append("unsupported-projection-modes:" + ",".join(bad_modes))
    if expanded_manifest.get("status") != "CERTIFIED":
        global_blockers.append("expanded-visual-control-not-certified")
    if expanded_manifest.get("scopeMode") != "ALL_SURFACES_CANONICAL":
        global_blockers.append("expanded-visual-control-not-global")
    if set(expanded_manifest.get("surfaces") or []) != set(SURFACES):
        global_blockers.append("expanded-visual-control-surface-set-incomplete")

    exact, duplicate_exact = _exact_records(
        repo_root=repo_root,
        entries=entries,
        bindings=bindings,
        recipes=recipes,
        adapters=adapters,
        layers=layers,
    )
    if duplicate_exact:
        global_blockers.append("duplicate-target-ids:" + ",".join(duplicate_exact))

    census = _census_records(repo_root=repo_root, entries=entries, adapters=adapters)
    records = exact + census
    records.sort(
        key=lambda row: (
            str(row.get("surface")),
            str(row.get("recordKind")),
            str(row.get("targetId")),
        )
    )

    target_ids = [row.get("targetId") for row in records]
    duplicate_all = sorted(
        str(value) for value, count in Counter(target_ids).items() if value and count > 1
    )
    if duplicate_all:
        global_blockers.append("duplicate-all-target-ids:" + ",".join(duplicate_all))

    counts = Counter(row["status"] for row in records)
    kinds = Counter(row["recordKind"] for row in records)
    enforcement = Counter(row["enforcement"] for row in records)
    payload = {
        "schema": "prisma.visual.application.target-index.v1",
        "version": "2.0.0",
        "authority": "current-rifat-and-identity-source",
        "generated": True,
        "manualEditsForbidden": True,
        "supportedProjectionModes": sorted(SUPPORTED_PROJECTION_MODES),
        "recordCount": len(records),
        "countsByStatus": dict(sorted(counts.items())),
        "countsByKind": dict(sorted(kinds.items())),
        "countsByEnforcement": dict(sorted(enforcement.items())),
        "coverage": _coverage(records),
        "records": records,
        "globalBlockers": sorted(set(global_blockers)),
        "hardTruth": (
            "Census records prove physical visual coordinates only. DISCOVERY_ONLY records are never "
            "APPLY_READY and do not authorize product mutation."
        ),
    }
    payload["indexDigest"] = sha256_bytes(canonical_json_bytes(payload))
    return payload


def render_files(index: dict[str, Any]) -> dict[Path, bytes]:
    enforced_records = [
        row for row in index["records"]
        if row.get("enforcement") != DISCOVERY_ONLY
    ]
    manifest = {
        key: value for key, value in index.items()
        if key != "records"
    }
    manifest["records"] = enforced_records
    manifest["recordStorage"] = {
        "totalRecordCount": index["recordCount"],
        "manifestEnforcedRecordCount": len(enforced_records),
        "censusStorage": "per-surface-files",
        "censusDuplicatedInManifest": False,
    }
    files = {OUT / "manifest.json": pretty_json_bytes(manifest)}
    for surface in SURFACES:
        view = {
            "schema": "prisma.visual.application.target-index.surface.v1",
            "surface": surface,
            "indexDigest": index["indexDigest"],
            "coverage": index["coverage"]["bySurface"][surface],
            "records": [row for row in index["records"] if row.get("surface") == surface],
        }
        files[OUT / f"{surface}.json"] = pretty_json_bytes(view)
    return files


def write(index: dict[str, Any]) -> None:
    for path, data in render_files(index).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def check(index: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for path, data in render_files(index).items():
        if not path.exists():
            problems.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_bytes() != data:
            problems.append(f"drift:{path.relative_to(ROOT)}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    index = build_index()

    if args.write:
        write(index)
        print(
            json.dumps(
                {
                    "status": "WROTE",
                    "indexDigest": index["indexDigest"],
                    "recordCount": index["recordCount"],
                    "countsByKind": index["countsByKind"],
                    "coverage": index["coverage"],
                },
                indent=2,
            )
        )
        return 0

    if args.check:
        problems = check(index)
        print(
            json.dumps(
                {"status": "PASS" if not problems else "FAIL", "problems": problems},
                indent=2,
            )
        )
        return 1 if problems else 0

    print(json.dumps(index, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
