from __future__ import annotations

from pathlib import Path
from typing import Any

from .graph import sort_ui_dictionary
from .ids import asset_id, component_id, hotspot_id, route_id, state_id, style_id
from .io_utils import load_json, write_text

REQUIRED_DOCS = [
    "README.md",
    "keystone-ui-graph.mmd",
    "ui_dictionary.json",
    "ui_dictionary.md",
    "owners_and_hotspots.md",
    "meta/schema.json",
    "meta/glossary.md",
    "meta/improvements_100.md",
    "queries/README.md",
    "queries/samples.md",
    "screens/screen-01.mmd",
    "screens/screen-02.mmd",
    "screens/screen-03.mmd",
    "screens/screen-04.mmd",
    "screens/screen-05.mmd",
    "screens/screen-06.mmd",
]


def validate_schema_conformance(dictionary: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    for key in required:
        if key not in dictionary:
            errors.append(f"missing top-level key: {key}")

    if dictionary.get("generated_by", {}).get("tool") != "tools/ui_map":
        errors.append("generated_by.tool must be tools/ui_map")
    if dictionary.get("generated_by", {}).get("mode") != "deterministic":
        errors.append("generated_by.mode must be deterministic")

    if not isinstance(dictionary.get("routes", []), list):
        errors.append("routes must be an array")
    if not isinstance(dictionary.get("components", []), list):
        errors.append("components must be an array")
    if not isinstance(dictionary.get("states", []), list):
        errors.append("states must be an array")
    if not isinstance(dictionary.get("styles", []), list):
        errors.append("styles must be an array")
    if not isinstance(dictionary.get("assets", []), list):
        errors.append("assets must be an array")
    if not isinstance(dictionary.get("edges", []), list):
        errors.append("edges must be an array")
    if not isinstance(dictionary.get("hotspots", []), list):
        errors.append("hotspots must be an array")

    return errors


def validate_deterministic_ids(dictionary: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for route in dictionary.get("routes", []):
        expected = route_id(route.get("path", ""))
        if route.get("route_id") != expected:
            errors.append(f"route_id mismatch for path {route.get('path', '')}")

    for component in dictionary.get("components", []):
        expected = component_id(component.get("file_path", ""), component.get("export_name", ""))
        if component.get("component_id") != expected:
            errors.append(f"component_id mismatch for {component.get('file_path', '')}::{component.get('export_name', '')}")

    for state in dictionary.get("states", []):
        expected = state_id(state.get("file_path", ""))
        if state.get("state_id") != expected:
            errors.append(f"state_id mismatch for {state.get('file_path', '')}")

    for style in dictionary.get("styles", []):
        expected = style_id(style.get("file_path", ""))
        if style.get("style_id") != expected:
            errors.append(f"style_id mismatch for {style.get('file_path', '')}")

    for asset in dictionary.get("assets", []):
        expected = asset_id(asset.get("file_path", ""))
        if asset.get("asset_id") != expected:
            errors.append(f"asset_id mismatch for {asset.get('file_path', '')}")

    for hotspot in dictionary.get("hotspots", []):
        expected = hotspot_id(hotspot.get("screen_or_global", ""), hotspot.get("title", ""))
        if hotspot.get("hotspot_id") != expected:
            errors.append(f"hotspot_id mismatch for {hotspot.get('title', '')}")

    return errors


def validate_sorting(dictionary: dict[str, Any]) -> list[str]:
    sorted_copy = sort_ui_dictionary(dictionary)
    if sorted_copy != dictionary:
        return ["dictionary is not deterministically sorted"]
    return []


def validate_docs_exist(out_dir: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in REQUIRED_DOCS:
        if not (out_dir / relative_path).exists():
            missing.append(relative_path)
    return missing


def validate_minimum_discovery(dictionary: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if len(dictionary.get("routes", [])) < 1:
        errors.append("minimum route discovery unmet (routes < 1)")
    if len(dictionary.get("components", [])) < 50:
        errors.append("minimum component discovery unmet (components < 50)")
    return errors


def write_blocked_report(out_dir: Path, discovery: dict[str, Any], reasons: list[str]) -> None:
    lines = [
        "# Keystone UI Map",
        "",
        "## BLOCKED",
        "",
        "Validation blocked generation because minimum discovery requirements were not met.",
        "",
        "### Reasons",
        *[f"- {reason}" for reason in reasons],
        "",
        "### Paths searched",
        *[f"- `{item}`" for item in discovery.get("paths_searched", [])],
        "",
        "### Route files discovered",
        *[f"- `{item}`" for item in discovery.get("route_files", [])],
        "",
        "### Screen roots discovered",
        *[f"- `{item}`" for item in discovery.get("screen_roots", [])],
    ]
    write_text(out_dir / "README.md", "\n".join(lines).rstrip() + "\n")


def run_validation(out_dir: Path, discovery: dict[str, Any]) -> dict[str, Any]:
    dictionary = load_json(out_dir / "ui_dictionary.json")
    schema = load_json(out_dir / "meta" / "schema.json")

    errors: list[str] = []
    errors.extend(validate_schema_conformance(dictionary, schema))
    errors.extend(validate_deterministic_ids(dictionary))
    errors.extend(validate_sorting(dictionary))

    missing_docs = validate_docs_exist(out_dir)
    if missing_docs:
        errors.extend([f"missing required doc: {item}" for item in missing_docs])

    min_errors = validate_minimum_discovery(dictionary)
    blocked = len(min_errors) > 0
    if blocked:
        write_blocked_report(out_dir, discovery, min_errors)
        errors.extend(min_errors)

    return {
        "ok": len(errors) == 0,
        "blocked": blocked,
        "errors": errors,
        "counts": {
            "routes": len(dictionary.get("routes", [])),
            "components": len(dictionary.get("components", [])),
            "states": len(dictionary.get("states", [])),
        },
    }
