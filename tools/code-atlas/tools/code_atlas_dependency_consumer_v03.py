#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code Atlas dependency-map consumer V03.

Consumes the reusable Capatch dependency-map analyzer JSON and emits Code Atlas
friendly reports without changing Capatch core or the existing Code Atlas GUI
Python graph behavior.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

VERSION = "3.1.0"
DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_PROJECT_ROOT = DEFAULT_REPO_ROOT / "apps" / "terminal-de-venta-system"
DEFAULT_OUTPUT_DIR = Path(r"F:\descargasf")
DEFAULT_RAW_REPORT = DEFAULT_OUTPUT_DIR / "terminal_dependency_map_clean_v02_2.json"
DEFAULT_ANALYZER_RELATIVE = Path("tools") / "dependency_map" / "analyze_project.py"
STAMP_FORMAT = "%y%m%d_%H%M"

LANGUAGE_LABELS = {
    "py": "Python",
    "js": "JavaScript",
    "jsx": "JSX",
    "mjs": "JavaScript module",
    "cjs": "CommonJS",
    "ts": "TypeScript",
    "tsx": "TSX",
}

ENTRYPOINT_NAMES = {
    "package.json",
    "pnpm-workspace.yaml",
    "pnpm-workspace.yml",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "tsconfig.json",
    "jsconfig.json",
    "schema.prisma",
    "seed.mjs",
    "seed.ts",
    "runtime-smoke.mjs",
    "module-registry.ts",
    "module-registry.tsx",
}

NEXT_ENTRYPOINT_SUFFIXES = (
    "/app/page.tsx",
    "/app/page.ts",
    "/app/layout.tsx",
    "/app/layout.ts",
    "/page.tsx",
    "/page.ts",
    "/layout.tsx",
    "/layout.ts",
    "/route.ts",
    "/route.js",
)

EXIT_OK = 0
EXIT_INPUT = 1
EXIT_RUN_FAILED = 2
EXIT_VERIFY_FAILED = 3
EXIT_INTERRUPTED = 130


@dataclass(frozen=True)
class OutputBundle:
    raw_json: Path | None
    summary_json: Path
    markdown: Path
    tree_txt: Path
    graph_json: Path
    unresolved_md: Path


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def safe_slug(value: Any) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return "project"
    forbidden = '<>:"/\\|?*'
    safe = "".join(ch if ch not in forbidden else "_" for ch in cleaned)
    safe = safe.replace(" ", "_").strip("._")
    return safe or "project"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_path(value: Any) -> Path:
    return Path(str(value)).expanduser().resolve()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"JSON report not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON report is not an object: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def edge_kind(edge: dict[str, Any]) -> str:
    return clean_text(edge.get("kind"))


def edge_source(edge: dict[str, Any]) -> str:
    return clean_text(edge.get("_source", edge.get("source"))).replace("\\", "/")


def edge_target(edge: dict[str, Any]) -> str:
    return clean_text(edge.get("_target", edge.get("target"))).replace("\\", "/")


def edge_raw(edge: dict[str, Any]) -> str:
    return clean_text(edge.get("raw"))


def _raw_edge_source(edge: dict[str, Any]) -> str:
    return clean_text(edge.get("source")).replace("\\", "/")


def _raw_edge_target(edge: dict[str, Any]) -> str:
    return clean_text(edge.get("target")).replace("\\", "/")


def classify_edge(edge: dict[str, Any]) -> str:
    explicit = clean_text(edge.get("_classification"))
    if explicit:
        return explicit
    kind = edge_kind(edge)
    if "unresolved" in kind:
        return "unresolved"
    if "external" in kind or kind == "package-dependency":
        return "external"
    if kind == "python-import":
        target = _raw_edge_target(edge)
        if _looks_like_project_path(target):
            return "internal"
        return "external"
    return "internal"


SOURCE_EXTENSIONS = (".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".css", ".scss", ".json", ".prisma")


def _looks_like_project_path(value: str) -> bool:
    normalized = clean_text(value).replace("\\", "/")
    if not normalized:
        return False
    if normalized.startswith(("node:", "@")):
        return False
    if "/" in normalized:
        return True
    return normalized.endswith(SOURCE_EXTENSIONS)


def _looks_like_malformed_import(edge: dict[str, Any]) -> bool:
    kind = edge_kind(edge)
    target = _raw_edge_target(edge)
    raw = edge_raw(edge)
    if "unresolved" in kind:
        return False
    suspicious = (target, raw)
    return any(
        item.startswith("\\.")
        or item.startswith("\\/")
        or "\\.\\." in item
        or "\\/" in item
        for item in suspicious
        if item
    )


def _source_path_index(payload: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for item in as_list(payload.get("edges")):
        if not isinstance(item, dict):
            continue
        source = _raw_edge_source(item)
        if source:
            paths.add(source)
        target = _raw_edge_target(item)
        if classify_edge(item) == "internal" and _looks_like_project_path(target):
            paths.add(target)
    return paths


def _resolve_python_internal_target(edge: dict[str, Any], known_paths: set[str]) -> str:
    if edge_kind(edge) != "python-import":
        return ""
    source = _raw_edge_source(edge)
    target = _raw_edge_target(edge)
    if not source or not target:
        return ""
    if _looks_like_project_path(target) and target in known_paths:
        return target
    parts = [part for part in target.split(".") if part]
    if not parts:
        return ""
    source_parent = str(Path(source.replace("\\", "/")).parent).replace("\\", "/")
    module_path = "/".join(parts)
    candidates = [
        f"{source_parent}/{module_path}.py",
        f"{source_parent}/{module_path}/__init__.py",
        f"{module_path}.py",
        f"{module_path}/__init__.py",
    ]
    for candidate in candidates:
        normalized = candidate.replace("./", "")
        if normalized in known_paths:
            return normalized
    return ""


def normalized_edges(payload: dict[str, Any]) -> list[dict[str, Any]]:
    known_paths = _source_path_index(payload)
    result: list[dict[str, Any]] = []
    for edge in as_list(payload.get("edges")):
        if not isinstance(edge, dict):
            continue
        cloned = dict(edge)
        cloned["_source"] = _raw_edge_source(edge)
        cloned["_target"] = _raw_edge_target(edge)
        if _looks_like_malformed_import(edge):
            cloned["_classification"] = "ignored"
            cloned["_ignore_reason"] = "malformed import-like literal"
            result.append(cloned)
            continue
        if edge_kind(edge) == "python-import":
            resolved = _resolve_python_internal_target(edge, known_paths)
            if resolved:
                cloned["_classification"] = "internal"
                cloned["_target"] = resolved
            else:
                cloned["_classification"] = "external"
        else:
            cloned["_classification"] = classify_edge(edge)
        result.append(cloned)
    return result


def external_package_name(edge: dict[str, Any]) -> str:
    raw = edge_raw(edge) or edge_target(edge)
    target = edge_target(edge) or raw
    value = clean_text(target or raw).replace("\\", "/")
    if not value:
        return "external"
    if value.startswith("node:"):
        return value.split("/", 1)[0]
    if value.startswith("@"):
        parts = value.split("/")
        return "/".join(parts[:2]) if len(parts) >= 2 else value
    if "/" in value:
        return value.split("/", 1)[0]
    return value.split(".", 1)[0]


def language_names(summary: dict[str, Any]) -> list[str]:
    counts = as_dict(summary.get("source_counts"))
    result: list[str] = []
    for ext in sorted(counts):
        label = LANGUAGE_LABELS.get(str(ext).lower(), str(ext).upper())
        result.append(f"{label} ({counts[ext]})")
    return result


def detect_frameworks(payload: dict[str, Any], edges: list[dict[str, Any]]) -> list[str]:
    project = as_dict(payload.get("project"))
    names: set[str] = set(str(item).lower() for item in as_list(project.get("frameworks")))
    targets = {edge_target(edge).split("/", 1)[0].lower() for edge in edges}
    paths = "\n".join(edge_source(edge) for edge in edges).lower()

    if "next" in targets or "/app/page." in paths or "/app/layout." in paths or "/route.ts" in paths:
        names.add("nextjs")
    if "react" in targets or any(edge_source(edge).endswith((".tsx", ".jsx")) for edge in edges):
        names.add("react")
    if "prisma" in targets or "schema.prisma" in paths or ".prisma.ts" in paths:
        names.add("prisma")
    if "zod" in targets:
        names.add("zod")
    return sorted(names)


def detect_entrypoints(payload: dict[str, Any], edges: list[dict[str, Any]]) -> list[str]:
    sources = {edge_source(edge) for edge in edges if edge_source(edge)}
    candidates: set[str] = set()
    for source in sources:
        name = Path(source).name
        normalized = source.replace("\\", "/")
        if name in ENTRYPOINT_NAMES:
            candidates.add(normalized)
            continue
        if normalized.endswith(NEXT_ENTRYPOINT_SUFFIXES):
            candidates.add(normalized)
            continue
        if "/app/api/" in normalized and name in {"route.ts", "route.js"}:
            candidates.add(normalized)
            continue
        if "/src/server/" in normalized and name in {"index.ts", "index.tsx", "index.js", "index.mjs"}:
            candidates.add(normalized)
            continue
        if normalized.endswith("/components/pos/pos-live-binding.tsx"):
            candidates.add(normalized)
    return sorted(candidates)


def workspace_patterns(payload: dict[str, Any]) -> list[str]:
    project = as_dict(payload.get("project"))
    return [clean_text(item).replace("\\", "/") for item in as_list(project.get("pnpm_workspaces")) if clean_text(item)]


def workspace_for(path: str, workspaces: Iterable[str]) -> str:
    normalized = clean_text(path).replace("\\", "/")
    best = ""
    for workspace in sorted((w.strip("/") for w in workspaces if w), key=len, reverse=True):
        if normalized == workspace or normalized.startswith(workspace + "/"):
            best = workspace
            break
    return best or "(root/tools)"


def workspace_relationships(edges: list[dict[str, Any]], workspaces: list[str]) -> dict[str, Any]:
    relationships: Counter[tuple[str, str]] = Counter()
    samples: list[dict[str, str]] = []
    for edge in edges:
        if classify_edge(edge) != "internal":
            continue
        source = edge_source(edge)
        target = edge_target(edge)
        source_ws = workspace_for(source, workspaces)
        target_ws = workspace_for(target, workspaces)
        if source_ws == target_ws:
            continue
        relationships[(source_ws, target_ws)] += 1
        if len(samples) < 80:
            samples.append({"source": source, "target": target, "source_workspace": source_ws, "target_workspace": target_ws, "raw": edge_raw(edge)})
    return {
        "relationship_counts": [
            {"source_workspace": src, "target_workspace": dst, "edges": count}
            for (src, dst), count in sorted(relationships.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
        ],
        "sample_cross_workspace_edges": samples,
    }


def tsconfig_aliases(payload: dict[str, Any]) -> list[dict[str, Any]]:
    project = as_dict(payload.get("project"))
    configs = as_list(project.get("tsconfigs"))
    result: list[dict[str, Any]] = []
    for config in configs:
        cfg = as_dict(config)
        result.append({
            "path": clean_text(cfg.get("path")),
            "base_url": clean_text(cfg.get("base_url")) or ".",
            "paths": as_dict(cfg.get("paths")),
        })
    root_cfg = as_dict(project.get("tsconfig"))
    if root_cfg and not result:
        result.append({
            "path": clean_text(root_cfg.get("path")),
            "base_url": clean_text(root_cfg.get("base_url")) or ".",
            "paths": as_dict(root_cfg.get("paths")),
        })
    return result


def top_external_imports(edges: list[dict[str, Any]], limit: int = 40) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    examples: dict[str, str] = {}
    for edge in edges:
        if classify_edge(edge) != "external":
            continue
        target = edge_target(edge)
        raw = edge_raw(edge) or target
        root = external_package_name(edge)
        if not root:
            continue
        counts[root] += 1
        examples.setdefault(root, raw)
    return [
        {"package": name, "edges": count, "example_raw": examples.get(name, "")}
        for name, count in counts.most_common(limit)
    ]


def unresolved_groups(edges: list[dict[str, Any]], workspaces: list[str]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in edges:
        if classify_edge(edge) != "unresolved":
            continue
        source = edge_source(edge)
        grouped[workspace_for(source, workspaces)].append({
            "source": source,
            "target": edge_target(edge),
            "kind": edge_kind(edge),
            "raw": edge_raw(edge),
        })
    return [
        {"workspace": workspace, "count": len(items), "items": sorted(items, key=lambda item: (item["source"], item["raw"]))}
        for workspace, items in sorted(grouped.items(), key=lambda item: item[0])
    ]


def build_graph_json(payload: dict[str, Any], edges: list[dict[str, Any]], workspaces: list[str]) -> dict[str, Any]:
    root = clean_text(payload.get("root"))
    project = as_dict(payload.get("project"))
    nodes: dict[str, dict[str, Any]] = {}
    graph_edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    def add_node(key: str, label: str, kind: str, path: str = "", metadata: dict[str, Any] | None = None) -> None:
        if key not in nodes:
            nodes[key] = {"id": key, "label": label, "kind": kind, "path": path, "metadata": metadata or {}, "inbound": 0, "outbound": 0}
        elif metadata:
            nodes[key]["metadata"].update(metadata)

    add_node("project:root", Path(root).name if root else "project", "project", root, {"package_name": project.get("package_name", "")})
    for workspace in workspaces:
        add_node(f"workspace:{workspace}", workspace, "workspace", workspace)
        graph_edges[("project:root", f"workspace:{workspace}", "contains", workspace)] = {
            "source": "project:root",
            "target": f"workspace:{workspace}",
            "kind": "contains",
            "raw": workspace,
            "weight": 1,
        }

    for edge in edges:
        source = edge_source(edge)
        target = edge_target(edge)
        kind = edge_kind(edge)
        raw = edge_raw(edge)
        classification = classify_edge(edge)
        if classification == "ignored":
            continue
        source_ws = workspace_for(source, workspaces)
        source_key = f"file:{source}"
        add_node(source_key, Path(source).name or source, "file", source, {"workspace": source_ws})
        if source_ws in workspaces:
            graph_edges[(f"workspace:{source_ws}", source_key, "contains", source)] = {
                "source": f"workspace:{source_ws}",
                "target": source_key,
                "kind": "contains",
                "raw": source,
                "weight": 1,
            }

        if classification == "internal":
            target_ws = workspace_for(target, workspaces)
            target_key = f"file:{target}"
            add_node(target_key, Path(target).name or target, "file", target, {"workspace": target_ws})
        elif classification == "external":
            external_name = external_package_name(edge)
            target_key = f"external:{external_name}"
            add_node(target_key, external_name or "external", "external", external_name or target, {"raw": raw})
        else:
            unresolved_name = raw or target
            target_key = f"unresolved:{source}:{unresolved_name}"
            add_node(target_key, unresolved_name or "unresolved", "unresolved", target, {"raw": raw, "source": source})

        key = (source_key, target_key, kind, raw)
        if key not in graph_edges:
            graph_edges[key] = {"source": source_key, "target": target_key, "kind": kind, "raw": raw, "weight": 0, "classification": classification}
        graph_edges[key]["weight"] += 1

    for edge in graph_edges.values():
        if edge["source"] in nodes:
            nodes[edge["source"]]["outbound"] += edge.get("weight", 1)
        if edge["target"] in nodes:
            nodes[edge["target"]]["inbound"] += edge.get("weight", 1)

    return {
        "tool": "code-atlas dependency consumer graph",
        "version": VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "nodes": sorted(nodes.values(), key=lambda node: (node["kind"], node["path"], node["id"])),
        "edges": sorted(graph_edges.values(), key=lambda item: (item["source"], item["target"], item["kind"], item.get("raw", ""))),
    }


def build_summary_report(raw_path: Path | None, payload: dict[str, Any], graph_path: Path, tree_path: Path, md_path: Path, unresolved_path: Path) -> dict[str, Any]:
    summary = as_dict(payload.get("summary"))
    project = as_dict(payload.get("project"))
    edges = normalized_edges(payload)
    workspaces = workspace_patterns(payload)
    internal = [edge for edge in edges if classify_edge(edge) == "internal"]
    external = [edge for edge in edges if classify_edge(edge) == "external"]
    unresolved = [edge for edge in edges if classify_edge(edge) == "unresolved"]
    ignored = [edge for edge in edges if classify_edge(edge) == "ignored"]
    salvage_edges = [edge for edge in edges if edge_source(edge).startswith("tools/prisma-salvage")]

    return {
        "tool": "code-atlas dependency-map consumer",
        "version": VERSION,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_report": str(raw_path) if raw_path else "",
        "project_root": clean_text(payload.get("root")),
        "project_profile": {
            "package_name": project.get("package_name", ""),
            "package_manager": project.get("package_manager", "unknown"),
            "frameworks": detect_frameworks(payload, edges),
            "languages": language_names(summary),
            "source_counts": as_dict(summary.get("source_counts")),
        },
        "dependency_summary": {
            "files_scanned": int(summary.get("files_scanned") or 0),
            "source_files": int(summary.get("source_files") or 0),
            "edges": int(summary.get("edges") or len(edges)),
            "internal_edges": len(internal),
            "external_edges": len(external),
            "unresolved_edges": len(unresolved),
            "ignored_edges": len(ignored),
            "salvage_edges": len(salvage_edges),
        },
        "tsconfig_aliases": tsconfig_aliases(payload),
        "pnpm_workspaces": workspaces,
        "workspace_relationships": workspace_relationships(edges, workspaces),
        "important_entrypoints": detect_entrypoints(payload, edges),
        "top_external_imports": top_external_imports(edges),
        "unresolved_groups": unresolved_groups(edges, workspaces),
        "generated_files": {
            "summary_json": "",
            "markdown_report": str(md_path),
            "tree_txt": str(tree_path),
            "graph_json": str(graph_path),
            "unresolved_md": str(unresolved_path),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    profile = as_dict(report.get("project_profile"))
    dep = as_dict(report.get("dependency_summary"))
    generated = as_dict(report.get("generated_files"))
    lines = [
        "# Code Atlas Dependency Consumer V03.1 Report",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Input report: `{report.get('input_report', '')}`",
        f"Project root: `{report.get('project_root', '')}`",
        "",
        "## Status",
        "",
        f"- Files scanned: `{dep.get('files_scanned', 0)}`",
        f"- Source files: `{dep.get('source_files', 0)}`",
        f"- Edges: `{dep.get('edges', 0)}`",
        f"- Internal edges: `{dep.get('internal_edges', 0)}`",
        f"- External edges: `{dep.get('external_edges', 0)}`",
        f"- Unresolved edges: `{dep.get('unresolved_edges', 0)}`",
        f"- Ignored malformed edges: `{dep.get('ignored_edges', 0)}`",
        f"- Salvage edges: `{dep.get('salvage_edges', 0)}`",
        "",
        "## Project profile",
        "",
        f"- Package: `{profile.get('package_name', '')}`",
        f"- Package manager: `{profile.get('package_manager', '')}`",
        f"- Frameworks: `{', '.join(map(str, profile.get('frameworks') or []))}`",
        f"- Languages: `{', '.join(map(str, profile.get('languages') or []))}`",
        "",
        "## pnpm workspaces",
        "",
    ]
    for workspace in as_list(report.get("pnpm_workspaces")):
        lines.append(f"- `{workspace}`")
    if not as_list(report.get("pnpm_workspaces")):
        lines.append("- None detected.")

    lines.extend(["", "## TypeScript / JavaScript aliases", ""])
    aliases = as_list(report.get("tsconfig_aliases"))
    if not aliases:
        lines.append("- None detected.")
    for alias in aliases:
        cfg = as_dict(alias)
        lines.append(f"- `{cfg.get('path', '') or '(root)'}` baseUrl=`{cfg.get('base_url', '.')}`")
        paths = as_dict(cfg.get("paths"))
        for key, value in sorted(paths.items()):
            lines.append(f"  - `{key}` -> `{value}`")

    lines.extend(["", "## Important entrypoints", ""])
    for path in as_list(report.get("important_entrypoints"))[:120]:
        lines.append(f"- `{path}`")
    if not as_list(report.get("important_entrypoints")):
        lines.append("- None detected.")

    lines.extend(["", "## Workspace relationships", ""])
    relationships = as_dict(report.get("workspace_relationships"))
    counts = as_list(relationships.get("relationship_counts"))
    if not counts:
        lines.append("- No cross-workspace internal edges detected.")
    for item in counts:
        row = as_dict(item)
        lines.append(f"- `{row.get('source_workspace')}` -> `{row.get('target_workspace')}`: `{row.get('edges')}` edges")

    lines.extend(["", "## Top external imports", ""])
    for item in as_list(report.get("top_external_imports"))[:40]:
        row = as_dict(item)
        lines.append(f"- `{row.get('package')}`: `{row.get('edges')}` edges, example `{row.get('example_raw')}`")
    if not as_list(report.get("top_external_imports")):
        lines.append("- None detected.")

    lines.extend(["", "## Unresolved imports", ""])
    groups = as_list(report.get("unresolved_groups"))
    if not groups:
        lines.append("- None. Nice, the import sewer is clean.")
    for group in groups:
        row = as_dict(group)
        lines.append(f"### {row.get('workspace')} ({row.get('count')} unresolved)")
        for item in as_list(row.get("items")):
            edge = as_dict(item)
            lines.append(f"- `{edge.get('source')}` -> `{edge.get('target')}` ({edge.get('kind')}: `{edge.get('raw')}`)")

    lines.extend(["", "## Generated files", ""])
    for key, value in generated.items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"


def render_tree(report: dict[str, Any], payload: dict[str, Any]) -> str:
    edges = normalized_edges(payload)
    workspaces = as_list(report.get("pnpm_workspaces"))
    by_workspace: dict[str, Counter[str]] = defaultdict(Counter)
    outbound: Counter[str] = Counter()
    inbound: Counter[str] = Counter()
    for edge in edges:
        source = edge_source(edge)
        target = edge_target(edge)
        if source:
            outbound[source] += 1
            by_workspace[workspace_for(source, workspaces)][source] += 1
        if classify_edge(edge) == "internal" and target:
            inbound[target] += 1
    lines = [
        "Code Atlas Dependency Tree V03.1",
        f"Generated: {report.get('generated_at', '')}",
        f"Project root: {report.get('project_root', '')}",
        "",
        "Project",
    ]
    for workspace in sorted(by_workspace.keys()):
        lines.append(f"+ {workspace}")
        ranked = sorted(by_workspace[workspace].items(), key=lambda item: (-item[1], item[0]))[:80]
        for path, out_count in ranked:
            in_count = inbound.get(path, 0)
            lines.append(f"  - {path}  [out:{out_count} in:{in_count}]")
    lines.extend(["", "Aliases"])
    for alias in as_list(report.get("tsconfig_aliases")):
        cfg = as_dict(alias)
        lines.append(f"+ {cfg.get('path', '') or '(root)'}")
        for key, value in sorted(as_dict(cfg.get("paths")).items()):
            lines.append(f"  - {key} -> {value}")
    lines.extend(["", "Unresolved"])
    groups = as_list(report.get("unresolved_groups"))
    if not groups:
        lines.append("- none")
    for group in groups:
        row = as_dict(group)
        lines.append(f"+ {row.get('workspace')}")
        for item in as_list(row.get("items")):
            edge = as_dict(item)
            lines.append(f"  - {edge.get('source')} -> {edge.get('raw') or edge.get('target')}")
    return "\n".join(lines) + "\n"


def render_unresolved_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Code Atlas unresolved imports V03.1",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Project root: `{report.get('project_root', '')}`",
        "",
    ]
    groups = as_list(report.get("unresolved_groups"))
    if not groups:
        lines.append("No unresolved imports detected.")
        return "\n".join(lines) + "\n"
    for group in groups:
        row = as_dict(group)
        lines.append(f"## {row.get('workspace')} ({row.get('count')} unresolved)")
        lines.append("")
        for item in as_list(row.get("items")):
            edge = as_dict(item)
            lines.append(f"- Source: `{edge.get('source')}`")
            lines.append(f"  - Target: `{edge.get('target')}`")
            lines.append(f"  - Raw: `{edge.get('raw')}`")
            lines.append(f"  - Kind: `{edge.get('kind')}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def make_output_bundle(output_dir: Path, project_name: str, stamp: str, raw_json: Path | None = None) -> OutputBundle:
    prefix = f"code_atlas_dependency_consumer_v03_{safe_slug(project_name)}_{stamp}"
    return OutputBundle(
        raw_json=raw_json,
        summary_json=output_dir / f"{prefix}_summary.json",
        markdown=output_dir / f"{prefix}_report.md",
        tree_txt=output_dir / f"{prefix}_tree.txt",
        graph_json=output_dir / f"{prefix}_graph.json",
        unresolved_md=output_dir / f"{prefix}_unresolved.md",
    )


def generate_reports(raw_report_path: Path | None, payload: dict[str, Any], output_dir: Path, formats: set[str]) -> OutputBundle:
    ensure_dir(output_dir)
    root = clean_text(payload.get("root")) or "project"
    project_name = Path(root).name if root else "project"
    stamp = datetime.now().strftime(STAMP_FORMAT)
    bundle = make_output_bundle(output_dir, project_name, stamp, raw_report_path)
    edges = normalized_edges(payload)
    workspaces = workspace_patterns(payload)
    graph = build_graph_json(payload, edges, workspaces)
    report = build_summary_report(raw_report_path, payload, bundle.graph_json, bundle.tree_txt, bundle.markdown, bundle.unresolved_md)
    report["generated_files"]["summary_json"] = str(bundle.summary_json)

    write_json(bundle.summary_json, report)
    if "graph" in formats or "all" in formats:
        write_json(bundle.graph_json, graph)
    if "md" in formats or "all" in formats:
        write_text(bundle.markdown, render_markdown(report))
        write_text(bundle.unresolved_md, render_unresolved_markdown(report))
    if "tree" in formats or "all" in formats:
        write_text(bundle.tree_txt, render_tree(report, payload))

    verify_generated(bundle, formats)
    return bundle


def verify_generated(bundle: OutputBundle, formats: set[str]) -> None:
    required = [bundle.summary_json]
    if "graph" in formats or "all" in formats:
        required.append(bundle.graph_json)
    if "md" in formats or "all" in formats:
        required.extend([bundle.markdown, bundle.unresolved_md])
    if "tree" in formats or "all" in formats:
        required.append(bundle.tree_txt)
    for path in required:
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"Generated output is missing or empty: {path}")
    load_json(bundle.summary_json)
    if ("graph" in formats or "all" in formats) and bundle.graph_json.exists():
        load_json(bundle.graph_json)


def run_analyzer(project_root: Path, analyzer_path: Path, output_dir: Path, max_files: int, exclude_dirs: list[str], timeout_seconds: int) -> Path:
    if not project_root.exists() or not project_root.is_dir():
        raise FileNotFoundError(f"Project root does not exist: {project_root}")
    if not analyzer_path.exists() or not analyzer_path.is_file():
        raise FileNotFoundError(f"dependency-map analyzer not found: {analyzer_path}")
    ensure_dir(output_dir)
    raw_path = output_dir / f"dependency_map_raw_{safe_slug(project_root.name)}_{datetime.now().strftime(STAMP_FORMAT)}.json"
    command = [
        sys.executable,
        str(analyzer_path),
        "--root",
        str(project_root),
        "--format",
        "json",
        "--output",
        str(raw_path),
        "--max-files",
        str(max_files),
    ]
    for item in exclude_dirs:
        clean = clean_text(item)
        if clean:
            command.extend(["--exclude-dir", clean])
    proc = subprocess.run(command, cwd=str(project_root), text=True, capture_output=True, timeout=timeout_seconds)
    if proc.returncode != 0:
        raise RuntimeError("dependency-map analyzer failed\nSTDOUT:\n" + proc.stdout[-3000:] + "\nSTDERR:\n" + proc.stderr[-3000:])
    if not raw_path.exists() or raw_path.stat().st_size <= 0:
        raise RuntimeError(f"dependency-map analyzer did not write JSON: {raw_path}")
    load_json(raw_path)
    return raw_path


def add_common_report_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for generated Code Atlas reports. Default: F:\\descargasf")
    parser.add_argument("--format", choices=["all", "json", "md", "tree", "graph"], default="all", help="Output family to generate. Summary JSON is always written.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Consume Capatch dependency-map JSON and produce Code Atlas reports.",
        epilog=(
            "Examples:\n"
            "  python code_atlas_dependency_consumer_v03.py report --report-json F:\\descargasf\\terminal_dependency_map_clean_v02_2.json --output-dir F:\\descargasf\n"
            "  python code_atlas_dependency_consumer_v03.py analyze --project-root F:\\repos\\hitech-os\\apps\\terminal-de-venta-system --exclude-dir prisma-salvage"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    report = sub.add_parser("report", help="Consume an existing dependency-map JSON report.")
    report.add_argument("--report-json", default=str(DEFAULT_RAW_REPORT), help="Existing dependency-map analyzer JSON report.")
    add_common_report_args(report)

    analyze = sub.add_parser("analyze", help="Run the installed dependency-map analyzer, then consume its JSON output.")
    analyze.add_argument("--project-root", default=str(DEFAULT_PROJECT_ROOT), help="Project root to analyze.")
    analyze.add_argument("--analyzer", default="", help="Analyzer path. Default: <project-root>\\tools\\dependency_map\\analyze_project.py")
    analyze.add_argument("--max-files", type=int, default=5000, help="Max files passed to dependency-map analyzer.")
    analyze.add_argument("--exclude-dir", action="append", default=[], help="Extra directory name to exclude. May be repeated.")
    analyze.add_argument("--timeout-seconds", type=int, default=180, help="Analyzer subprocess timeout.")
    add_common_report_args(analyze)

    verify = sub.add_parser("verify", help="Verify a dependency-map JSON report against simple gates.")
    verify.add_argument("--report-json", default=str(DEFAULT_RAW_REPORT), help="Existing dependency-map analyzer JSON report.")
    verify.add_argument("--max-unresolved", type=int, default=-1, help="Fail if unresolved_edges is above this value. -1 disables the gate.")
    verify.add_argument("--forbid-source-prefix", action="append", default=[], help="Fail if any edge source starts with this prefix.")
    return parser


def command_report(args: argparse.Namespace) -> int:
    report_path = resolve_path(args.report_json)
    output_dir = resolve_path(args.output_dir)
    formats = {args.format}
    payload = load_json(report_path)
    bundle = generate_reports(report_path, payload, output_dir, formats)
    print(json.dumps({
        "ok": True,
        "version": VERSION,
        "mode": "report",
        "input_report": str(report_path),
        "generated_files": {
            "summary_json": str(bundle.summary_json),
            "markdown_report": str(bundle.markdown) if bundle.markdown.exists() else "",
            "tree_txt": str(bundle.tree_txt) if bundle.tree_txt.exists() else "",
            "graph_json": str(bundle.graph_json) if bundle.graph_json.exists() else "",
            "unresolved_md": str(bundle.unresolved_md) if bundle.unresolved_md.exists() else "",
        },
    }, indent=2, ensure_ascii=False))
    return EXIT_OK


def command_analyze(args: argparse.Namespace) -> int:
    project_root = resolve_path(args.project_root)
    analyzer_path = resolve_path(args.analyzer) if clean_text(args.analyzer) else project_root / DEFAULT_ANALYZER_RELATIVE
    output_dir = resolve_path(args.output_dir)
    raw_path = run_analyzer(project_root, analyzer_path, output_dir, args.max_files, list(args.exclude_dir or []), args.timeout_seconds)
    payload = load_json(raw_path)
    bundle = generate_reports(raw_path, payload, output_dir, {args.format})
    print(json.dumps({
        "ok": True,
        "version": VERSION,
        "mode": "analyze",
        "raw_report": str(raw_path),
        "generated_files": {
            "summary_json": str(bundle.summary_json),
            "markdown_report": str(bundle.markdown) if bundle.markdown.exists() else "",
            "tree_txt": str(bundle.tree_txt) if bundle.tree_txt.exists() else "",
            "graph_json": str(bundle.graph_json) if bundle.graph_json.exists() else "",
            "unresolved_md": str(bundle.unresolved_md) if bundle.unresolved_md.exists() else "",
        },
    }, indent=2, ensure_ascii=False))
    return EXIT_OK


def command_verify(args: argparse.Namespace) -> int:
    report_path = resolve_path(args.report_json)
    payload = load_json(report_path)
    summary = as_dict(payload.get("summary"))
    edges = normalized_edges(payload)
    unresolved = int(summary.get("unresolved_edges") or len([edge for edge in edges if classify_edge(edge) == "unresolved"]))
    failures: list[str] = []
    if args.max_unresolved >= 0 and unresolved > args.max_unresolved:
        failures.append(f"unresolved_edges {unresolved} > max_unresolved {args.max_unresolved}")
    for prefix in args.forbid_source_prefix or []:
        normalized_prefix = clean_text(prefix).replace("\\", "/").strip("/")
        if not normalized_prefix:
            continue
        matches = [edge_source(edge) for edge in edges if edge_source(edge).startswith(normalized_prefix)]
        if matches:
            failures.append(f"forbidden source prefix {normalized_prefix!r} matched {len(matches)} edges")
    result = {
        "ok": not failures,
        "version": clean_text(payload.get("version")),
        "files_scanned": int(summary.get("files_scanned") or 0),
        "source_files": int(summary.get("source_files") or 0),
        "edges": int(summary.get("edges") or len(edges)),
        "unresolved_edges": unresolved,
        "ignored_edges": len([edge for edge in edges if classify_edge(edge) == "ignored"]),
        "failures": failures,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if not failures else EXIT_VERIFY_FAILED


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "report":
            return command_report(args)
        if args.command == "analyze":
            return command_analyze(args)
        if args.command == "verify":
            return command_verify(args)
        parser.error(f"Unknown command: {args.command}")
        return EXIT_INPUT
    except KeyboardInterrupt:
        return EXIT_INTERRUPTED
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"[INPUT ERROR] {exc}", file=sys.stderr)
        return EXIT_INPUT
    except subprocess.TimeoutExpired as exc:
        print(f"[RUN FAILED] command timed out: {exc}", file=sys.stderr)
        return EXIT_RUN_FAILED
    except Exception as exc:
        print(f"[FAILED] {exc}", file=sys.stderr)
        return EXIT_RUN_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
