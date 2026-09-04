#!/usr/bin/env python3
"""Core loader, validator and deterministic compiler for PRISMA identity authority."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "authority" / "rifat" / "identity"
COMPILED = IDENTITY / "compiled" / "current"
WINDOWS_ABSOLUTE = re.compile(r"[A-Za-z]:\\")
SURFACES = ("shared-ui", "tablet", "pc", "mobile", "web", "chart-lab", "control-center")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def flatten_css_name(token_id: str) -> str:
    return "--prisma-identity-" + token_id.replace(".", "-")


def load_model() -> dict[str, Any]:
    token_registry = load_json(IDENTITY / "registries" / "semantic-tokens.registry.json")
    profile_registry = load_json(IDENTITY / "registries" / "identity.registry.json")
    adapter_registry = load_json(IDENTITY / "registries" / "surface-adapters.registry.json")
    binding_registry = load_json(IDENTITY / "registries" / "bindings.registry.json")
    export_registry = load_json(IDENTITY / "registries" / "portable-export.registry.json")
    activation = load_json(IDENTITY / "activation" / "active.identity.json")
    profiles = {
        item["id"]: load_json(IDENTITY / item["path"])
        for item in profile_registry["profiles"]
    }
    adapters = {
        item["surface"]: load_json(IDENTITY / item["path"])
        for item in adapter_registry["adapters"]
    }
    bindings = {item["surface"]: item for item in binding_registry["bindings"]}
    return {
        "tokens": token_registry,
        "profileRegistry": profile_registry,
        "adapterRegistry": adapter_registry,
        "bindingRegistry": binding_registry,
        "exportRegistry": export_registry,
        "activation": activation,
        "profiles": profiles,
        "adapters": adapters,
        "bindings": bindings,
    }


def merge_tokens(model: dict[str, Any], profile_id: str, surface: str) -> dict[str, Any]:
    defaults = {item["id"]: item["default"] for item in model["tokens"]["tokens"]}
    defaults.update(model["profiles"][profile_id].get("tokenOverrides", {}))
    defaults.update(model["adapters"][surface].get("tokenOverrides", {}))
    return defaults


def build_compilation(model: dict[str, Any] | None = None) -> dict[str, bytes]:
    model = model or load_model()
    activation = model["activation"]
    profile_id = activation["selectedProfileId"]
    profile = model["profiles"][profile_id]
    files: dict[str, bytes] = {}
    projections: dict[str, Any] = {}
    binding_ready = 0
    blocked = 0

    for surface in SURFACES:
        adapter = model["adapters"][surface]
        binding = model["bindings"][surface]
        if binding["readiness"] == "CERTIFIED_BINDING_SOURCE":
            status = "BINDING_READY_SOURCE_ONLY"
            binding_ready += 1
        elif binding["readiness"] == "NEUTRAL_SOURCE_READY":
            status = "NEUTRAL_SOURCE_READY"
        else:
            status = "BLOCKED_BY_MISSING_VISUAL_CONTROL_BINDINGS"
            blocked += 1
        projection = {
            "schema": "prisma.identity.compiled-projection.v1",
            "surface": surface,
            "profileId": profile_id,
            "profileName": profile["name"],
            "adapterId": adapter["id"],
            "status": status,
            "runtimeProjectionAllowed": False,
            "tokens": merge_tokens(model, profile_id, surface),
            "binding": binding,
            "projectionRules": adapter["projectionRules"],
            "forbiddenMutations": adapter["forbiddenMutations"],
        }
        projections[surface] = projection
        files[f"projections/{surface}.identity-projection.json"] = canonical_bytes(projection)

    input_hashes = {}
    for relative in (
        "registries/semantic-tokens.registry.json",
        "registries/identity.registry.json",
        "registries/surface-adapters.registry.json",
        "registries/bindings.registry.json",
        "registries/portable-export.registry.json",
        "activation/active.identity.json",
    ):
        input_hashes[relative] = digest((IDENTITY / relative).read_bytes())
    for profile_id_value, profile_value in sorted(model["profiles"].items()):
        input_hashes[f"profiles/{profile_id_value}.identity.json"] = digest(canonical_bytes(profile_value))
    for surface, adapter_value in sorted(model["adapters"].items()):
        input_hashes[f"adapters/{surface}.adapter.json"] = digest(canonical_bytes(adapter_value))

    manifest = {
        "schema": "prisma.identity.compilation-manifest.v1",
        "version": "1.0.0",
        "status": "SOURCE_READY_MULTI_SURFACE_BINDINGS" if blocked == 0 else "SOURCE_READY_PARTIAL_BINDINGS",
        "selectedProfileId": profile_id,
        "selectedProfileName": profile["name"],
        "selectedAt": activation["selectedAt"],
        "surfaceCount": len(SURFACES),
        "bindingReadyCount": binding_ready,
        "neutralSourceReadyCount": sum(1 for surface in SURFACES if model["bindings"][surface]["readiness"] == "NEUTRAL_SOURCE_READY"),
        "blockedSurfaceCount": blocked,
        "runtimeMutationCount": 0,
        "runtimeProjectionAllowed": False,
        "portableElementExport": {
            "status": "SOURCE_READY_INSTRUCTION_ONLY",
            "artifactSchema": model["exportRegistry"]["artifactSchema"],
            "supportedKindCount": len(model["exportRegistry"]["supportedKinds"]),
            "readOnlyImportInspection": True,
            "productApplicationAllowed": False,
        },
        "inputHashes": input_hashes,
        "projectionFiles": sorted(f"projections/{surface}.identity-projection.json" for surface in SURFACES),
        "hardTruth": "Compiled authority is not runtime certification.",
    }
    files["manifest.json"] = canonical_bytes(manifest)

    bundle = {
        "manifest": manifest,
        "profiles": [model["profiles"][item["id"]] for item in model["profileRegistry"]["profiles"]],
        "tokenDefinitions": model["tokens"]["tokens"],
        "projections": projections,
        "surfaceAdapters": model["adapters"],
        "portableExportRegistry": model["exportRegistry"],
    }
    files["identity-bundle.json"] = canonical_bytes(bundle)
    files["identity-bundle.js"] = (
        "window.PRISMA_IDENTITY_BUNDLE = "
        + json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + ";\n"
    ).encode("utf-8")

    css_lines = [
        "/* @generated by tools/compile_identity_dictionary.py",
        " * authority-only preview tokens; not application runtime",
        " * manual-edits-forbidden: true",
        " */",
        ":root {",
    ]
    shared_tokens = projections["shared-ui"]["tokens"]
    token_types = {item["id"]: item["type"] for item in model["tokens"]["tokens"]}
    for token_id, value in sorted(shared_tokens.items()):
        if token_types.get(token_id) in {"color", "css-value", "font-family", "length", "duration", "easing", "number", "integer"}:
            css_lines.append(f"  {flatten_css_name(token_id)}: {value};")
    css_lines.append("}")
    files["identity.tokens.css"] = ("\n".join(css_lines) + "\n").encode("utf-8")
    return files


def validate_model(check_compiled: bool = True) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    required = [
        IDENTITY / "README.md",
        IDENTITY / "contract" / "PRISMA_IDENTITY_DICTIONARY_CONTRACT.md",
        IDENTITY / "registries" / "semantic-tokens.registry.json",
        IDENTITY / "registries" / "identity.registry.json",
        IDENTITY / "registries" / "surface-adapters.registry.json",
        IDENTITY / "registries" / "bindings.registry.json",
        IDENTITY / "registries" / "portable-export.registry.json",
        IDENTITY / "schemas" / "portable-element-export.schema.json",
        IDENTITY / "schemas" / "portable-export-registry.schema.json",
        IDENTITY / "contract" / "PRISMA_PORTABLE_ELEMENT_EXPORT_CONTRACT.md",
        IDENTITY / "portable" / "README.md",
        IDENTITY / "activation" / "active.identity.json",
    ]
    for path in required:
        if not path.is_file():
            problems.append(f"missing required identity file: {path.relative_to(ROOT).as_posix()}")
    if problems:
        return problems, warnings

    model = load_model()
    token_ids = [item["id"] for item in model["tokens"]["tokens"]]
    if len(token_ids) != len(set(token_ids)):
        problems.append("duplicate semantic token id")
    token_set = set(token_ids)
    profile_ids = set(model["profiles"])
    if model["activation"]["selectedProfileId"] not in profile_ids:
        problems.append("selected identity profile does not exist")
    if model["activation"].get("runtimeProjection") is not False:
        problems.append("iteration 1 runtime projection must remain false")
    if set(model["adapters"]) != set(SURFACES):
        problems.append(f"surface adapter set mismatch: {sorted(model['adapters'])}")
    if set(model["bindings"]) != set(SURFACES):
        problems.append(f"binding set mismatch: {sorted(model['bindings'])}")

    export_registry = model["exportRegistry"]
    if export_registry.get("artifactSchema") != "prisma.identity.portable-element-export.v1":
        problems.append("portable export artifact schema mismatch")
    if export_registry.get("artifactExtension") != ".prisma-visual.json":
        problems.append("portable export extension mismatch")
    if export_registry.get("instructionOnly") is not True:
        problems.append("portable export must remain instruction-only")
    if export_registry.get("runtimeMutationAllowed") is not False:
        problems.append("portable export runtime mutation must remain false")
    kinds = [item.get("kind") for item in export_registry.get("supportedKinds", [])]
    expected_kinds = {
        "identity-profile",
        "semantic-token",
        "surface-adapter",
        "preview-component-recipe",
    }
    if set(kinds) != expected_kinds:
        problems.append(f"portable export kind set mismatch: {sorted(kinds)}")
    component_ids = [item.get("id") for item in export_registry.get("viewerComponents", [])]
    if len(component_ids) != len(set(component_ids)) or len(component_ids) < 2:
        problems.append("portable export viewer component registry is incomplete or duplicated")
    if export_registry.get("bindingPolicy", {}).get("unknownBindingsMustRemainNull") is not True:
        problems.append("portable export must keep unknown bindings null")
    if export_registry.get("bindingPolicy", {}).get("productApplicationForbidden") is not True:
        problems.append("portable export must forbid product application")

    for profile_id, profile in model["profiles"].items():
        unknown = sorted(set(profile.get("tokenOverrides", {})) - token_set)
        if unknown:
            problems.append(f"profile {profile_id} uses unknown tokens: {unknown}")
        if len(profile.get("traits", [])) < 3:
            problems.append(f"profile {profile_id} has insufficient semantic traits")
    for surface, adapter in model["adapters"].items():
        if adapter.get("surface") != surface:
            problems.append(f"adapter surface mismatch: {surface}")
        unknown = sorted(set(adapter.get("tokenOverrides", {})) - token_set)
        if unknown:
            problems.append(f"adapter {surface} uses unknown tokens: {unknown}")
        if "priority-override" not in adapter.get("forbiddenMutations", []):
            problems.append(f"adapter {surface} does not forbid priority overrides")

    # Grounded all-surface binding truth.
    visual_root = ROOT / "authority/rifat/prisma-ui/visual-control"
    visual_registry = load_json(visual_root / "registry.json")
    visual_surfaces = load_json(visual_root / "surfaces.json")
    owners = load_json(visual_root / "owners.json")
    slots = load_json(visual_root / "editable-slots.json")
    layers = load_json(visual_root / "layers.json")
    routes = load_json(visual_root / "routes.json")
    expanded = load_json(visual_root / "expanded/manifest.json")

    expected_surface_set = set(SURFACES)
    end_surfaces = {"tablet", "pc", "mobile", "web", "chart-lab", "control-center"}
    if visual_registry.get("status") != "CERTIFIED":
        problems.append("all-surface Visual Control source is not CERTIFIED")
    if visual_registry.get("scopeMode") != "ALL_SURFACES_CANONICAL" or visual_registry.get("canonicalGlobal") is not True:
        problems.append("Visual Control authority is not an all-surface canonical promotion")
    if set(visual_registry.get("targetSurfaces") or []) != expected_surface_set:
        problems.append("Visual Control target surface set is incomplete")
    if set(visual_registry.get("runtimeTargetSurfaces") or []) != end_surfaces:
        problems.append("Visual Control runtime target surface set is incomplete")
    if set(item.get("surface") for item in visual_surfaces.get("surfaces", [])) != expected_surface_set:
        problems.append("Visual Control surface registry is incomplete")
    if expanded.get("schema") != "prisma.ui.visual-control.expanded-manifest.v1":
        problems.append("expanded Visual Control manifest schema mismatch")
    if expanded.get("scopeMode") != "ALL_SURFACES_CANONICAL" or expanded.get("canonicalGlobal") is not True:
        problems.append("expanded Visual Control authority is not all-surface canonical")

    if owners.get("status") != "CERTIFIED" or slots.get("status") != "CERTIFIED" or layers.get("status") != "CERTIFIED" or routes.get("status") != "CERTIFIED":
        problems.append("all-surface Visual Control compact authority is not fully certified")

    expanded_counts = expanded.get("countsBySurface") if isinstance(expanded.get("countsBySurface"), dict) else {}
    for surface in SURFACES:
        binding = model["bindings"][surface]
        expected_readiness = "NEUTRAL_SOURCE_READY" if surface == "shared-ui" else "CERTIFIED_BINDING_SOURCE"
        if binding.get("readiness") != expected_readiness:
            problems.append(f"{surface} binding readiness mismatch: {binding.get('readiness')}")
        for field in ("routeSource", "ownerSource", "slotSource", "layerSource", "expandedSource"):
            raw = binding.get(field)
            if not raw:
                problems.append(f"{surface} missing binding source field: {field}")
                continue
            source_path = ROOT / raw
            if field == "expandedSource":
                if not source_path.is_dir():
                    problems.append(f"{surface} expanded binding source missing: {raw}")
            elif not source_path.is_file():
                problems.append(f"{surface} binding source missing: {raw}")
        counts = expanded_counts.get(surface)
        if not isinstance(counts, dict):
            problems.append(f"{surface} expanded counts missing")
            continue
        for field in ("layers", "editableSlots", "regionOwners"):
            if not isinstance(counts.get(field), int) or counts[field] <= 0:
                problems.append(f"{surface} expanded {field} evidence is empty")
        if surface in end_surfaces and (not isinstance(counts.get("routes"), int) or counts["routes"] <= 0):
            problems.append(f"{surface} expanded route evidence is empty")
        if binding.get("layerCount") != counts.get("layers"):
            problems.append(f"{surface} binding layerCount drift")
        if binding.get("editableSlotCount") != counts.get("editableSlots"):
            problems.append(f"{surface} binding editableSlotCount drift")
        if binding.get("regionOwnerCount") != counts.get("regionOwners"):
            problems.append(f"{surface} binding regionOwnerCount drift")
        if binding.get("routeCount") != counts.get("routes"):
            problems.append(f"{surface} binding routeCount drift")

    for path in IDENTITY.rglob("*"):
        if not path.is_file() or "compiled/current" in path.as_posix():
            continue
        data = path.read_text(encoding="utf-8", errors="ignore")
        if "!important" in data:
            problems.append(f"priority override found: {path.relative_to(ROOT).as_posix()}")
        if WINDOWS_ABSOLUTE.search(data):
            problems.append(f"local absolute path found: {path.relative_to(ROOT).as_posix()}")

    if check_compiled and not problems:
        expected = build_compilation(model)
        expected_names = set(expected)
        actual_names = {
            path.relative_to(COMPILED).as_posix()
            for path in COMPILED.rglob("*") if path.is_file()
        } if COMPILED.is_dir() else set()
        if expected_names != actual_names:
            problems.append(f"compiled file set mismatch: expected={sorted(expected_names)} actual={sorted(actual_names)}")
        else:
            for relative, content in expected.items():
                if (COMPILED / relative).read_bytes() != content:
                    problems.append(f"compiled drift: {relative}")
    if model["bindings"]["shared-ui"].get("missing"):
        warnings.append("Shared UI remains a neutral source and lacks detailed editable-slot certification.")
    return problems, warnings
