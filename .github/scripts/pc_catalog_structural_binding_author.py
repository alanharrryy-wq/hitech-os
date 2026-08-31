#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APP = REPO / "apps/terminal-de-venta-system"
PRISMA_HTML = REPO / "prisma-html"
RIFAT = PRISMA_HTML / "authority/rifat"

LAYER_ID = "LYR.VIS.SURFACE.CONTENT.PRIMARY.PC.CATALOG.WORKSPACE.BASE"
REGION_ID = LAYER_ID + ".layer"
SLOT_ID = "pc.catalog.lyr.vis.surface.content.primary.pc.catalog.workspace.base.layer"
COMPONENT_ID = "products.pc.app.components.catalog.product.media.workspace.tsx"
CSS_ID = "products.pc.app.components.catalog.product.media.workspace.module.css"
IMPLEMENTATION_LAYER_ID = "products.pc.app.components.catalog.product.media.workspace.module.css.workspace"
COMPONENT_PATH = "products/pc/app/components/catalog/product-media-workspace.tsx"
CSS_PATH = "products/pc/app/components/catalog/product-media-workspace.module.css"


def run(args: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd or REPO, check=True)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_visual_control() -> None:
    path = APP / "tools/quality/ui-visual-control.mjs"
    text = path.read_text(encoding="utf-8")
    old_sig = "function buildVisualRegions(routes, panels, layers, components = []) {"
    new_sig = "function buildVisualRegions(routes, panels, layers, components = [], certifiedLayers = []) {"
    if old_sig in text:
        text = text.replace(old_sig, new_sig, 1)
    elif new_sig not in text:
        raise SystemExit("BUILD_VISUAL_REGIONS_SIGNATURE_ANCHOR_MISSING")

    component_anchor = "  for (const component of components.filter((item) => item.hasButton)) {"
    structural_block = """  const materialLayerIds = new Set(
    layers
      .filter((item) => item.background || item.backdropFilter || item.zIndex)
      .map((item) => item.layer_id)
  );
  for (const layer of certifiedLayers.filter((item) => !materialLayerIds.has(item.implementationLayerId))) {
    const routeOwner = routes.find((item) => item.route_id === layer.routeId) || null;
    regions.push({
      region_id: `${layer.layer_id}.layer`,
      surface: layer.surface,
      route: routeOwner?.route || null,
      human_id: `${layer.neutralMeaningId} certified structural layer`,
      visualRegion: layer.visualRegion,
      ownerComponent: layer.ownerComponent || null,
      ownerCss: [layer.ownerCss].filter(Boolean),
      assetOwner: [],
      tokenOwner: tokenOwners(),
      safetyClassification: layer.safetyClassification,
      excludedSurfaces: excludedSurfaces(layer.surface),
      layerOwner: layer.layer_id,
      implementationLayerId: layer.implementationLayerId,
      certificationStatus: layer.certificationStatus
    });
  }
"""
    if structural_block not in text:
        if component_anchor not in text:
            raise SystemExit("STRUCTURAL_LAYER_INSERT_ANCHOR_MISSING")
        text = text.replace(component_anchor, structural_block + component_anchor, 1)

    old_call = "const regions = buildVisualRegions(routes, panels, layerPayload.layers, components);"
    new_call = "const regions = buildVisualRegions(routes, panels, layerPayload.layers, components, layerPayload.certifiedLayers);"
    if old_call in text:
        text = text.replace(old_call, new_call, 1)
    elif new_call not in text:
        raise SystemExit("BUILD_VISUAL_REGIONS_CALL_ANCHOR_MISSING")
    path.write_text(text, encoding="utf-8")


def patch_layer_certification() -> None:
    path = APP / "config/prisma-visual/identity-layer-certifications.registry.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    certification = {
        "layerId": LAYER_ID,
        "neutralMeaningId": "VIS.SURFACE.CONTENT.PRIMARY",
        "surface": "pc",
        "file": CSS_PATH,
        "selector": ".workspace",
        "ownerComponent": COMPONENT_PATH,
        "routeId": "pc.catalog.route",
        "regionId": REGION_ID,
        "slotId": SLOT_ID,
        "expectedImplementationLayerId": IMPLEMENTATION_LAYER_ID,
        "safetyClassification": "safeVisualOnly",
        "certificationPolicy": "EXACTLY_ONE_IMPLEMENTATION_MATCH_REQUIRED",
    }
    data["certifications"] = [x for x in data.get("certifications", []) if x.get("layerId") != LAYER_ID] + [certification]
    data["version"] = "1.1.0"
    write_json(path, data)


def load_vc(vc: Path, name: str) -> dict:
    return json.loads((vc / name).read_text(encoding="utf-8"))


def prove_and_promote(vc: Path) -> None:
    routes = load_vc(vc, "routes.json")
    owners = load_vc(vc, "owners.json")
    components = load_vc(vc, "components.json")
    slots = load_vc(vc, "editable-slots.json")
    layers = load_vc(vc, "layers.json")
    risks = load_vc(vc, "risks.json")

    assert risks.get("status") == "CERTIFIED", risks
    assert risks.get("blockerCount") == 0, risks
    assert risks.get("warningCount") == 0, risks
    assert risks.get("activeImportantCount") == 0, risks

    route = next((x for x in routes.get("routes", []) if x.get("route_id") == "pc.catalog.route"), None)
    component = next((x for x in components.get("components", []) if x.get("component_id") == COMPONENT_ID), None)
    css_owner = next((x for x in owners.get("cssOwnerSamples", []) if x.get("owner_id") == CSS_ID), None)
    region = next((x for x in owners.get("regionOwnerSamples", []) if x.get("region_id") == REGION_ID), None)
    slot = next((x for x in slots.get("slotUnitSamples", []) if x.get("slot_unit_id") == SLOT_ID), None)
    certified = next((x for x in layers.get("certifiedLayers", []) if x.get("layer_id") == LAYER_ID), None)
    implementation = next((x for x in layers.get("layerSamples", []) if x.get("layer_id") == IMPLEMENTATION_LAYER_ID), None)

    assert route and route.get("route") == "/catalog", route
    assert component and component.get("path") == COMPONENT_PATH, component
    assert css_owner and css_owner.get("file") == CSS_PATH, css_owner
    assert region and region.get("route") == "/catalog", region
    assert region.get("ownerComponent") == COMPONENT_PATH, region
    assert slot and slot.get("route") == "/catalog" and slot.get("target") == REGION_ID, slot
    assert certified and certified.get("implementationLayerId") == IMPLEMENTATION_LAYER_ID, certified
    assert certified.get("selector") == ".workspace", certified
    assert implementation and implementation.get("selector") == ".workspace", implementation

    pc_dst = RIFAT / "prisma-ui/visual-control/pc"
    pc_dst.mkdir(parents=True, exist_ok=True)
    for name in ["registry.json", "surfaces.json", "routes.json", "components.json", "editable-slots.json", "owners.json", "layers.json", "risks.json"]:
        shutil.copy2(vc / name, pc_dst / name)

    path = RIFAT / "identity/registries/bindings.registry.json"
    bindings = json.loads(path.read_text(encoding="utf-8"))
    pc = next(x for x in bindings["bindings"] if x.get("surface") == "pc")
    pc.update(
        {
            "readiness": "ROUTE_SCOPED_BINDING_SOURCE_READY",
            "sourceEvidenceReadiness": "CERTIFIED_SOURCE_AVAILABLE",
            "routeSource": "authority/rifat/prisma-ui/visual-control/pc/routes.json",
            "ownerSource": "authority/rifat/prisma-ui/visual-control/pc/owners.json",
            "componentSource": "authority/rifat/prisma-ui/visual-control/pc/components.json",
            "slotSource": "authority/rifat/prisma-ui/visual-control/pc/editable-slots.json",
            "layerSource": "authority/rifat/prisma-ui/visual-control/pc/layers.json",
            "routeCount": routes.get("routeCount"),
            "routeOwnerCount": owners.get("routeOwnerCount"),
            "regionOwnerCount": owners.get("regionOwnerCount"),
            "editableSlotCount": slots.get("editableSlotCount"),
            "slotUnitCount": slots.get("slotUnitCount"),
            "layerCount": layers.get("layerCount"),
            "componentCount": components.get("componentCount"),
            "certifiedLayerCount": layers.get("certifiedLayerCount"),
            "missing": ["surface-wide-binding-coverage"],
            "runtimeProjectionAllowed": False,
            "sourceCertification": {
                "status": "CERTIFIED",
                "surface": "pc",
                "scope": "route-scoped-authority-enabled; surface-wide coverage remains incomplete",
                "generator": "apps/terminal-de-venta-system/tools/quality/ui-visual-control.mjs",
                "auditRunId": 33371314103,
                "authorityMeshRunId": 33370426993,
                "productMutationAllowed": False,
            },
        }
    )
    bindings["version"] = "1.1.0"
    write_json(path, bindings)


def patch_resolver() -> None:
    path = PRISMA_HTML / "tools/identity_binding_resolver_core.py"
    core = path.read_text(encoding="utf-8")
    needle = 'REGISTRY_PATH = IDENTITY / "registries" / "element-bindings.registry.json"\n'
    if "BINDINGS_REGISTRY_PATH" not in core:
        if needle not in core:
            raise SystemExit("RESOLVER_REGISTRY_ANCHOR_NOT_FOUND")
        core = core.replace(needle, needle + 'BINDINGS_REGISTRY_PATH = IDENTITY / "registries" / "bindings.registry.json"\n', 1)

    start_marker = "def authority_indexes() -> dict[str, Any]:\n"
    end_marker = "\n\ndef selector_from_artifact"
    if start_marker not in core or end_marker not in core:
        raise SystemExit("RESOLVER_AUTHORITY_INDEX_BLOCK_NOT_FOUND")
    start = core.index(start_marker)
    end = core.index(end_marker, start)
    replacement = '''def authority_indexes() -> dict[str, Any]:
    """Load binding authority only from per-surface sources declared by bindings.registry.json."""
    source_registry = load_json(BINDINGS_REGISTRY_PATH)
    indexes: dict[str, dict[str, Any]] = {
        "routes": {},
        "componentOwners": {},
        "cssOwners": {},
        "regionOwners": {},
        "components": {},
        "slots": {},
        "layers": {},
    }
    loaded: dict[str, dict[str, Any]] = {}

    def doc(rel_path: str | None) -> dict[str, Any] | None:
        if not rel_path:
            return None
        if rel_path not in loaded:
            candidate = ROOT / rel_path
            if not candidate.is_file():
                raise FileNotFoundError(f"declared binding authority source is missing: {rel_path}")
            loaded[rel_path] = load_json(candidate)
        return loaded[rel_path]

    def same_surface(item: dict[str, Any], surface: str) -> bool:
        return item.get("surface") in {None, surface}

    for binding_source in source_registry.get("bindings", []):
        surface = str(binding_source.get("surface") or "")
        routes_doc = doc(binding_source.get("routeSource"))
        if routes_doc:
            for item in routes_doc.get("routes", []):
                if same_surface(item, surface):
                    indexes["routes"][item["route_id"]] = item

        owners_doc = doc(binding_source.get("ownerSource"))
        components_doc = doc(binding_source.get("componentSource"))
        if components_doc is None and binding_source.get("ownerSource"):
            parent = str(Path(binding_source["ownerSource"]).parent)
            candidate = f"{parent}/components.json"
            if (ROOT / candidate).is_file():
                components_doc = doc(candidate)

        if components_doc:
            for item in components_doc.get("components", []):
                if same_surface(item, surface):
                    indexes["components"][item["component_id"]] = item
                    indexes["componentOwners"].setdefault(item["component_id"], item)

        if owners_doc:
            for item in owners_doc.get("componentOwnerSamples", []):
                if same_surface(item, surface):
                    indexes["componentOwners"][item["component_id"]] = item
            for item in owners_doc.get("cssOwnerSamples", []):
                if same_surface(item, surface):
                    indexes["cssOwners"][item["owner_id"]] = item
            for item in owners_doc.get("regionOwnerSamples", []):
                if same_surface(item, surface):
                    indexes["regionOwners"][item["region_id"]] = item

        slots_doc = doc(binding_source.get("slotSource"))
        if slots_doc:
            for item in slots_doc.get("slotUnitSamples", []):
                if same_surface(item, surface):
                    indexes["slots"][item["slot_unit_id"]] = item

        layers_doc = doc(binding_source.get("layerSource"))
        if layers_doc:
            for item in [*layers_doc.get("layerSamples", []), *layers_doc.get("certifiedLayers", [])]:
                if same_surface(item, surface):
                    indexes["layers"][item["layer_id"]] = item

    return indexes
'''
    path.write_text(core[:start] + replacement + core[end:], encoding="utf-8")


def patch_element_registry() -> None:
    path = RIFAT / "identity/registries/element-bindings.registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    binding_id = "BND.VIS.SURFACE.CONTENT.PRIMARY.PC.CATALOG.WORKSPACE.V1"
    binding = {
        "bindingId": binding_id,
        "selector": {
            "neutralMeaningId": "VIS.SURFACE.CONTENT.PRIMARY",
            "identityProfileId": "*",
            "recipePresetId": "*",
            "objectId": "PC-HOME-FORM-COMPONENTS-CATALOG-PRODUCT-MEDIA-WORKSPACE-WORKSPACE-FRM-01",
            "surfaceId": "pc",
        },
        "cardinality": "ONE_TO_ONE_CANDIDATE",
        "status": "RESOLVED",
        "reason": "Fresh PC-only Visual Control and the certified structural-layer registry prove one exact /catalog .workspace coordinate. Visual recipe values remain gated to the later APPLY Mesh.",
        "targets": [
            {
                "targetId": "TGT.PC.CATALOG.WORKSPACE.CONTENT.PRIMARY.V1",
                "ownerId": COMPONENT_ID,
                "routeId": "pc.catalog.route",
                "regionId": REGION_ID,
                "slotId": SLOT_ID,
                "componentUiId": COMPONENT_ID,
                "layerId": LAYER_ID,
                "ownerCssId": CSS_ID,
                "selector": ".workspace",
                "missingBindings": [],
                "status": "RESOLVED",
                "safetyClassification": "safeVisualOnly",
                "evidence": {
                    "routeSource": "authority/rifat/prisma-ui/visual-control/pc/routes.json",
                    "ownerSource": "authority/rifat/prisma-ui/visual-control/pc/owners.json",
                    "componentSource": "authority/rifat/prisma-ui/visual-control/pc/components.json",
                    "slotSource": "authority/rifat/prisma-ui/visual-control/pc/editable-slots.json",
                    "layerSource": "authority/rifat/prisma-ui/visual-control/pc/layers.json",
                    "sourceComponentPath": COMPONENT_PATH,
                    "sourceCssPath": CSS_PATH,
                    "layerLookupResult": "CERTIFIED_EXACT_LAYER_RECORD",
                    "layerCertificationRegistry": "apps/terminal-de-venta-system/config/prisma-visual/identity-layer-certifications.registry.json",
                    "layerGenerator": "apps/terminal-de-venta-system/tools/quality/ui-visual-control.mjs",
                    "surfaceAdapterId": "prisma.adapter.pc.v1",
                    "authorityMeshRunId": 33370426993,
                    "visualControlAuditRunId": 33371314103,
                    "recipeStatus": "APPLY_STAGE_CANONICAL_RECIPE_PENDING",
                },
                "implementationLayerId": IMPLEMENTATION_LAYER_ID,
            }
        ],
    }
    registry["bindings"] = [x for x in registry.get("bindings", []) if x.get("bindingId") != binding_id] + [binding]
    registry["scope"] = sorted(set(registry.get("scope", []) + ["pc"]))
    registry["version"] = "1.2.0"
    registry["status"] = "SOURCE_READY_ROUTE_SCOPED_PC_CATALOG_BINDING_RESOLVED"
    snapshot = registry["authoritySnapshot"]
    wanted = [
        "authority/rifat/prisma-ui/visual-control/pc/routes.json",
        "authority/rifat/prisma-ui/visual-control/pc/owners.json",
        "authority/rifat/prisma-ui/visual-control/pc/components.json",
        "authority/rifat/prisma-ui/visual-control/pc/editable-slots.json",
        "authority/rifat/prisma-ui/visual-control/pc/layers.json",
        "tools/identity_binding_resolver_core.py",
    ]
    existing = {x["path"] for x in snapshot.get("files", [])}
    for rel in wanted:
        if rel not in existing:
            snapshot["files"].append({"path": rel, "sha256": "", "bytes": 0, "required": True, "readOnly": True})
    snapshot["files"] = sorted(snapshot["files"], key=lambda x: x["path"])
    snapshot["meshRunId"] = "github-actions-33370426993-pc-catalog-route-binding-mesh"
    write_json(path, registry)


def validate_final() -> None:
    sys.path.insert(0, str(PRISMA_HTML / "tools"))
    from identity_binding_resolver_core import authority_indexes, load_registry, validate_registry

    errors, warnings = validate_registry(load_registry())
    if errors:
        raise SystemExit("BINDING_VALIDATION_ERRORS=" + repr(errors))
    indexes = authority_indexes()
    expected = {
        "routes": "pc.catalog.route",
        "componentOwners": COMPONENT_ID,
        "cssOwners": CSS_ID,
        "regionOwners": REGION_ID,
        "slots": SLOT_ID,
        "layers": LAYER_ID,
    }
    for index, value in expected.items():
        if value not in indexes[index]:
            raise SystemExit(f"MISSING_CANONICAL_INDEX={index}:{value}")
    binding = next(x for x in load_registry()["bindings"] if x.get("bindingId") == "BND.VIS.SURFACE.CONTENT.PRIMARY.PC.CATALOG.WORKSPACE.V1")
    if binding.get("status") != "RESOLVED" or binding["targets"][0].get("status") != "RESOLVED":
        raise SystemExit("PC_CATALOG_BINDING_NOT_RESOLVED")
    print("PC_CATALOG_BINDING_SOURCE_ONLY=RESOLVED")
    print("WARNINGS=" + repr(warnings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vc-out", required=True)
    args = parser.parse_args()
    vc_out = Path(args.vc_out).resolve()
    vc_out.mkdir(parents=True, exist_ok=True)

    patch_visual_control()
    patch_layer_certification()
    run(["node", "--check", "tools/quality/ui-visual-control.mjs"], cwd=APP)
    run(["node", "tools/quality/ui-visual-control.mjs", "visual-control:report", "--surface", "pc", "--output-root", str(vc_out)], cwd=APP)
    prove_and_promote(vc_out / "visual-control")
    patch_resolver()
    run([sys.executable, "-m", "py_compile", "tools/identity_binding_resolver_core.py"], cwd=PRISMA_HTML)
    patch_element_registry()
    run([sys.executable, "tools/identity_binding_resolver.py", "refresh-snapshot", "--write"], cwd=PRISMA_HTML)
    validate_final()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
