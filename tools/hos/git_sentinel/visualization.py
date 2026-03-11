#!/usr/bin/env python3
from __future__ import annotations

import itertools
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any

from tools.hos._core.stable_json import write_json

from .config import SentinelConfig
from .git_utils import git_commit_file_sets, git_growth_timeline, git_top_modified_files


JS_IMPORT_RE = re.compile(
    r"(?:from\s+['\"](?P<from>[^'\"]+)['\"]|require\(\s*['\"](?P<req>[^'\"]+)['\"]\s*\))"
)
PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))")


def _module_from_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip("/")
    if not normalized:
        return "."
    return normalized.split("/", 1)[0]


def _resolve_local_import(source_path: str, target: str) -> str:
    source_parent = PurePosixPath(source_path).parent
    candidate = (source_parent / target).as_posix()
    normalized = PurePosixPath(candidate).as_posix()
    return normalized.lstrip("./")


def _dependency_edges_from_scan(config: SentinelConfig, scan_state: dict[str, Any]) -> list[dict[str, Any]]:
    files = scan_state.get("files", [])[: config.max_files_for_dependency_graph]
    edge_counts: dict[tuple[str, str], int] = defaultdict(int)

    for row in files:
        rel_path = str(row.get("path", ""))
        if bool(row.get("binary", False)):
            continue
        ext = str(row.get("extension", "")).lower()
        if ext not in {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
            continue

        source_module = _module_from_path(rel_path)
        abs_path = (config.repo_root / rel_path).resolve()
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for line in text.splitlines():
            js_match = JS_IMPORT_RE.search(line)
            if js_match:
                target = js_match.group("from") or js_match.group("req") or ""
                target = target.strip()
                if target.startswith("."):
                    target_path = _resolve_local_import(rel_path, target)
                    target_module = _module_from_path(target_path)
                    if target_module and source_module and target_module != source_module:
                        edge_counts[(source_module, target_module)] += 1
                continue

            py_match = PY_IMPORT_RE.search(line)
            if py_match:
                imported = py_match.group(1) or py_match.group(2) or ""
                imported = imported.strip()
                if not imported:
                    continue
                target_module = imported.split(".", 1)[0]
                if target_module and source_module and target_module != source_module:
                    edge_counts[(source_module, target_module)] += 1

    edges = [
        {"from": source, "to": target, "weight": weight}
        for (source, target), weight in sorted(edge_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    return edges


def _build_growth_timeline(repo_root: SentinelConfig) -> list[dict[str, Any]]:
    commits = git_growth_timeline(repo_root.repo_root, max_commits=repo_root.max_commits_for_history)
    grouped: dict[str, int] = defaultdict(int)
    for row in commits:
        epoch = int(row.get("epoch", 0))
        month = datetime.fromtimestamp(epoch, tz=UTC).strftime("%Y-%m")
        grouped[month] += 1
    return [{"month": month, "commits": count} for month, count in sorted(grouped.items())]


def _build_module_interaction_graph(config: SentinelConfig) -> list[dict[str, Any]]:
    commits = git_commit_file_sets(config.repo_root, max_commits=config.max_commits_for_history)
    pair_counts: dict[tuple[str, str], int] = defaultdict(int)
    for commit_files in commits:
        modules = sorted({_module_from_path(path) for path in commit_files if path.strip()})
        if len(modules) < 2:
            continue
        for left, right in itertools.combinations(modules, 2):
            pair_counts[(left, right)] += 1
    return [
        {"left": left, "right": right, "weight": weight}
        for (left, right), weight in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def generate_visualization_data(config: SentinelConfig, scan_state: dict[str, Any]) -> dict[str, Any]:
    config.visualization_dir.mkdir(parents=True, exist_ok=True)

    dependency_graph = {
        "nodes": sorted({_module_from_path(row.get("path", "")) for row in scan_state.get("files", [])}),
        "edges": _dependency_edges_from_scan(config, scan_state),
    }
    heatmap = {
        "files": git_top_modified_files(config.repo_root, days=120, limit=500),
    }
    growth_timeline = {
        "timeline": _build_growth_timeline(config),
    }
    module_graph = {
        "edges": _build_module_interaction_graph(config),
    }

    dep_path = (config.visualization_dir / "repository_dependency_graph.json").resolve()
    heatmap_path = (config.visualization_dir / "file_modification_heatmap.json").resolve()
    growth_path = (config.visualization_dir / "repository_growth_timeline.json").resolve()
    module_path = (config.visualization_dir / "module_interaction_graph.json").resolve()

    write_json(dep_path, dependency_graph, indent=2, sort_keys=True)
    write_json(heatmap_path, heatmap, indent=2, sort_keys=True)
    write_json(growth_path, growth_timeline, indent=2, sort_keys=True)
    write_json(module_path, module_graph, indent=2, sort_keys=True)

    return {
        "dependencyGraphPath": dep_path.as_posix(),
        "heatmapPath": heatmap_path.as_posix(),
        "growthTimelinePath": growth_path.as_posix(),
        "moduleGraphPath": module_path.as_posix(),
    }

