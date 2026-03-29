from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from .io_utils import write_text


def _node_key(raw: str) -> str:
    value = raw.replace("-", "_").replace("/", "_").replace(".", "_").replace(":", "_")
    return "n_" + "".join(ch for ch in value if ch.isalnum() or ch == "_")


def _label_for_route(route: dict[str, Any]) -> str:
    return f"{route.get('path', '')}"


def _label_for_component(component: dict[str, Any]) -> str:
    export_name = component.get("export_name", "")
    file_name = component.get("file_path", "").split("/")[-1]
    return f"{export_name}\\n{file_name}"


def _label_for_state(state: dict[str, Any]) -> str:
    return state.get("file_path", "").split("/")[-1]


def _label_for_style(style: dict[str, Any]) -> str:
    return style.get("file_path", "").split("/")[-1]


def _label_for_asset(asset: dict[str, Any]) -> str:
    return asset.get("file_path", "").split("/")[-1]


def emit_mermaid_graphs(out_dir: Path, dictionary: dict[str, Any], discovery: dict[str, Any]) -> None:
    write_text(out_dir / "keystone-ui-graph.mmd", _global_graph(dictionary, discovery))
    screen_map = discovery.get("screen_mapping", {})
    for index in range(1, 7):
        screen_id = f"screen-{index:02d}"
        info = screen_map.get(screen_id, {})
        content = _screen_graph(screen_id, info, dictionary)
        write_text(out_dir / "screens" / f"{screen_id}.mmd", content)


def _global_graph(dictionary: dict[str, Any], discovery: dict[str, Any]) -> str:
    routes = dictionary.get("routes", [])
    components = dictionary.get("components", [])
    states = dictionary.get("states", [])
    styles = dictionary.get("styles", [])
    assets = dictionary.get("assets", [])
    edges = dictionary.get("edges", [])

    component_by_id = {item["component_id"]: item for item in components}

    route_nodes = [(item["route_id"], _label_for_route(item)) for item in routes]
    screen_ids = {
        info.get("component_id")
        for info in discovery.get("screen_mapping", {}).values()
        if info.get("component_id") and info.get("component_id") != "(undiscovered)"
    }

    screen_nodes = []
    shared_nodes = []
    brand_nodes = []
    for component in components:
        cid = component["component_id"]
        file_path = component.get("file_path", "")
        label = _label_for_component(component)
        if cid in screen_ids:
            screen_nodes.append((cid, label))
            continue
        if "/brand/" in file_path:
            brand_nodes.append((cid, label))
            continue
        if file_path.startswith("packages/ui-kit/"):
            shared_nodes.append((cid, label))

    state_nodes = [(item["state_id"], _label_for_state(item)) for item in states]
    style_nodes = [(item["style_id"], _label_for_style(item)) for item in styles]
    asset_nodes = [(item["asset_id"], _label_for_asset(item)) for item in assets]

    lines = ["flowchart LR"]

    def render_nodes(title: str, nodes: list[tuple[str, str]], shape: str = "[\"{label}\"]") -> None:
        lines.append(f"  subgraph \"{title}\"")
        for node_id, label in sorted(nodes, key=lambda item: item[0]):
            key = _node_key(node_id)
            safe_label = label.replace('"', "'")
            lines.append(f"    {key}{shape.format(label=safe_label)}")
        lines.append("  end")

    render_nodes("Routes", route_nodes)
    render_nodes("Screens", screen_nodes)
    render_nodes("Shared UI Kit", shared_nodes)
    render_nodes("Brand System", brand_nodes)
    render_nodes("State/Stores", state_nodes, shape="([\"{label}\"])")
    render_nodes("Styles/Assets", style_nodes + asset_nodes, shape="[[\"{label}\"]]")

    lines.extend(
        [
            "  subgraph Legend",
            "    lg1[\"imports\"]",
            "    lg2[\"renders\"]",
            "    lg3[\"reads/writes\"]",
            "    lg4[\"uses_style/uses_asset\"]",
            "    lg5[\"route_to_screen/layout_wraps\"]",
            "  end",
        ]
    )

    allowed = {
        "imports": "-->",
        "renders": "==>",
        "reads": "-.->",
        "writes": "-.->",
        "uses_style": "-.->",
        "uses_asset": "-.->",
        "route_to_screen": "==>",
        "layout_wraps": "-->",
    }

    seen: set[tuple[str, str, str]] = set()
    for edge in edges:
        edge_type = edge.get("type")
        if edge_type not in allowed:
            continue
        source = edge.get("from", "")
        target = edge.get("to", "")
        key = (source, target, edge_type)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"  {_node_key(source)} {allowed[edge_type]}|{edge_type}| {_node_key(target)}")

    return "\n".join(lines).rstrip() + "\n"


def _screen_graph(screen_id: str, info: dict[str, str], dictionary: dict[str, Any]) -> str:
    components = dictionary.get("components", [])
    edges = dictionary.get("edges", [])
    routes = dictionary.get("routes", [])

    component_by_id = {item["component_id"]: item for item in components}
    route_by_id = {item["route_id"]: item for item in routes}

    root_component = info.get("component_id", "(undiscovered)")
    root_route = info.get("route_id", "(undiscovered)")

    adjacency: dict[str, list[tuple[str, str]]] = {}
    for edge in edges:
        adjacency.setdefault(edge.get("from", ""), []).append((edge.get("to", ""), edge.get("type", "")))

    included: set[str] = set()
    queue: deque[str] = deque()

    if root_route and root_route != "(undiscovered)":
        queue.append(root_route)
    if root_component and root_component != "(undiscovered)":
        queue.append(root_component)

    while queue and len(included) < 48:
        node = queue.popleft()
        if node in included:
            continue
        included.add(node)
        for target, edge_type in sorted(adjacency.get(node, []), key=lambda item: (item[1], item[0])):
            if edge_type in {"imports", "renders", "reads", "writes", "uses_style", "uses_asset", "route_to_screen", "layout_wraps"}:
                queue.append(target)

    lines = [f"%% {screen_id} graph", "flowchart TD"]

    for node_id in sorted(included):
        if node_id in component_by_id:
            label = _label_for_component(component_by_id[node_id]).replace('"', "'")
            lines.append(f"  {_node_key(node_id)}[\"{label}\"]")
        elif node_id in route_by_id:
            label = _label_for_route(route_by_id[node_id]).replace('"', "'")
            lines.append(f"  {_node_key(node_id)}((\"{label}\"))")
        else:
            lines.append(f"  {_node_key(node_id)}[[\"{node_id}\"]]")

    arrows = {
        "imports": "-->",
        "renders": "==>",
        "reads": "-.->",
        "writes": "-.->",
        "uses_style": "-.->",
        "uses_asset": "-.->",
        "route_to_screen": "==>",
        "layout_wraps": "-->",
    }

    for edge in sorted(edges, key=lambda item: (item.get("type", ""), item.get("from", ""), item.get("to", ""))):
        source = edge.get("from", "")
        target = edge.get("to", "")
        edge_type = edge.get("type", "")
        if source not in included or target not in included:
            continue
        if edge_type not in arrows:
            continue
        lines.append(f"  {_node_key(source)} {arrows[edge_type]}|{edge_type}| {_node_key(target)}")

    route_file = info.get("route_file", "(undiscovered)")
    component_file = info.get("component_file", "(undiscovered)")
    lines.extend(
        [
            "",
            "%% Where-to-edit",
            f"%% If you want to change layout -> {route_file}",
            f"%% If you want to change interactions -> {component_file}",
            "%% If you want to change brand -> central config files only (do not override :root)",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"
