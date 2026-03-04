from __future__ import annotations

from typing import Any

EDGE_ORDER = {
    "imports": 1,
    "renders": 2,
    "reads": 3,
    "writes": 4,
    "uses_style": 5,
    "uses_asset": 6,
    "route_to_screen": 7,
    "layout_wraps": 8,
}

KIND_ORDER = {
    "route": 1,
    "screen": 2,
    "layout": 3,
    "block": 4,
    "control": 5,
    "dataviz": 6,
    "nav": 7,
    "brand": 8,
    "state": 9,
    "style": 10,
}


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted(set(values), key=lambda item: (item.lower(), item))


def sort_ui_dictionary(data: dict[str, Any]) -> dict[str, Any]:
    routes = sorted(
        data.get("routes", []),
        key=lambda item: (item.get("route_id", ""), item.get("path", ""), item.get("entry_file", "")),
    )
    for route in routes:
        route["data_source_ids"] = _sorted_unique(route.get("data_source_ids", []))

    components = sorted(
        data.get("components", []),
        key=lambda item: (
            item.get("component_id", ""),
            item.get("file_path", ""),
            item.get("export_name", ""),
        ),
    )
    for component in components:
        component["imports"] = _sorted_unique(component.get("imports", []))
        component["renders"] = _sorted_unique(component.get("renders", []))
        uses = component.setdefault("uses", {})
        uses["hooks"] = _sorted_unique(uses.get("hooks", []))
        uses["stores"] = _sorted_unique(uses.get("stores", []))
        uses["css"] = _sorted_unique(uses.get("css", []))
        uses["assets"] = _sorted_unique(uses.get("assets", []))

    states = sorted(
        data.get("states", []),
        key=lambda item: (item.get("state_id", ""), item.get("file_path", "")),
    )
    for state in states:
        state["readers"] = _sorted_unique(state.get("readers", []))
        state["writers"] = _sorted_unique(state.get("writers", []))
        events = state.get("events", [])
        state["events"] = sorted(
            events,
            key=lambda item: (item.get("name", ""), item.get("writer_component_id", "")),
        )

    styles = sorted(
        data.get("styles", []),
        key=lambda item: (item.get("style_id", ""), item.get("file_path", "")),
    )
    for style in styles:
        style["referenced_by"] = _sorted_unique(style.get("referenced_by", []))

    assets = sorted(
        data.get("assets", []),
        key=lambda item: (item.get("asset_id", ""), item.get("file_path", "")),
    )
    for asset in assets:
        asset["referenced_by"] = _sorted_unique(asset.get("referenced_by", []))

    edges = sorted(
        data.get("edges", []),
        key=lambda item: (
            EDGE_ORDER.get(item.get("type", ""), 99),
            item.get("from", ""),
            item.get("to", ""),
            item.get("notes", ""),
        ),
    )

    hotspots = sorted(
        data.get("hotspots", []),
        key=lambda item: (
            item.get("hotspot_id", ""),
            item.get("screen_or_global", ""),
            item.get("title", ""),
        ),
    )
    for hotspot in hotspots:
        hotspot["files"] = _sorted_unique(hotspot.get("files", []))
        hotspot["components"] = _sorted_unique(hotspot.get("components", []))
        hotspot["change_types"] = _sorted_unique(hotspot.get("change_types", []))

    sorted_data = dict(data)
    sorted_data["routes"] = routes
    sorted_data["components"] = components
    sorted_data["states"] = states
    sorted_data["styles"] = styles
    sorted_data["assets"] = assets
    sorted_data["edges"] = edges
    sorted_data["hotspots"] = hotspots
    return sorted_data


def find_component_by_file(
    components: list[dict[str, Any]], file_path: str, export_name: str | None = None
) -> dict[str, Any] | None:
    filtered = [item for item in components if item.get("file_path") == file_path]
    if export_name is not None:
        filtered = [item for item in filtered if item.get("export_name") == export_name]
    if not filtered:
        return None
    filtered.sort(key=lambda item: item.get("component_id", ""))
    return filtered[0]
