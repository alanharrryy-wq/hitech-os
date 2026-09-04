#!/usr/bin/env python3
"""Static validator for the canonical RIFAT visual authority."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

PRISMA_HTML_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PRISMA_HTML_ROOT.parent
AUTHORITY_ROOT = PRISMA_HTML_ROOT / "authority" / "rifat"
TABLET_ROOT = AUTHORITY_ROOT / "tablet"
VISUAL_SOURCE_MANIFEST = AUTHORITY_ROOT / "visual-source-manifest.json"
WINDOWS_PATH = re.compile(r"[A-Za-z]:\\\\")
GOVERNED_SURFACES = {"chart-lab", "web", "tablet", "pc", "mobile", "control-center", "shared-ui"}
RUNTIME_SURFACES = {"chart-lab", "web", "tablet", "pc", "mobile", "control-center"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL object required: {path}:{number}")
        rows.append(value)
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_visual_source_manifest(problems: list[str]) -> int:
    if not VISUAL_SOURCE_MANIFEST.is_file():
        problems.append("missing canonical visual source manifest")
        return 0

    manifest = load(VISUAL_SOURCE_MANIFEST)
    entries = manifest.get("entries", [])
    if manifest.get("entryCount") != len(entries):
        problems.append("visual source manifest entry count mismatch")
    if manifest.get("projectionCount") != len(entries):
        problems.append("visual source manifest projection count mismatch")
    if manifest.get("surfaceCount") != len({entry.get("surface") for entry in entries}):
        problems.append("visual source manifest surface count mismatch")

    sources: set[str] = set()
    outputs: set[str] = set()
    for entry in entries:
        source_ref = entry.get("source")
        output_ref = entry.get("output")
        if not isinstance(source_ref, str) or not isinstance(output_ref, str):
            problems.append("visual source manifest contains a non-string path")
            continue
        if source_ref in sources:
            problems.append(f"duplicate visual source: {source_ref}")
        if output_ref in outputs:
            problems.append(f"duplicate visual output: {output_ref}")
        sources.add(source_ref)
        outputs.add(output_ref)

        if Path(source_ref).is_absolute() or Path(output_ref).is_absolute():
            problems.append(f"absolute visual projection path forbidden: {source_ref} -> {output_ref}")
            continue
        source_path = REPOSITORY_ROOT / source_ref
        output_path = REPOSITORY_ROOT / output_ref
        if not source_path.is_file():
            problems.append(f"missing canonical visual source: {source_ref}")
            continue
        if not output_path.is_file():
            problems.append(f"missing visual projection output: {output_ref}")
            continue

        source_hash = sha256(source_path)
        output_hash = sha256(output_path)
        if source_hash != entry.get("sourceSha256"):
            problems.append(f"visual source hash mismatch: {source_ref}")
        if output_hash != entry.get("outputSha256"):
            problems.append(f"visual output hash mismatch: {output_ref}")
        if entry.get("projectionMode") == "exact-byte-copy" and source_hash != output_hash:
            problems.append(f"exact-copy visual projection drift: {source_ref} -> {output_ref}")
        if entry.get("generated") is not True or entry.get("manualEditsForbidden") is not True:
            problems.append(f"visual projection safety flags missing: {output_ref}")
        if b"!important" in source_path.read_bytes():
            problems.append(f"priority override forbidden: {source_ref}")

    return len(entries)


def main() -> int:
    problems: list[str] = []
    contract = load(TABLET_ROOT / "runtime.contract.json")
    routes = load(TABLET_ROOT / "routes.json")
    sources = load(TABLET_ROOT / "css-source-manifest.json")
    visual_source_entries = validate_visual_source_manifest(problems)

    if contract.get("authorityRepo") != "hitech-os-prisma-html/prisma-html":
        problems.append("authority repo mismatch")
    if contract.get("atlas", {}).get("importWholeAtlasCss") is not False:
        problems.append("whole atlas.css import must remain forbidden")
    if routes.get("detected") != len(routes.get("routes", [])):
        problems.append("route count mismatch")
    if routes.get("customerVisible") != len([row for row in routes["routes"] if not row.get("internal")]):
        problems.append("customer visible route count mismatch")
    route_ids = [row["route"] for row in routes["routes"]]
    if len(route_ids) != len(set(route_ids)):
        problems.append("duplicate route binding")

    required_states = set(contract["states"])
    route_states = {state for row in routes["routes"] if not row.get("internal") for state in row["states"]}
    missing_states = sorted(required_states - route_states)
    if missing_states:
        problems.append(f"unmapped states: {missing_states}")

    source_paths = [*sources["coreFragments"]]
    source_paths.extend(row["source"] for row in sources["moduleSources"])
    source_paths.extend(row["source"] for row in sources["adapterSources"])
    for relative in source_paths:
        path = AUTHORITY_ROOT / relative
        if not path.exists():
            problems.append(f"missing source: {relative}")
            continue
        data = path.read_bytes()
        if b"!important" in data:
            problems.append(f"priority override forbidden: {relative}")
        if WINDOWS_PATH.search(data.decode("utf-8", errors="ignore")):
            problems.append(f"local path forbidden: {relative}")

    atlas = contract["atlas"]
    for path_key, hash_key in (("tokens", "tokensSha256"), ("css", "cssSha256")):
        path = PRISMA_HTML_ROOT / atlas[path_key]
        actual = sha256(path)
        if actual != atlas[hash_key]:
            problems.append(f"Atlas hash mismatch: {atlas[path_key]}")

    prisma_ui = AUTHORITY_ROOT / "prisma-ui"
    for relative in ("registry.json", "surfaces.json", "routes.json", "panels", "visual-control"):
        if not (prisma_ui / relative).exists():
            problems.append(f"missing canonical prisma-ui source: {relative}")
    canonical_routes = load(prisma_ui / "routes.json")
    canonical_tablet_routes = [
        row["route"] for row in canonical_routes.get("routes", []) if row.get("surface") == "tablet"
    ]
    if canonical_tablet_routes != route_ids:
        problems.append("canonical prisma-ui Tablet routes do not match RIFAT route bindings")
    canonical_surface = next(
        (row for row in load(prisma_ui / "surfaces.json").get("surfaces", []) if row.get("id") == "tablet"),
        None,
    )
    if not canonical_surface or canonical_surface.get("routes") != route_ids:
        problems.append("canonical prisma-ui Tablet surface routes do not match RIFAT route bindings")
    visual_routes = load(prisma_ui / "visual-control" / "routes.json")
    visual_tablet_routes = [
        row["route"] for row in visual_routes.get("routes", []) if row.get("surface") == "tablet"
    ]
    if visual_tablet_routes != route_ids:
        problems.append("canonical Visual Control Tablet routes do not match RIFAT route bindings")
    visual_registry = load(prisma_ui / "visual-control" / "registry.json")
    if visual_registry.get("status") != "CERTIFIED":
        problems.append("canonical Visual Control registry is not CERTIFIED")
    if visual_registry.get("scopeMode") != "ALL_SURFACES_CANONICAL" or visual_registry.get("canonicalGlobal") is not True:
        problems.append("canonical Visual Control is not the all-surface promoted authority")
    if set(visual_registry.get("targetSurfaces") or []) != GOVERNED_SURFACES:
        problems.append("canonical Visual Control governed surface set is incomplete")
    if set(visual_registry.get("runtimeTargetSurfaces") or []) != RUNTIME_SURFACES:
        problems.append("canonical Visual Control runtime surface set is incomplete")
    if visual_registry.get("sourceSurface") is not None:
        problems.append("canonical Visual Control must not be surface-scoped")
    visual_risks = load(prisma_ui / "visual-control" / "risks.json")
    required_zero_risks = (
        "blockerCount",
        "warningCount",
        "routeOwnerMissingCount",
        "regionOwnerMissingCount",
        "slotUnclassifiedCount",
        "activeImportantCount",
        "ambiguousActiveLayerOwnerCount",
    )
    if visual_risks.get("status") != "CERTIFIED" or any(
        visual_risks.get(key) != 0 for key in required_zero_risks
    ):
        problems.append("canonical Tablet Visual Control risks are not zero-certified")
    visual_owners = load(prisma_ui / "visual-control" / "owners.json")
    if visual_owners.get("status") != "CERTIFIED":
        problems.append("canonical Visual Control owners are not CERTIFIED")
    if visual_owners.get("routeOwnerCount") != len(visual_routes.get("routes", [])):
        problems.append("canonical Visual Control global route owner count is incomplete")

    tablet_route_owner_path = prisma_ui / "visual-control" / "expanded" / "tablet" / "owners-routeOwners.jsonl"
    if not tablet_route_owner_path.is_file():
        problems.append("canonical Tablet Visual Control route-owner shard is missing")
    else:
        tablet_route_owners = load_jsonl(tablet_route_owner_path)
        tablet_owner_routes = [row.get("route") for row in tablet_route_owners]
        if len(tablet_route_owners) != len(route_ids) or tablet_owner_routes != route_ids:
            problems.append("canonical Tablet Visual Control route owners are incomplete")
        if any(row.get("surface") != "tablet" for row in tablet_route_owners):
            problems.append("canonical Tablet Visual Control route-owner shard contains foreign surfaces")

    expanded_manifest = load(prisma_ui / "visual-control" / "expanded" / "manifest.json")
    if expanded_manifest.get("status") != "CERTIFIED":
        problems.append("canonical Visual Control expanded authority is not CERTIFIED")
    if expanded_manifest.get("scopeMode") != "ALL_SURFACES_CANONICAL" or expanded_manifest.get("canonicalGlobal") is not True:
        problems.append("canonical Visual Control expanded authority is not all-surface canonical")
    if set(expanded_manifest.get("surfaces") or []) != GOVERNED_SURFACES:
        problems.append("canonical Visual Control expanded surface set is incomplete")
    expanded_counts = expanded_manifest.get("countsBySurface") if isinstance(expanded_manifest.get("countsBySurface"), dict) else {}
    tablet_counts = expanded_counts.get("tablet") if isinstance(expanded_counts.get("tablet"), dict) else {}
    if tablet_counts.get("routeOwners") != len(route_ids):
        problems.append("canonical Tablet expanded route-owner count does not match RIFAT routes")

    governance = AUTHORITY_ROOT / "governance" / "current"
    required_governance = (
        "AUTHORITY_READSET.lock.json",
        "APP_IMPACT_MATRIX.md",
        "CONTRACT_AND_GATE_MATRIX.json",
        "MISSING_OR_UNMAPPED_RISK.md",
        "AGENT_PROMPT_ENVELOPE.md",
        "AUTHORITY_MESH_REPORT.md",
        "LAYERS_MAP.md",
        "LAYERS_MAP.json",
    )
    for relative in required_governance:
        if not (governance / relative).exists():
            problems.append(f"missing RIFAT governance output: {relative}")

    status = "PASS" if not problems else "FAIL"
    print(
        json.dumps(
            {
                "status": status,
                "authority": "prisma-html/authority/rifat",
                "routes": len(routes["routes"]),
                "customerVisibleRoutes": routes["customerVisible"],
                "canonicalCssSources": len(sources["coreFragments"]) + len(sources["moduleSources"]),
                "adapterSources": len(sources["adapterSources"]),
                "visualSourceEntries": visual_source_entries,
                "importantCount": 0 if not any("priority override" in item for item in problems) else None,
                "problems": problems,
            },
            indent=2,
        )
    )
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
