#!/usr/bin/env python3
"""PRISMA VISCORE1: one visual authority, one readiness view, zero fake READY.

This is a read-mostly orchestration layer over the existing Identity Dictionary,
RIFAT/prisma-ui binding authority, projection manifest and Atlasfin cockpit.
It does not mutate product runtime and it does not certify browser visuals.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from identity_dictionary_core import COMPILED, IDENTITY, ROOT, SURFACES, build_compilation, load_model, validate_model
from visual_application.target_index import build_index as build_application_target_index

PRISMA_UI = ROOT / "authority" / "rifat" / "prisma-ui"
VISUAL_SOURCE_MANIFEST = ROOT / "authority" / "rifat" / "visual-source-manifest.json"
VISUAL_AUTHORITY_REGISTRY = IDENTITY / "registries" / "visual-authority.registry.json"
ATLAS_ROOT = ROOT / "extras" / "atlasfin"
ATLAS_MANIFEST = ATLAS_ROOT / "assets" / "data" / "atlas.manifest.json"
DEFAULT_REPORT_DIR = ROOT / "reports" / "visual-core"
ATLAS_STATUS_JSON = ATLAS_ROOT / "assets" / "data" / "visual-core.status.json"
ATLAS_STATUS_JS = ATLAS_ROOT / "assets" / "data" / "visual-core.status.js"

APP_SURFACES = ("tablet", "pc", "mobile", "web", "chart-lab", "control-center")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def route_counts(routes: dict[str, Any]) -> Counter[str]:
    return Counter(
        str(row.get("surface"))
        for row in routes.get("routes", [])
        if row.get("surface")
    )


def projection_counts(manifest: dict[str, Any]) -> Counter[str]:
    return Counter(
        str(row.get("surface"))
        for row in manifest.get("entries", [])
        if row.get("surface")
    )


def expected_compiled() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    files = build_compilation()
    manifest = json.loads(files["manifest.json"].decode("utf-8"))
    projections = {
        surface: json.loads(files[f"projections/{surface}.identity-projection.json"].decode("utf-8"))
        for surface in SURFACES
    }
    return manifest, projections


def detailed_binding_sources(binding: dict[str, Any]) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for key in ("routeSource", "ownerSource", "slotSource", "layerSource"):
        value = binding.get(key)
        out[key] = bool(value and (ROOT / str(value)).is_file())
    return out


def surface_status(
    surface: str,
    binding: dict[str, Any],
    routes_by_surface: Counter[str],
    projection_by_surface: Counter[str],
    expected_projection: dict[str, Any],
    identity_problems: list[str],
) -> dict[str, Any]:
    declared_routes = binding.get("routeCount")
    current_routes = routes_by_surface.get(surface, 0)
    count_is_applicable = surface in APP_SURFACES
    route_count_drift = bool(
        count_is_applicable
        and isinstance(declared_routes, int)
        and declared_routes != current_routes
    )
    sources = detailed_binding_sources(binding)
    binding_readiness = str(binding.get("readiness", "UNKNOWN"))
    blockers: list[str] = []

    if route_count_drift:
        blockers.append(f"route-count-drift:{declared_routes}->{current_routes}")
    blockers.extend(str(item) for item in binding.get("missing", []))

    if surface in APP_SURFACES and binding_readiness == "CERTIFIED_BINDING_SOURCE":
        for key in ("routeSource", "ownerSource", "slotSource", "layerSource"):
            if not sources.get(key):
                blockers.append(f"missing-binding-source:{key}")

    compiled_status = str(expected_projection.get("status", "UNKNOWN"))
    runtime_allowed = bool(expected_projection.get("runtimeProjectionAllowed"))

    if surface == "shared-ui":
        stage = "NEUTRAL_SOURCE_READY"
    elif route_count_drift:
        stage = "DRIFT_BLOCKED"
    elif binding_readiness != "CERTIFIED_BINDING_SOURCE":
        stage = "BLOCKED_BINDINGS"
    elif compiled_status != "BINDING_READY_SOURCE_ONLY":
        stage = "BLOCKED_COMPILE"
        blockers.append(f"compiled-status:{compiled_status}")
    elif identity_problems:
        stage = "BLOCKED_IDENTITY_GATE"
        blockers.append("identity-validator-failed")
    elif not runtime_allowed:
        stage = "BINDING_READY_SOURCE_ONLY"
        blockers.append("runtime-projection-not-authorized")
    else:
        stage = "READY_FOR_RUNTIME_CERTIFICATION"
        blockers.append("runtime-visual-evidence-required")

    return {
        "surface": surface,
        "stage": stage,
        "ready": stage == "READY",
        "bindingReadiness": binding_readiness,
        "declaredRouteCount": declared_routes,
        "effectiveRouteCount": current_routes if count_is_applicable else declared_routes,
        "routeCountDrift": route_count_drift,
        "bindingSources": sources,
        "compiledStatus": compiled_status,
        "runtimeProjectionAllowed": runtime_allowed,
        "projectionManifestEntries": projection_by_surface.get(surface, 0),
        "blockers": sorted(set(blockers)),
    }


def build_status() -> dict[str, Any]:
    problems, warnings = validate_model(check_compiled=True)
    model = load_model()
    routes = load_json(PRISMA_UI / "routes.json")
    visual_manifest = load_json(VISUAL_SOURCE_MANIFEST)
    atlas_manifest = load_json(ATLAS_MANIFEST)
    authority_registry = load_json(VISUAL_AUTHORITY_REGISTRY)
    compiled_manifest, expected_projections = expected_compiled()
    by_route_surface = route_counts(routes)
    by_projection_surface = projection_counts(visual_manifest)
    application_index = build_application_target_index(ROOT)

    surfaces = [
        surface_status(
            surface,
            model["bindings"][surface],
            by_route_surface,
            by_projection_surface,
            expected_projections[surface],
            problems,
        )
        for surface in SURFACES
    ]

    metadata_drift = [
        {
            "surface": row["surface"],
            "kind": "binding-route-count",
            "declared": row["declaredRouteCount"],
            "effective": row["effectiveRouteCount"],
        }
        for row in surfaces if row["routeCountDrift"]
    ]

    architecture_problems: list[str] = []
    if authority_registry.get("editableAuthorityCount") != 1:
        architecture_problems.append("editable-authority-count-must-equal-one")
    if authority_registry.get("cockpit", {}).get("path") != "extras/atlasfin/index.html":
        architecture_problems.append("atlasfin-must-be-canonical-cockpit")
    if visual_manifest.get("entryCount") != len(visual_manifest.get("entries", [])):
        architecture_problems.append("visual-source-manifest-entry-count-drift")
    if visual_manifest.get("projectionCount") != len(visual_manifest.get("entries", [])):
        architecture_problems.append("visual-source-manifest-projection-count-drift")
    if visual_manifest.get("surfaceCount") != len(by_projection_surface):
        architecture_problems.append("visual-source-manifest-surface-count-drift")
    architecture_problems.extend(
        f"application-target-index:{item}" for item in application_index.get("globalBlockers", [])
    )

    atlas_sections = atlas_manifest.get("sections", [])
    atlas_items = atlas_manifest.get("items", [])
    atlas_status = {
        "path": "extras/atlasfin/index.html",
        "manifestStatus": atlas_manifest.get("status"),
        "pages": 1 + len(atlas_sections),
        "sections": len(atlas_sections),
        "elements": atlas_manifest.get("total_items", len(atlas_items)),
        "role": "canonical-human-cockpit",
        "authority": False,
    }

    overall = "PASS"
    if architecture_problems or problems:
        overall = "FAIL_ARCHITECTURE"
    elif metadata_drift:
        overall = "PASS_WITH_METADATA_DRIFT"
    elif any(row["stage"].startswith("BLOCKED") or row["stage"] == "DRIFT_BLOCKED" for row in surfaces):
        overall = "SOURCE_READY_WITH_BLOCKED_SURFACES"

    return {
        "schema": "prisma.visual.core.status.v1",
        "version": "1.0.0",
        "status": overall,
        "hardTruth": "Compiled or source-ready authority is not runtime visual certification.",
        "authority": {
            "editableAuthorityCount": authority_registry.get("editableAuthorityCount"),
            "editableAuthority": authority_registry.get("editableAuthority"),
            "bindingAuthority": authority_registry.get("bindingAuthority"),
            "cockpit": authority_registry.get("cockpit"),
            "derivedViews": authority_registry.get("derivedViews", []),
        },
        "identity": {
            "selectedProfileId": model["activation"]["selectedProfileId"],
            "compiledStatus": compiled_manifest.get("status"),
            "validatorProblems": problems,
            "validatorWarnings": warnings,
        },
        "atlasfin": atlas_status,
        "projectionManifest": {
            "path": "authority/rifat/visual-source-manifest.json",
            "surfaceCount": visual_manifest.get("surfaceCount"),
            "entryCount": visual_manifest.get("entryCount"),
            "manualEditsForbiddenCount": sum(
                row.get("manualEditsForbidden") is True
                for row in visual_manifest.get("entries", [])
            ),
            "countsBySurface": dict(sorted(by_projection_surface.items())),
        },
        "applicationEngine": {
            "schema": "prisma.visual.application.engine-readiness.v1",
            "status": "SOURCE_STATIC_ONLY" if not application_index.get("globalBlockers") else "BLOCKED_STATIC",
            "targetIndex": "authority/rifat/prisma-ui/visual-control/target-index/manifest.json",
            "indexDigest": application_index.get("indexDigest"),
            "recordCount": application_index.get("recordCount", 0),
            "countsByStatus": application_index.get("countsByStatus", {}),
            "supportedProjectionModes": application_index.get("supportedProjectionModes", []),
            "globalBlockers": application_index.get("globalBlockers", []),
            "evidenceClassification": "SOURCE_STATIC_ONLY",
            "runtimeVisualGreen": False,
            "ready": False,
            "doesNotProve": ["browser-rendering", "runtime-visual-green", "production-readiness", "all-surfaces-application", "broader-mutation-authorization"],
        },
        "surfaces": surfaces,
        "metadataDrift": metadata_drift,
        "architectureProblems": architecture_problems,
        "readyPolicy": {
            "stages": [
                "DISCOVERED",
                "BOUND",
                "COMPILED",
                "PROJECTED",
                "STATIC_GREEN",
                "RUNTIME_VISUAL_GREEN",
                "READY",
            ],
            "currentRule": "No surface is READY until runtime visual evidence is explicitly certified.",
        },
    }


def render_markdown(status: dict[str, Any]) -> str:
    lines = [
        "# PRISMA Visual Core Status",
        "",
        f"- Status: `{status['status']}`",
        f"- Editable visual authorities: `{status['authority']['editableAuthorityCount']}`",
        f"- Identity profile: `{status['identity']['selectedProfileId']}`",
        f"- Projection entries: `{status['projectionManifest']['entryCount']}`",
        f"- GVAE Target Index: `{status['applicationEngine']['status']}` / `{status['applicationEngine']['recordCount']}` records",
        f"- Atlasfin: `{status['atlasfin']['pages']} pages / {status['atlasfin']['sections']} sections / {status['atlasfin']['elements']} elements`",
        "",
        "| Surface | Stage | Routes effective | Declared | Projection entries | Runtime allowed | Blockers |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in status["surfaces"]:
        blockers = ", ".join(row["blockers"]) or "—"
        lines.append(
            f"| {row['surface']} | {row['stage']} | {row['effectiveRouteCount']} | "
            f"{row['declaredRouteCount']} | {row['projectionManifestEntries']} | "
            f"{'yes' if row['runtimeProjectionAllowed'] else 'no'} | {blockers} |"
        )
    if status["metadataDrift"]:
        lines += ["", "## Metadata drift", ""]
        for row in status["metadataDrift"]:
            lines.append(
                f"- `{row['surface']}` {row['kind']}: declared={row['declared']} effective={row['effective']}"
            )
    if status["architectureProblems"]:
        lines += ["", "## Architecture problems", ""]
        lines.extend(f"- {item}" for item in status["architectureProblems"])
    if status["identity"]["validatorProblems"]:
        lines += ["", "## Identity gate problems", ""]
        lines.extend(f"- {item}" for item in status["identity"]["validatorProblems"])
    lines += [
        "",
        "## Final architecture",
        "",
        "`neutral meaning -> identity profile -> surface adapter -> certified binding -> compiled projection -> governed runtime -> visual evidence -> READY`",
        "",
        "Atlasfin is the human cockpit. Identity Dictionary is the editable visual authority. RIFAT/prisma-ui owns location/bindings. Product files are generated projections where declared by the projection manifest.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(status: dict[str, Any], outdir: Path, atlas_export: bool) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / "VISUAL_CORE_STATUS.json"
    md_path = outdir / "VISUAL_CORE_STATUS.md"
    json_text = json.dumps(status, indent=2, ensure_ascii=False) + "\n"
    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(render_markdown(status), encoding="utf-8")
    outputs = [json_path, md_path]
    if atlas_export:
        ATLAS_STATUS_JSON.write_text(json_text, encoding="utf-8")
        ATLAS_STATUS_JS.write_text(
            "window.PRISMA_VISUAL_CORE_STATUS = "
            + json.dumps(status, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + ";\n",
            encoding="utf-8",
        )
        outputs.extend([ATLAS_STATUS_JSON, ATLAS_STATUS_JS])
    return outputs


def print_summary(status: dict[str, Any]) -> None:
    print(f"PRISMA VISUAL CORE: {status['status']}")
    print("surface         stage                              blockers")
    print("--------------  ---------------------------------  ----------------------------------------")
    for row in status["surfaces"]:
        blockers = ", ".join(row["blockers"][:3]) or "—"
        print(f"{row['surface']:<14}  {row['stage']:<33}  {blockers}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PRISMA VISCORE1")
    sub = parser.add_subparsers(dest="command", required=True)
    status_parser = sub.add_parser("status")
    status_parser.add_argument("--json", action="store_true")
    sub.add_parser("check")
    ready = sub.add_parser("ready")
    ready.add_argument("surface", choices=SURFACES)
    write = sub.add_parser("write")
    write.add_argument("--out", default=str(DEFAULT_REPORT_DIR.relative_to(ROOT)))
    write.add_argument("--atlas-export", action="store_true")
    sub.add_parser("tree")
    args = parser.parse_args(argv)

    status = build_status()
    if args.command == "status":
        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print_summary(status)
        return 0
    if args.command == "check":
        print_summary(status)
        hard_fail = bool(status["architectureProblems"] or status["identity"]["validatorProblems"])
        return 1 if hard_fail else 0
    if args.command == "ready":
        row = next(item for item in status["surfaces"] if item["surface"] == args.surface)
        print(json.dumps(row, indent=2, ensure_ascii=False))
        return 0 if row["ready"] else 2
    if args.command == "write":
        outdir = Path(args.out)
        if not outdir.is_absolute():
            outdir = ROOT / outdir
        outputs = write_outputs(status, outdir, args.atlas_export)
        rendered = []
        for path in outputs:
            try:
                rendered.append(path.relative_to(ROOT).as_posix())
            except ValueError:
                rendered.append(str(path))
        print(json.dumps({"status": status["status"], "outputs": rendered}, indent=2))
        return 0
    if args.command == "tree":
        print(
            "PRISMA VISUAL AUTHORITY\n"
            "  authority/rifat/identity        editable semantic authority\n"
            "    -> profiles/tokens/recipes\n"
            "    -> surface adapters\n"
            "  authority/rifat/prisma-ui       route/owner/slot/layer binding authority\n"
            "    -> compiled identity projections\n"
            "    -> visual-source-manifest     deterministic product projections\n"
            "  extras/atlasfin                 canonical human cockpit\n"
            "  apps/product runtimes           consumers, never competing authority\n"
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
