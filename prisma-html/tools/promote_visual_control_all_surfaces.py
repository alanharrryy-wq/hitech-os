#!/usr/bin/env python3
"""Promote a fresh all-surface Visual Control census into canonical RIFAT authority.

This tool never scans product source itself. It accepts only a certified all-surface
output produced by tools/quality/ui-visual-control.mjs, validates the complete
machine-detail shards, and promotes that evidence into prisma-html authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
APP_ROOT = REPO_ROOT / "apps" / "terminal-de-venta-system"
DEFAULT_SOURCE = APP_ROOT / ".prisma-ui" / "visual-control"
DEST = ROOT / "authority" / "rifat" / "prisma-ui" / "visual-control"
BINDINGS_PATH = ROOT / "authority" / "rifat" / "identity" / "registries" / "bindings.registry.json"
ADAPTERS_PATH = ROOT / "authority" / "rifat" / "identity" / "registries" / "surface-adapters.registry.json"

SURFACES = ("shared-ui", "tablet", "pc", "mobile", "web", "chart-lab", "control-center")
END_SURFACES = ("tablet", "pc", "mobile", "web", "chart-lab", "control-center")
CORE_FILES = (
    "registry.json",
    "surfaces.json",
    "routes.json",
    "components.json",
    "editable-slots.json",
    "owners.json",
    "layers.json",
    "risks.json",
    "reuse-report.json",
)
EXPANDED_FILES = (
    "routes.jsonl",
    "components.jsonl",
    "visual-regions.jsonl",
    "editable-slots.jsonl",
    "layers.jsonl",
    "assets.jsonl",
    "owners-componentOwners.jsonl",
    "owners-cssOwners.jsonl",
    "owners-assetOwners.jsonl",
    "owners-tokenThemeOwners.jsonl",
    "owners-routeOwners.jsonl",
    "owners-regionOwners.jsonl",
)


class PromotionError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PromotionError(f"JSON object required: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def jsonl_rows(path: Path, *, surface: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise PromotionError(f"missing expanded authority shard: {path}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PromotionError(f"invalid JSONL {path}:{number}: {exc}") from exc
        if not isinstance(row, dict):
            raise PromotionError(f"JSONL object required {path}:{number}")
        if row.get("surface") != surface:
            raise PromotionError(
                f"surface mismatch {path}:{number}: expected={surface} actual={row.get('surface')}"
            )
        rows.append(row)
    return rows


def normalized_registry(source: Path) -> dict[str, Any]:
    registry = load_json(source / "registry.json")
    if registry.get("schema") != "prisma.ui.visual-control.registry.v1":
        raise PromotionError("visual-control registry schema mismatch")
    if registry.get("status") != "CERTIFIED":
        raise PromotionError(f"visual-control registry not certified: {registry.get('status')}")
    if registry.get("scopeMode") != "ALL_SURFACES_CANONICAL":
        raise PromotionError(f"surface-scoped source cannot promote globally: {registry.get('scopeMode')}")
    if registry.get("canonicalGlobal") is not True or registry.get("sourceSurface") is not None:
        raise PromotionError("global promotion requires canonicalGlobal=true and sourceSurface=null")
    if set(registry.get("targetSurfaces") or []) != set(SURFACES):
        raise PromotionError(
            f"target surface set mismatch: {sorted(registry.get('targetSurfaces') or [])}"
        )
    if set(registry.get("runtimeTargetSurfaces") or []) != set(END_SURFACES):
        raise PromotionError(
            f"runtime target surface set mismatch: {sorted(registry.get('runtimeTargetSurfaces') or [])}"
        )
    # createdAt/branch/repoHead are execution evidence, not canonical authority bytes.
    registry = dict(registry)
    registry.pop("createdAt", None)
    registry.pop("branch", None)
    registry.pop("repoHead", None)
    registry["promotionPolicy"] = {
        "allSurfaceOnly": True,
        "surfaceScopedRunsMayNotPromoteGlobal": True,
        "expandedMachineDetailRequired": True,
        "productSourceMutation": False,
    }
    return registry


def validate_source(source: Path) -> dict[str, Any]:
    registry = normalized_registry(source)
    surfaces = load_json(source / "surfaces.json")
    routes = load_json(source / "routes.json")
    owners = load_json(source / "owners.json")
    slots = load_json(source / "editable-slots.json")
    layers = load_json(source / "layers.json")
    expanded = load_json(source / "expanded" / "manifest.json")

    for label, doc in (
        ("surfaces", surfaces),
        ("routes", routes),
        ("owners", owners),
        ("editable-slots", slots),
        ("layers", layers),
        ("expanded", expanded),
    ):
        if doc.get("status") != "CERTIFIED":
            raise PromotionError(f"{label} is not CERTIFIED: {doc.get('status')}")

    surface_rows = surfaces.get("surfaces")
    if not isinstance(surface_rows, list):
        raise PromotionError("surfaces array missing")
    seen_surfaces = [row.get("surface") for row in surface_rows if isinstance(row, dict)]
    if set(seen_surfaces) != set(SURFACES) or len(seen_surfaces) != len(SURFACES):
        raise PromotionError(f"visual-control surfaces mismatch: {seen_surfaces}")

    if expanded.get("schema") != "prisma.ui.visual-control.expanded-manifest.v1":
        raise PromotionError("expanded manifest schema mismatch")
    if expanded.get("scopeMode") != "ALL_SURFACES_CANONICAL" or expanded.get("canonicalGlobal") is not True:
        raise PromotionError("expanded authority is not all-surface canonical")
    if set(expanded.get("surfaces") or []) != set(SURFACES):
        raise PromotionError("expanded surface set mismatch")

    counts = expanded.get("countsBySurface")
    if not isinstance(counts, dict):
        raise PromotionError("expanded countsBySurface missing")

    line_count_map = {
        "routes": "routes.jsonl",
        "components": "components.jsonl",
        "visualRegions": "visual-regions.jsonl",
        "editableSlots": "editable-slots.jsonl",
        "layers": "layers.jsonl",
        "assets": "assets.jsonl",
        "routeOwners": "owners-routeOwners.jsonl",
        "regionOwners": "owners-regionOwners.jsonl",
        "cssOwners": "owners-cssOwners.jsonl",
    }

    verified_counts: dict[str, dict[str, int]] = {}
    for surface in SURFACES:
        row = counts.get(surface)
        if not isinstance(row, dict):
            raise PromotionError(f"expanded counts missing surface: {surface}")
        verified_counts[surface] = {}
        for field, filename in line_count_map.items():
            rows = jsonl_rows(source / "expanded" / surface / filename, surface=surface)
            actual = len(rows)
            expected = row.get(field)
            if expected != actual:
                raise PromotionError(
                    f"expanded count mismatch {surface}/{field}: manifest={expected} actual={actual}"
                )
            verified_counts[surface][field] = actual
        for filename in EXPANDED_FILES:
            path = source / "expanded" / surface / filename
            if not path.is_file():
                raise PromotionError(f"expanded shard missing: {path}")

        if verified_counts[surface]["layers"] <= 0:
            raise PromotionError(f"surface has no visual layers: {surface}")
        if verified_counts[surface]["editableSlots"] <= 0:
            raise PromotionError(f"surface has no editable slots: {surface}")
        if verified_counts[surface]["regionOwners"] <= 0:
            raise PromotionError(f"surface has no region owners: {surface}")
        if surface in END_SURFACES and verified_counts[surface]["routes"] <= 0:
            raise PromotionError(f"end surface has no routes: {surface}")

    return {
        "registry": registry,
        "surfaces": surfaces,
        "routes": routes,
        "owners": owners,
        "slots": slots,
        "layers": layers,
        "expanded": expanded,
        "verifiedCounts": verified_counts,
    }


def build_bindings(validated: dict[str, Any]) -> dict[str, Any]:
    counts = validated["verifiedCounts"]
    rows: list[dict[str, Any]] = []
    for surface in SURFACES:
        c = counts[surface]
        if surface == "shared-ui":
            readiness = "NEUTRAL_SOURCE_READY"
            missing: list[str] = []
        else:
            readiness = "CERTIFIED_BINDING_SOURCE"
            missing = []
        rows.append(
            {
                "surface": surface,
                "readiness": readiness,
                "routeSource": "authority/rifat/prisma-ui/visual-control/routes.json",
                "ownerSource": "authority/rifat/prisma-ui/visual-control/owners.json",
                "slotSource": "authority/rifat/prisma-ui/visual-control/editable-slots.json",
                "layerSource": "authority/rifat/prisma-ui/visual-control/layers.json",
                "expandedSource": f"authority/rifat/prisma-ui/visual-control/expanded/{surface}/",
                "routeCount": c["routes"],
                "routeOwnerCount": c["routeOwners"],
                "regionOwnerCount": c["regionOwners"],
                "editableSlotCount": c["editableSlots"],
                "layerCount": c["layers"],
                "missing": missing,
                "runtimeProjectionAllowed": False,
            }
        )
    return {
        "schema": "prisma.identity.bindings.registry.v1",
        "version": "1.1.0",
        "surfaceCount": len(SURFACES),
        "bindings": rows,
        "policy": {
            "certifiedMeansDetailedOwnersAndSlotsExist": True,
            "discoveryRoutesAreNotCertification": True,
            "runtimeProjectionDefault": False,
            "allSurfaceCanonicalPromotionRequired": True,
            "surfaceScopedRunsMayNotPromoteGlobal": True,
            "expandedMachineDetailRequiredForExactTargets": True,
        },
    }


def build_adapters() -> dict[str, Any]:
    current = load_json(ADAPTERS_PATH)
    rows: list[dict[str, Any]] = []
    for row in current.get("adapters", []):
        if not isinstance(row, dict):
            continue
        item = dict(row)
        surface = item.get("surface")
        if surface == "shared-ui":
            item["readiness"] = "NEUTRAL_SOURCE_READY"
        elif surface in END_SURFACES:
            item["readiness"] = "BINDING_READY_SOURCE_ONLY"
        rows.append(item)
    if set(item.get("surface") for item in rows) != set(SURFACES):
        raise PromotionError("surface adapter registry does not contain the seven canonical surfaces")
    return {
        "schema": "prisma.identity.surface-adapters.registry.v1",
        "version": "1.1.0",
        "adapterCount": len(rows),
        "adapters": rows,
    }


def expected_files(source: Path) -> dict[Path, bytes]:
    validated = validate_source(source)
    result: dict[Path, bytes] = {}

    for name in CORE_FILES:
        src = source / name
        if not src.is_file():
            raise PromotionError(f"missing source file: {src}")
        if name == "registry.json":
            data = canonical_bytes(validated["registry"])
        else:
            data = src.read_bytes()
        result[DEST / name] = data

    expanded_manifest = dict(validated["expanded"])
    expanded_manifest.pop("branch", None)
    expanded_manifest.pop("repoHead", None)
    expanded_manifest["promotionPolicy"] = {
        "allSurfaceOnly": True,
        "surfaceScopedRunsMayNotPromoteGlobal": True,
        "fullMachineDetail": True,
    }
    result[DEST / "expanded" / "manifest.json"] = canonical_bytes(expanded_manifest)

    for surface in SURFACES:
        for name in EXPANDED_FILES:
            src = source / "expanded" / surface / name
            result[DEST / "expanded" / surface / name] = src.read_bytes()

    bindings = build_bindings(validated)
    result[BINDINGS_PATH] = canonical_bytes(bindings)
    result[ADAPTERS_PATH] = canonical_bytes(build_adapters())

    deterministic_source_parts: list[tuple[str, bytes]] = [
        ("registry.json", canonical_bytes(validated["registry"])),
        ("surfaces.json", (source / "surfaces.json").read_bytes()),
        ("routes.json", (source / "routes.json").read_bytes()),
        ("components.json", (source / "components.json").read_bytes()),
        ("editable-slots.json", (source / "editable-slots.json").read_bytes()),
        ("owners.json", (source / "owners.json").read_bytes()),
        ("layers.json", (source / "layers.json").read_bytes()),
        ("risks.json", (source / "risks.json").read_bytes()),
        ("reuse-report.json", (source / "reuse-report.json").read_bytes()),
        ("expanded/manifest.json", canonical_bytes(expanded_manifest)),
    ]
    for surface in SURFACES:
        for name in EXPANDED_FILES:
            rel = f"expanded/{surface}/{name}"
            deterministic_source_parts.append((rel, (source / rel).read_bytes()))

    provenance = {
        "schema": "prisma.ui.visual-control.promotion.v1",
        "status": "SOURCE_STATIC_ONLY",
        "sourceGenerator": "apps/terminal-de-venta-system/tools/quality/ui-visual-control.mjs",
        "sourceScopeMode": "ALL_SURFACES_CANONICAL",
        "surfaceCount": len(SURFACES),
        "surfaces": list(SURFACES),
        "expandedCountsBySurface": validated["verifiedCounts"],
        "sourceAuthorityDigest": sha256_bytes(
            b"".join(
                rel.encode("utf-8") + b"\\0" + data
                for rel, data in sorted(deterministic_source_parts)
            )
        ),
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
        "doesNotProve": [
            "browser-render equivalence",
            "runtime visual certification",
            "GVAE APPLY readiness",
            "semantic recipe coverage",
            "production readiness",
        ],
    }
    result[DEST / "promotion.json"] = canonical_bytes(provenance)
    return result


def write_expected(source: Path) -> dict[str, Any]:
    files = expected_files(source)
    expanded_root = DEST / "expanded"
    if expanded_root.exists():
        shutil.rmtree(expanded_root)
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return summary(files, "WROTE_ALL_SURFACE_VISUAL_AUTHORITY")


def check_expected(source: Path) -> tuple[dict[str, Any], list[str]]:
    files = expected_files(source)
    problems: list[str] = []
    expected_paths = set(files)
    for path, data in files.items():
        if not path.is_file():
            problems.append(f"missing:{path.relative_to(ROOT).as_posix()}")
        elif path.read_bytes() != data:
            problems.append(f"drift:{path.relative_to(ROOT).as_posix()}")

    if (DEST / "expanded").is_dir():
        actual_expanded = {p for p in (DEST / "expanded").rglob("*") if p.is_file()}
        expected_expanded = {p for p in expected_paths if (DEST / "expanded") in p.parents}
        for extra in sorted(actual_expanded - expected_expanded):
            problems.append(f"extra:{extra.relative_to(ROOT).as_posix()}")

    return summary(files, "PASS_ALL_SURFACE_VISUAL_AUTHORITY" if not problems else "FAIL_ALL_SURFACE_VISUAL_AUTHORITY"), problems


def summary(files: dict[Path, bytes], status: str) -> dict[str, Any]:
    return {
        "schema": "prisma.ui.visual-control.promotion-result.v1",
        "status": status,
        "surfaceCount": len(SURFACES),
        "fileCount": len(files),
        "authorityDigest": sha256_bytes(
            b"".join(
                path.relative_to(ROOT).as_posix().encode("utf-8") + b"\0" + data
                for path, data in sorted(files.items(), key=lambda item: item[0].as_posix())
            )
        ),
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--status", action="store_true")
    args = parser.parse_args(argv)
    source = Path(args.source).resolve()

    try:
        if args.write:
            result = write_expected(source)
            print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
            return 0
        if args.check:
            result, problems = check_expected(source)
            result["problems"] = problems
            print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
            return 0 if not problems else 2
        files = expected_files(source)
        print(json.dumps(summary(files, "SOURCE_VALIDATED"), indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except PromotionError as exc:
        print(
            json.dumps(
                {
                    "schema": "prisma.ui.visual-control.promotion-result.v1",
                    "status": "BLOCKED_ALL_SURFACE_VISUAL_AUTHORITY",
                    "errors": [str(exc)],
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
