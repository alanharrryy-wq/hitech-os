#!/usr/bin/env python3
"""Static validator for the canonical RIFAT visual authority."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

PRISMA_HTML_ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_ROOT = PRISMA_HTML_ROOT / "authority" / "rifat"
TABLET_ROOT = AUTHORITY_ROOT / "tablet"
WINDOWS_PATH = re.compile(r"[A-Za-z]:\\\\")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    problems: list[str] = []
    contract = load(TABLET_ROOT / "runtime.contract.json")
    routes = load(TABLET_ROOT / "routes.json")
    sources = load(TABLET_ROOT / "css-source-manifest.json")

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
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
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
    if visual_registry.get("targetSurfaces") != ["tablet"]:
        problems.append("canonical Visual Control must target only the Tablet surface")
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
    if visual_owners.get("status") != "CERTIFIED" or visual_owners.get("routeOwnerCount") != len(route_ids):
        problems.append("canonical Tablet Visual Control route owners are incomplete")

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
                "importantCount": 0 if not any("priority override" in item for item in problems) else None,
                "problems": problems,
            },
            indent=2,
        )
    )
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
