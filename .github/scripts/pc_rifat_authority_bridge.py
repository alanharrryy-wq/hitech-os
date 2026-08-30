#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_resolver(core_path: Path) -> None:
    core = core_path.read_text(encoding="utf-8")
    needle = 'REGISTRY_PATH = IDENTITY / "registries" / "element-bindings.registry.json"\n'
    if "BINDINGS_REGISTRY_PATH" not in core:
        if needle not in core:
            raise SystemExit("RESOLVER_REGISTRY_ANCHOR_NOT_FOUND")
        core = core.replace(
            needle,
            needle + 'BINDINGS_REGISTRY_PATH = IDENTITY / "registries" / "bindings.registry.json"\n',
            1,
        )

    start_marker = "def authority_indexes() -> dict[str, Any]:\n"
    end_marker = "\n\ndef selector_from_artifact"
    if start_marker not in core or end_marker not in core:
        raise SystemExit("RESOLVER_AUTHORITY_INDEX_BLOCK_NOT_FOUND")
    start = core.index(start_marker)
    end = core.index(end_marker, start)
    replacement = '''def authority_indexes() -> dict[str, Any]:
    """Load binding authority from per-surface sources declared by bindings.registry.json.

    Legacy Tablet paths remain valid. New surfaces can publish isolated certified
    visual-control sources without overwriting another surface's authority.
    """
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
            path = ROOT / rel_path
            if not path.is_file():
                raise FileNotFoundError(f"declared binding authority source is missing: {rel_path}")
            loaded[rel_path] = load_json(path)
        return loaded[rel_path]

    def same_surface(item: dict[str, Any], surface: str) -> bool:
        value = item.get("surface")
        return value in {None, surface}

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
            owner_parent = str(Path(binding_source["ownerSource"]).parent)
            candidate = f"{owner_parent}/components.json"
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
    core_path.write_text(core[:start] + replacement + core[end:], encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--vc", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    vc = Path(args.vc).resolve() / "visual-control"
    rifat = repo / "prisma-html" / "authority" / "rifat"
    dst = rifat / "prisma-ui" / "visual-control" / "pc"
    dst.mkdir(parents=True, exist_ok=True)

    required = [
        "registry.json",
        "surfaces.json",
        "routes.json",
        "components.json",
        "editable-slots.json",
        "owners.json",
        "layers.json",
        "risks.json",
    ]
    for name in required:
        src = vc / name
        if not src.is_file():
            raise SystemExit(f"MISSING_PC_VISUAL_CONTROL={src}")
        shutil.copy2(src, dst / name)

    risks = json.loads((vc / "risks.json").read_text(encoding="utf-8"))
    owners = json.loads((vc / "owners.json").read_text(encoding="utf-8"))
    slots = json.loads((vc / "editable-slots.json").read_text(encoding="utf-8"))
    layers = json.loads((vc / "layers.json").read_text(encoding="utf-8"))
    routes = json.loads((vc / "routes.json").read_text(encoding="utf-8"))
    components = json.loads((vc / "components.json").read_text(encoding="utf-8"))
    if risks.get("status") != "CERTIFIED" or risks.get("blockerCount") != 0 or risks.get("warningCount") != 0:
        raise SystemExit(f"PC_VISUAL_CONTROL_NOT_CLEAN={risks}")
    if risks.get("activeImportantCount") != 0:
        raise SystemExit("PC_ACTIVE_IMPORTANT_NOT_ZERO")

    bindings_path = rifat / "identity" / "registries" / "bindings.registry.json"
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    pc = next((x for x in bindings.get("bindings", []) if x.get("surface") == "pc"), None)
    if pc is None:
        raise SystemExit("PC_BINDING_SOURCE_ENTRY_MISSING")
    pc.update(
        {
            "readiness": "CERTIFIED_BINDING_SOURCE",
            "routeSource": "authority/rifat/prisma-ui/routes.json",
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
            "missing": [],
            "runtimeProjectionAllowed": False,
            "sourceCertification": {
                "status": "CERTIFIED",
                "surface": "pc",
                "generator": "apps/terminal-de-venta-system/tools/quality/ui-visual-control.mjs",
                "mode": "source-only",
                "productMutationAllowed": False,
            },
        }
    )
    bindings["version"] = "1.1.0"
    write_json(bindings_path, bindings)

    patch_resolver(repo / "prisma-html" / "tools" / "identity_binding_resolver_core.py")

    element_path = rifat / "identity" / "registries" / "element-bindings.registry.json"
    element = json.loads(element_path.read_text(encoding="utf-8"))
    snapshot = element["authoritySnapshot"]
    wanted = [
        "authority/rifat/prisma-ui/visual-control/pc/owners.json",
        "authority/rifat/prisma-ui/visual-control/pc/components.json",
        "authority/rifat/prisma-ui/visual-control/pc/editable-slots.json",
        "authority/rifat/prisma-ui/visual-control/pc/layers.json",
    ]
    existing = {x["path"] for x in snapshot.get("files", [])}
    for rel in wanted:
        if rel not in existing:
            snapshot["files"].append(
                {"path": rel, "sha256": "", "bytes": 0, "required": True, "readOnly": True}
            )
    snapshot["files"] = sorted(snapshot["files"], key=lambda x: x["path"])
    snapshot["meshRunId"] = "github-actions-33305075845-rifat-pc-authority-mesh"
    write_json(element_path, element)

    print(
        json.dumps(
            {
                "status": "SOURCE_BRIDGE_STAGED",
                "pcReadiness": pc["readiness"],
                "routeCount": pc["routeCount"],
                "componentCount": pc["componentCount"],
                "regionOwnerCount": pc["regionOwnerCount"],
                "editableSlotCount": pc["editableSlotCount"],
                "slotUnitCount": pc["slotUnitCount"],
                "layerCount": pc["layerCount"],
                "snapshotFilesAdded": wanted,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
