from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_utils import write_json, write_text


def emit_ui_dictionary(out_dir: Path, dictionary: dict[str, Any]) -> None:
    write_json(out_dir / "ui_dictionary.json", dictionary)
    write_text(out_dir / "ui_dictionary.md", _dictionary_markdown(dictionary))


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def _dictionary_markdown(dictionary: dict[str, Any]) -> str:
    routes = dictionary.get("routes", [])
    components = dictionary.get("components", [])
    states = dictionary.get("states", [])
    styles = dictionary.get("styles", [])
    assets = dictionary.get("assets", [])
    hotspots = dictionary.get("hotspots", [])

    route_rows = [
        [
            item.get("route_id", ""),
            item.get("path", ""),
            item.get("entry_file", ""),
            item.get("screen_component_id", ""),
        ]
        for item in routes
    ]

    component_rows = [
        [
            item.get("component_id", ""),
            item.get("export_name", ""),
            item.get("kind", ""),
            item.get("file_path", ""),
        ]
        for item in components[:120]
    ]

    state_rows = [
        [
            item.get("state_id", ""),
            item.get("file_path", ""),
            str(len(item.get("readers", []))),
            str(len(item.get("writers", []))),
        ]
        for item in states
    ]

    style_rows = [[item.get("style_id", ""), item.get("file_path", ""), str(len(item.get("referenced_by", [])))] for item in styles]
    asset_rows = [[item.get("asset_id", ""), item.get("kind", ""), item.get("file_path", ""), str(len(item.get("referenced_by", [])))] for item in assets]

    hotspot_rows = [
        [
            item.get("hotspot_id", ""),
            item.get("screen_or_global", ""),
            item.get("risk", ""),
            item.get("title", ""),
        ]
        for item in hotspots
    ]

    lines = [
        "# UI Dictionary",
        "",
        f"- version: `{dictionary.get('version', '')}`",
        "- generated_by: `tools/ui_map deterministic`",
        f"- routes: `{len(routes)}`",
        f"- components: `{len(components)}`",
        f"- states: `{len(states)}`",
        f"- styles: `{len(styles)}`",
        f"- assets: `{len(assets)}`",
        f"- hotspots: `{len(hotspots)}`",
        "",
        "## Routes",
        _table(["route_id", "path", "entry_file", "screen_component_id"], route_rows) if route_rows else "(none)",
        "",
        "## Components (first 120)",
        _table(["component_id", "export_name", "kind", "file_path"], component_rows) if component_rows else "(none)",
        "",
        "## States",
        _table(["state_id", "file_path", "readers", "writers"], state_rows) if state_rows else "(none)",
        "",
        "## Styles",
        _table(["style_id", "file_path", "referenced_by_count"], style_rows) if style_rows else "(none)",
        "",
        "## Assets",
        _table(["asset_id", "kind", "file_path", "referenced_by_count"], asset_rows) if asset_rows else "(none)",
        "",
        "## Hotspots",
        _table(["hotspot_id", "screen_or_global", "risk", "title"], hotspot_rows) if hotspot_rows else "(none)",
        "",
        "_Component table is intentionally truncated; full dataset is in `ui_dictionary.json`._",
    ]
    return "\n".join(lines).rstrip() + "\n"
