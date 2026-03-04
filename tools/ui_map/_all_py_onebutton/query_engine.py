from __future__ import annotations

from collections import deque
from typing import Any


class QueryEngine:
    def __init__(self, dictionary: dict[str, Any], discovery: dict[str, Any]) -> None:
        self.dictionary = dictionary
        self.discovery = discovery
        self.routes = dictionary.get("routes", [])
        self.components = dictionary.get("components", [])
        self.states = dictionary.get("states", [])
        self.styles = dictionary.get("styles", [])
        self.assets = dictionary.get("assets", [])
        self.edges = dictionary.get("edges", [])
        self.hotspots = dictionary.get("hotspots", [])

        self.component_by_id = {item["component_id"]: item for item in self.components}
        self.component_ids_by_file: dict[str, list[str]] = {}
        for component in self.components:
            self.component_ids_by_file.setdefault(component["file_path"], []).append(component["component_id"])
        for values in self.component_ids_by_file.values():
            values.sort()

        self.adj: dict[str, list[dict[str, str]]] = {}
        self.rev: dict[str, list[dict[str, str]]] = {}
        for edge in self.edges:
            source = edge.get("from", "")
            target = edge.get("to", "")
            edge_type = edge.get("type", "")
            payload = {"from": source, "to": target, "type": edge_type}
            self.adj.setdefault(source, []).append(payload)
            self.rev.setdefault(target, []).append(payload)

        for table in (self.adj, self.rev):
            for key in table:
                table[key].sort(key=lambda item: (item.get("type", ""), item.get("from", ""), item.get("to", "")))

    def dependents_of_file(self, file_path: str) -> list[dict[str, str]]:
        file_components = set(self.component_ids_by_file.get(file_path, []))
        dependents: list[dict[str, str]] = []
        for component in self.components:
            imports = component.get("imports", [])
            if file_path in imports:
                dependents.append(
                    {
                        "component_id": component["component_id"],
                        "file_path": component["file_path"],
                        "reason": "imports_file",
                    }
                )
            elif file_components and any(edge.get("to") in file_components for edge in self.adj.get(component["component_id"], [])):
                dependents.append(
                    {
                        "component_id": component["component_id"],
                        "file_path": component["file_path"],
                        "reason": "depends_on_export",
                    }
                )
        dependents.sort(key=lambda item: (item["file_path"], item["component_id"], item["reason"]))
        return dependents

    def screens_using_component(self, component_id: str) -> list[str]:
        screen_map = self.discovery.get("screen_mapping", {})
        matched: list[str] = []
        for screen_id, info in sorted(screen_map.items()):
            tree = self.component_tree(screen_id)
            if component_id in tree.get("component_ids", []):
                matched.append(screen_id)
        return matched

    def files_touched_by_screen(self, screen_id: str) -> list[str]:
        tree = self.component_tree(screen_id)
        files = {self.component_by_id[item]["file_path"] for item in tree.get("component_ids", []) if item in self.component_by_id}
        info = self.discovery.get("screen_mapping", {}).get(screen_id, {})
        if info.get("route_file"):
            files.add(info["route_file"])
        if info.get("component_file"):
            files.add(info["component_file"])

        component_ids = set(tree.get("component_ids", []))
        for state in self.states:
            if component_ids.intersection(state.get("readers", [])) or component_ids.intersection(state.get("writers", [])):
                files.add(state["file_path"])
        for style in self.styles:
            if component_ids.intersection(style.get("referenced_by", [])):
                files.add(style["file_path"])
        for asset in self.assets:
            if component_ids.intersection(asset.get("referenced_by", [])):
                files.add(asset["file_path"])

        return sorted(files)

    def state_readers(self, state_id: str) -> list[str]:
        for state in self.states:
            if state.get("state_id") == state_id:
                return sorted(state.get("readers", []))
        return []

    def state_writers(self, state_id: str) -> list[str]:
        for state in self.states:
            if state.get("state_id") == state_id:
                return sorted(state.get("writers", []))
        return []

    def assets_used_by_screen(self, screen_id: str) -> list[dict[str, str]]:
        files = set(self.files_touched_by_screen(screen_id))
        used = [
            {"asset_id": item["asset_id"], "file_path": item["file_path"], "kind": item["kind"]}
            for item in self.assets
            if item["file_path"] in files
        ]
        used.sort(key=lambda item: (item["kind"], item["file_path"], item["asset_id"]))
        return used

    def styles_used_by_screen(self, screen_id: str) -> list[dict[str, str]]:
        files = set(self.files_touched_by_screen(screen_id))
        used = [
            {"style_id": item["style_id"], "file_path": item["file_path"]}
            for item in self.styles
            if item["file_path"] in files
        ]
        used.sort(key=lambda item: (item["file_path"], item["style_id"]))
        return used

    def hotspots_by_risk(self, level: str) -> list[dict[str, Any]]:
        matched = [item for item in self.hotspots if item.get("risk") == level]
        matched.sort(key=lambda item: (item.get("screen_or_global", ""), item.get("title", ""), item.get("hotspot_id", "")))
        return matched

    def component_tree(self, screen_id: str) -> dict[str, Any]:
        info = self.discovery.get("screen_mapping", {}).get(screen_id, {})
        root = info.get("component_id")
        if not root or root == "(undiscovered)":
            return {"screen_id": screen_id, "root_component_id": root or "", "component_ids": [], "edges": []}

        visited: set[str] = set()
        queue: deque[str] = deque([root])
        captured_edges: list[dict[str, str]] = []

        while queue and len(visited) < 80:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            for edge in self.adj.get(node, []):
                if edge.get("type") not in {"renders", "imports", "reads", "writes"}:
                    continue
                captured_edges.append(edge)
                target = edge.get("to", "")
                if target in self.component_by_id and target not in visited:
                    queue.append(target)

        captured_edges.sort(key=lambda item: (item.get("type", ""), item.get("from", ""), item.get("to", "")))
        return {
            "screen_id": screen_id,
            "root_component_id": root,
            "component_ids": sorted(visited),
            "edges": captured_edges,
        }

    def imports_of_file(self, file_path: str) -> list[str]:
        imports: set[str] = set()
        for component in self.components:
            if component.get("file_path") == file_path:
                imports.update(component.get("imports", []))
        return sorted(imports)

    def routes_index(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for route in self.routes:
            rows.append(
                {
                    "route_id": route.get("route_id", ""),
                    "path": route.get("path", ""),
                    "entry_file": route.get("entry_file", ""),
                    "screen_component_id": route.get("screen_component_id", ""),
                }
            )
        rows.sort(key=lambda item: (item["path"], item["route_id"], item["entry_file"]))
        return rows

    def changeset_hint(self, file_or_component: str) -> dict[str, Any]:
        if file_or_component in self.component_by_id:
            component = self.component_by_id[file_or_component]
            hotspots = [item for item in self.hotspots if file_or_component in item.get("components", [])]
            hotspots.sort(key=lambda item: (item.get("risk", ""), item.get("title", "")))
            return {
                "type": "component",
                "target": file_or_component,
                "file_path": component.get("file_path", ""),
                "kind": component.get("kind", ""),
                "touches": [item.get("title", "") for item in hotspots],
            }

        dependent_components = self.dependents_of_file(file_or_component)
        hotspots = [item for item in self.hotspots if file_or_component in item.get("files", [])]
        hotspots.sort(key=lambda item: (item.get("risk", ""), item.get("title", "")))
        return {
            "type": "file",
            "target": file_or_component,
            "dependents": dependent_components,
            "hotspots": [item.get("title", "") for item in hotspots],
            "note": "If this file is shared across screens, validate route-level and hotspot-level impacts before edits.",
        }

    def available_queries(self) -> list[str]:
        return [
            "dependents_of_file(file)",
            "screens_using_component(component_id)",
            "files_touched_by_screen(screen_id)",
            "state_readers(state_id)",
            "state_writers(state_id)",
            "assets_used_by_screen(screen_id)",
            "styles_used_by_screen(screen_id)",
            "hotspots_by_risk(level)",
            "component_tree(screen_id)",
            "imports_of_file(file)",
            "routes_index()",
            "changeset_hint(file_or_component)",
        ]
