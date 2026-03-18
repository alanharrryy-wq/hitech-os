#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools" / "graphviz"
OUTPUT_ROOT = TOOLS_ROOT / "graphs"
MANIFEST_PATH = TOOLS_ROOT / ".graphviz_manifest.json"
CODEOWNERS_PATH = REPO_ROOT / ".github" / "CODEOWNERS"
DEPENDENCIES_POLICY_PATH = REPO_ROOT / "policies" / "dependencies.json"
WORKSPACE_CONFIG_PATH = REPO_ROOT / "pnpm-workspace.yaml"
SCOPE_TOP_RISKS_PATH = OUTPUT_ROOT / "scope_top_risks.json"

FOCUS_PREFIXES = ("apps/", "services/", "packages/", "tools/")
NOISE_PREFIXES = (
    ".agents/",
    ".codex/",
    "_attic/",
    "_reports/",
    "artifacts/",
    "tools/_local/",
    "tools/codex/worktrees/",
    "tools/codex/runs/",
    "tools/codex/_triage/",
    "tools/live-scene-composer/selection-store-inspector-target-wiring-v1/",
    "tools/live-scene-composer/structure-tree-canvas-sync-over-selection-store-v1/",
    "tools/live-scene-composer/mutation-client-bridge-preview-commit-pack-v2-fixed/",
    "tools/live-scene-composer/_local/",
    "docs/knowledge/codex_chats/",
)

WORKSPACE_ROOTS_FALLBACK = ("apps", "services", "packages", "tools")
WORKSPACE_DEP_SECTIONS = (
    "dependencies",
    "devDependencies",
    "peerDependencies",
    "optionalDependencies",
)


@dataclass
class FolderRecord:
    folder: str
    dir_name: str
    active: bool
    file_count: int
    edge_count_total: int
    edge_count_rendered: int
    scope: str
    is_focus: bool
    is_noise: bool
    last_seen_at: str


@dataclass
class CodeownersEntry:
    pattern: str
    owners: list[str]
    regex: re.Pattern[str]


@dataclass
class WorkspaceProject:
    path: str
    package_name: str
    manifest: dict[str, Any]


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def parse_workspace_patterns(path: Path) -> list[str]:
    if not path.exists():
        return []

    patterns: list[str] = []
    in_packages = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if not in_packages:
            if line == "packages:" or line.startswith("packages:"):
                in_packages = True
            continue

        if line.startswith("-"):
            pattern = line[1:].strip().strip("'\"")
            if pattern:
                patterns.append(pattern.replace("\\", "/"))
            continue

        if raw_line and not raw_line.startswith((" ", "\t")):
            break

    return sorted(set(patterns))


def workspace_roots_from_patterns(patterns: list[str]) -> list[str]:
    roots: list[str] = []
    for pattern in patterns:
        normalized = pattern.strip().strip("'\"").replace("\\", "/")
        if not normalized:
            continue
        if normalized.endswith("/*"):
            root = normalized[:-2].rstrip("/")
            if root:
                roots.append(root)
            continue
        if "*" not in normalized:
            roots.append(normalized.rstrip("/"))
            continue
        root = normalized.split("/", 1)[0]
        if root and "*" not in root:
            roots.append(root)
    return sorted(set(item for item in roots if item))


def load_workspace_model() -> dict[str, Any]:
    dependency_policy = load_json(DEPENDENCIES_POLICY_PATH, {})
    policy_patterns = dependency_policy.get("workspace_patterns", [])
    policy_patterns = [
        str(pattern).replace("\\", "/").strip()
        for pattern in policy_patterns
        if isinstance(pattern, str) and str(pattern).strip()
    ]
    policy_patterns = sorted(set(policy_patterns))

    pnpm_patterns = parse_workspace_patterns(WORKSPACE_CONFIG_PATH)
    effective_patterns = policy_patterns if policy_patterns else pnpm_patterns
    policy_roots = dependency_policy.get("workspace_roots", [])
    policy_roots = [str(root).replace("\\", "/").strip() for root in policy_roots if str(root).strip()]
    policy_roots = sorted(set(policy_roots))

    derived_roots = workspace_roots_from_patterns(effective_patterns)
    workspace_roots = policy_roots if policy_roots else derived_roots
    if not workspace_roots:
        workspace_roots = sorted(set(WORKSPACE_ROOTS_FALLBACK))

    only_in_policy = sorted(set(policy_patterns) - set(pnpm_patterns))
    only_in_pnpm = sorted(set(pnpm_patterns) - set(policy_patterns))

    return {
        "dependency_policy": dependency_policy,
        "workspace_roots": workspace_roots,
        "workspace_patterns_effective": effective_patterns,
        "workspace_patterns_policy": policy_patterns,
        "workspace_patterns_pnpm": pnpm_patterns,
        "workspace_pattern_sync": {
            "in_sync": len(only_in_policy) == 0 and len(only_in_pnpm) == 0,
            "only_in_policy": only_in_policy,
            "only_in_pnpm_workspace": only_in_pnpm,
        },
    }


def classify_scope(folder: str) -> str:
    if folder in ("", "."):
        return "root"
    return folder.split("/", 1)[0]


def is_focus_folder(folder: str) -> bool:
    return folder.startswith(FOCUS_PREFIXES)


def is_noise_folder(folder: str) -> bool:
    return folder.startswith(NOISE_PREFIXES)


def normalize_folder_for_codeowners(folder: str) -> str:
    if folder in ("", "."):
        return "/"
    if folder.endswith("/"):
        return folder
    return f"{folder}/"


def codeowners_pattern_to_regex(pattern: str) -> re.Pattern[str] | None:
    normalized = pattern.strip()
    if not normalized:
        return None

    if normalized.endswith("/"):
        normalized = f"{normalized}**"

    anchored = normalized.startswith("/")
    if anchored:
        normalized = normalized[1:]

    escaped = re.escape(normalized)
    escaped = escaped.replace(r"\*\*", "__DOUBLE_STAR__")
    escaped = escaped.replace(r"\*", "__SINGLE_STAR__")
    escaped = escaped.replace(r"\?", "__QMARK__")

    regex_body = escaped.replace("__DOUBLE_STAR__", ".*")
    regex_body = regex_body.replace("__SINGLE_STAR__", "[^/]*")
    regex_body = regex_body.replace("__QMARK__", "[^/]")

    prefix = "^" if anchored else r"(^|.*/)"
    try:
        return re.compile(f"{prefix}{regex_body}$")
    except re.error:
        return None


def parse_codeowners(path: Path) -> list[CodeownersEntry]:
    if not path.exists():
        return []

    entries: list[CodeownersEntry] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for raw_line in lines:
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        parts = [part for part in line.split() if part]
        if len(parts) < 2:
            continue

        regex = codeowners_pattern_to_regex(parts[0])
        if regex is None:
            continue

        entries.append(CodeownersEntry(pattern=parts[0], owners=parts[1:], regex=regex))

    return entries


def match_codeowners(entries: list[CodeownersEntry], relative_path: str) -> list[str]:
    matched: list[str] = []
    for entry in entries:
        if entry.regex.search(relative_path):
            matched = entry.owners
    return matched


def load_records() -> list[FolderRecord]:
    manifest = load_json(MANIFEST_PATH, {"folders": {}})
    records: list[FolderRecord] = []
    folders = manifest.get("folders", {})
    if not isinstance(folders, dict):
        return records

    for folder, entry in folders.items():
        if not isinstance(entry, dict):
            continue
        dir_name = str(entry.get("dir_name", "")).strip()
        if not dir_name:
            continue

        summary_path = OUTPUT_ROOT / dir_name / "summary.json"
        summary = load_json(summary_path, {})

        records.append(
            FolderRecord(
                folder=folder,
                dir_name=dir_name,
                active=bool(entry.get("active", False)),
                file_count=int(summary.get("file_count", 0) or 0),
                edge_count_total=int(summary.get("edge_count_total", 0) or 0),
                edge_count_rendered=int(summary.get("edge_count_rendered", 0) or 0),
                scope=classify_scope(folder),
                is_focus=is_focus_folder(folder),
                is_noise=is_noise_folder(folder),
                last_seen_at=str(entry.get("last_seen_at", "")),
            )
        )

    records.sort(key=lambda item: item.folder)
    return records


def discover_workspace_projects(workspace_roots: list[str]) -> tuple[dict[str, WorkspaceProject], dict[str, str]]:
    projects: dict[str, WorkspaceProject] = {}
    package_name_to_path: dict[str, str] = {}

    for root in workspace_roots:
        root_path = REPO_ROOT / root
        if not root_path.exists() or not root_path.is_dir():
            continue

        for child in root_path.iterdir():
            if not child.is_dir():
                continue
            manifest_path = child / "package.json"
            if not manifest_path.exists():
                continue

            manifest = load_json(manifest_path, {})
            relative_path = child.relative_to(REPO_ROOT).as_posix()
            package_name = str(manifest.get("name") or relative_path)
            projects[relative_path] = WorkspaceProject(
                path=relative_path,
                package_name=package_name,
                manifest=manifest,
            )
            package_name_to_path[package_name] = relative_path

    return projects, package_name_to_path


def build_workspace_graph(
    projects: dict[str, WorkspaceProject],
    package_name_to_path: dict[str, str],
) -> tuple[dict[str, set[str]], dict[str, set[str]], list[dict[str, str]]]:
    forward: dict[str, set[str]] = {project_path: set() for project_path in projects}
    reverse: dict[str, set[str]] = {project_path: set() for project_path in projects}
    edges: list[dict[str, str]] = []

    for project_path, project in projects.items():
        for section in WORKSPACE_DEP_SECTIONS:
            deps = project.manifest.get(section, {})
            if not isinstance(deps, dict):
                continue

            for dep_name, dep_version in deps.items():
                if not isinstance(dep_version, str) or not dep_version.startswith("workspace:"):
                    continue
                target_path = package_name_to_path.get(str(dep_name))
                if not target_path or target_path == project_path:
                    continue

                if target_path not in forward[project_path]:
                    forward[project_path].add(target_path)
                    reverse[target_path].add(project_path)
                    edges.append({"from": project_path, "to": target_path})

    edges.sort(key=lambda row: (row["from"], row["to"]))
    return forward, reverse, edges


def collect_workspace_cycles(forward: dict[str, set[str]]) -> list[list[str]]:
    index_map: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    current_index = 0
    cycles: list[list[str]] = []

    def strong_connect(node: str) -> None:
        nonlocal current_index
        index_map[node] = current_index
        lowlink[node] = current_index
        current_index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in forward.get(node, set()):
            if neighbor not in index_map:
                strong_connect(neighbor)
                lowlink[node] = min(lowlink[node], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node] = min(lowlink[node], index_map[neighbor])

        if lowlink[node] == index_map[node]:
            scc: list[str] = []
            while stack:
                current = stack.pop()
                on_stack.discard(current)
                scc.append(current)
                if current == node:
                    break

            has_self_loop = len(scc) == 1 and scc[0] in forward.get(scc[0], set())
            if len(scc) > 1 or has_self_loop:
                cycles.append(sorted(scc))

    for node in sorted(forward.keys()):
        if node not in index_map:
            strong_connect(node)

    cycles.sort(key=lambda group: " -> ".join(group))
    return cycles


def summarize_hubs(
    forward: dict[str, set[str]],
    reverse: dict[str, set[str]],
    limit: int = 12,
) -> tuple[list[dict[str, int | str]], list[dict[str, int | str]]]:
    rows: list[dict[str, int | str]] = []
    for node in sorted(forward.keys()):
        fan_out = len(forward.get(node, set()))
        fan_in = len(reverse.get(node, set()))
        rows.append(
            {
                "project": node,
                "fan_in": fan_in,
                "fan_out": fan_out,
                "total_degree": fan_in + fan_out,
            }
        )

    fan_in = sorted(rows, key=lambda row: (-int(row["fan_in"]), str(row["project"])))[:limit]
    fan_out = sorted(rows, key=lambda row: (-int(row["fan_out"]), str(row["project"])))[:limit]
    return fan_in, fan_out


def summarize_cross_boundary_edges(
    edges: list[dict[str, str]],
    boundary_model: dict[str, list[str]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    cross_edges: list[dict[str, str]] = []
    boundary_violations: list[dict[str, Any]] = []
    for edge in edges:
        from_root = edge["from"].split("/", 1)[0]
        to_root = edge["to"].split("/", 1)[0]
        if from_root == to_root:
            continue
        cross_entry = (
            {
                "from": edge["from"],
                "to": edge["to"],
                "from_root": from_root,
                "to_root": to_root,
            }
        )
        cross_edges.append(cross_entry)

        allowed_targets = boundary_model.get(from_root, [])
        if allowed_targets and to_root not in allowed_targets:
            boundary_violations.append(
                {
                    **cross_entry,
                    "allowed_roots": allowed_targets,
                }
            )

    cross_edges.sort(key=lambda row: (row["from"], row["to"]))
    boundary_violations.sort(key=lambda row: (str(row["from"]), str(row["to"])))
    return cross_edges, boundary_violations


def compute_folder_risk_score(record: FolderRecord, owners: list[str]) -> int:
    score = record.edge_count_total * 4 + record.file_count
    if record.scope in {"packages", "services"}:
        score += 4
    if "/api/" in record.folder or "/contracts/" in record.folder:
        score += 6
    if "/tests" in record.folder or "/__tests__/" in record.folder:
        score += 2
    if not owners:
        score += 8
    return score


def aggregate(records: list[FolderRecord]) -> dict[str, Any]:
    workspace_model = load_workspace_model()
    dependency_policy = workspace_model.get("dependency_policy", {})
    boundary_model = dependency_policy.get("boundary_model", {})
    if not isinstance(boundary_model, dict):
        boundary_model = {}

    active = [record for record in records if record.active]
    focus = [record for record in active if record.is_focus]
    focus_clean = [record for record in focus if not record.is_noise]
    noise = [record for record in active if record.is_noise]

    scope_stats: dict[str, dict[str, int]] = {}
    for record in active:
        bucket = scope_stats.setdefault(
            record.scope,
            {"folder_count": 0, "file_count": 0, "edge_count_total": 0, "edge_count_rendered": 0},
        )
        bucket["folder_count"] += 1
        bucket["file_count"] += record.file_count
        bucket["edge_count_total"] += record.edge_count_total
        bucket["edge_count_rendered"] += record.edge_count_rendered

    codeowners_entries = parse_codeowners(CODEOWNERS_PATH)
    owner_set: set[str] = set()
    for entry in codeowners_entries:
        owner_set.update(entry.owners)

    focus_owner_map: dict[str, list[str]] = {}
    for record in focus_clean:
        owners = match_codeowners(codeowners_entries, normalize_folder_for_codeowners(record.folder))
        focus_owner_map[record.folder] = owners

    focus_without_owner = sorted(
        [folder for folder, owners in focus_owner_map.items() if not owners]
    )

    top_focus = sorted(
        focus_clean,
        key=lambda item: (-item.edge_count_total, -item.file_count, item.folder),
    )[:60]

    projects, package_name_to_path = discover_workspace_projects(
        workspace_model.get("workspace_roots", list(WORKSPACE_ROOTS_FALLBACK))
    )
    forward, reverse, dependency_edges = build_workspace_graph(projects, package_name_to_path)
    cycles = collect_workspace_cycles(forward)
    fan_in_hubs, fan_out_hubs = summarize_hubs(forward, reverse)
    cross_boundary_edges, boundary_violations = summarize_cross_boundary_edges(
        dependency_edges,
        {str(key): [str(value) for value in values] for key, values in boundary_model.items() if isinstance(values, list)},
    )

    workspace_graph = {
        "project_count": len(projects),
        "edge_count": len(dependency_edges),
        "cycle_count": len(cycles),
        "cycles": cycles,
        "fan_in_hubs": fan_in_hubs,
        "fan_out_hubs": fan_out_hubs,
        "cross_boundary_edge_count": len(cross_boundary_edges),
        "cross_boundary_edges_sample": cross_boundary_edges[:100],
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations_sample": boundary_violations[:100],
    }

    ownership_overlay = {
        "codeowners_path": str(CODEOWNERS_PATH),
        "owner_count": len(owner_set),
        "single_owner_mode": len(owner_set) == 1,
        "focus_clean_folder_count": len(focus_clean),
        "focus_folders_with_owner_count": len(focus_clean) - len(focus_without_owner),
        "focus_folders_without_owner_count": len(focus_without_owner),
        "focus_folders_without_owner_sample": focus_without_owner[:120],
    }

    focus_hotspots: list[dict[str, Any]] = []
    scored_focus: list[dict[str, Any]] = []
    for record in focus_clean:
        owners = focus_owner_map.get(record.folder, [])
        risk_score = compute_folder_risk_score(record, owners)
        scored_focus.append(
            {
                "folder": record.folder,
                "dir_name": record.dir_name,
                "scope": record.scope,
                "file_count": record.file_count,
                "edge_count_total": record.edge_count_total,
                "owners": owners,
                "risk_score": risk_score,
            }
        )

    scored_focus.sort(
        key=lambda row: (
            -int(row["risk_score"]),
            -int(row["edge_count_total"]),
            str(row["folder"]),
        )
    )
    priority_focus = [row for row in scored_focus if int(row["risk_score"]) >= 25 or int(row["edge_count_total"]) >= 6]

    for record in top_focus:
        focus_hotspots.append(
            {
                "folder": record.folder,
                "dir_name": record.dir_name,
                "edge_count_total": record.edge_count_total,
                "file_count": record.file_count,
                "scope": record.scope,
                "owners": focus_owner_map.get(record.folder, []),
                "risk_score": compute_folder_risk_score(record, focus_owner_map.get(record.folder, [])),
            }
        )

    top_risks = scored_focus[:80]
    noise_ratio = 0.0 if len(active) == 0 else round(len(noise) / len(active), 4)

    return {
        "schema_version": 3,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "paths": {
            "repo_root": str(REPO_ROOT),
            "manifest_path": str(MANIFEST_PATH),
            "output_root": str(OUTPUT_ROOT),
            "codeowners_path": str(CODEOWNERS_PATH),
            "dependencies_policy_path": str(DEPENDENCIES_POLICY_PATH),
            "workspace_config_path": str(WORKSPACE_CONFIG_PATH),
            "top_risk_output_path": str(SCOPE_TOP_RISKS_PATH),
        },
        "workspace_model": {
            "roots": workspace_model.get("workspace_roots", []),
            "effective_patterns": workspace_model.get("workspace_patterns_effective", []),
            "policy_patterns": workspace_model.get("workspace_patterns_policy", []),
            "pnpm_workspace_patterns": workspace_model.get("workspace_patterns_pnpm", []),
            "pattern_sync": workspace_model.get("workspace_pattern_sync", {}),
        },
        "counts": {
            "total_folders_manifest": len(records),
            "active_folders": len(active),
            "focus_active_folders": len(focus),
            "focus_clean_active_folders": len(focus_clean),
            "priority_focus_folders": len(priority_focus),
            "noise_active_folders": len(noise),
            "historical_folders": max(0, len(records) - len(active)),
        },
        "risk_overview": {
            "noise_ratio": noise_ratio,
            "top_hotspot_count": len(top_risks),
            "priority_focus_folders": len(priority_focus),
        },
        "scope_stats": dict(sorted(scope_stats.items(), key=lambda item: (-item[1]["folder_count"], item[0]))),
        "blast_radius_hotspots": focus_hotspots,
        "top_risks": top_risks,
        "workspace_dependency_health": workspace_graph,
        "ownership_overlay": ownership_overlay,
    }


def render_index(records: list[FolderRecord], summary: dict[str, Any]) -> str:
    active = [record for record in records if record.active]
    focus_clean = [record for record in active if record.is_focus and not record.is_noise]
    noise = [record for record in active if record.is_noise]

    codeowners_entries = parse_codeowners(CODEOWNERS_PATH)
    owner_map: dict[str, list[str]] = {}
    for record in focus_clean:
        owner_map[record.folder] = match_codeowners(
            codeowners_entries, normalize_folder_for_codeowners(record.folder)
        )

    folder_to_record = {record.folder: record for record in focus_clean}
    top_risks = summary.get("top_risks", [])
    if not isinstance(top_risks, list):
        top_risks = []

    ranked_rows: list[dict[str, Any]] = []
    for row in top_risks:
        if not isinstance(row, dict):
            continue
        folder = str(row.get("folder", ""))
        record = folder_to_record.get(folder)
        if record is None:
            continue
        ranked_rows.append(
            {
                "folder": folder,
                "scope": record.scope,
                "file_count": int(row.get("file_count", record.file_count)),
                "edge_count_total": int(row.get("edge_count_total", record.edge_count_total)),
                "dir_name": str(row.get("dir_name", record.dir_name)),
                "risk_score": int(row.get("risk_score", compute_folder_risk_score(record, owner_map.get(folder, [])))),
                "owners": owner_map.get(folder, []),
            }
        )

    if not ranked_rows:
        for record in sorted(
            focus_clean, key=lambda item: (-item.edge_count_total, -item.file_count, item.folder)
        )[:80]:
            ranked_rows.append(
                {
                    "folder": record.folder,
                    "scope": record.scope,
                    "file_count": record.file_count,
                    "edge_count_total": record.edge_count_total,
                    "dir_name": record.dir_name,
                    "risk_score": compute_folder_risk_score(record, owner_map.get(record.folder, [])),
                    "owners": owner_map.get(record.folder, []),
                }
            )

    top_risk_folders = {str(row.get("folder", "")) for row in ranked_rows}
    remaining_focus = sorted(
        [record for record in focus_clean if record.folder not in top_risk_folders],
        key=lambda item: (item.scope, -item.edge_count_total, item.folder),
    )

    def render_ranked_row(row: dict[str, Any]) -> str:
        folder = html.escape(str(row.get("folder", "")))
        dir_name = html.escape(str(row.get("dir_name", "")))
        owners = row.get("owners", [])
        if isinstance(owners, list):
            owners_text = ", ".join(html.escape(str(owner)) for owner in owners) if owners else "(unowned)"
        else:
            owners_text = "(unowned)"
        return (
            "<tr>"
            f"<td>{folder}</td>"
            f"<td>{html.escape(str(row.get('scope', '')))}</td>"
            f"<td>{int(row.get('file_count', 0))}</td>"
            f"<td>{int(row.get('edge_count_total', 0))}</td>"
            f"<td>{int(row.get('risk_score', 0))}</td>"
            f"<td>{owners_text}</td>"
            f"<td><a href='./{dir_name}/graph.svg'>graph.svg</a></td>"
            f"<td><a href='./{dir_name}/summary.json'>summary.json</a></td>"
            "</tr>"
        )

    top_rows = "\n".join(render_ranked_row(row) for row in ranked_rows[:120])
    remaining_rows = "\n".join(
        f"<li>{html.escape(record.folder)} <span class='muted'>(scope={html.escape(record.scope)}, edges={record.edge_count_total}, files={record.file_count})</span></li>"
        for record in remaining_focus
    )
    noise_rows = "\n".join(
        f"<li>{html.escape(record.folder)} <span class='muted'>(edges={record.edge_count_total}, files={record.file_count})</span></li>"
        for record in sorted(noise, key=lambda item: item.folder)
    )

    counts = summary.get("counts", {})
    workspace = summary.get("workspace_dependency_health", {})
    ownership = summary.get("ownership_overlay", {})
    workspace_model = summary.get("workspace_model", {})
    risk_overview = summary.get("risk_overview", {})

    fan_in_rows = "\n".join(
        f"<li>{html.escape(str(row.get('project', '')))} <span class='muted'>(fan-in={int(row.get('fan_in', 0))}, fan-out={int(row.get('fan_out', 0))})</span></li>"
        for row in workspace.get("fan_in_hubs", [])[:10]
    )
    fan_out_rows = "\n".join(
        f"<li>{html.escape(str(row.get('project', '')))} <span class='muted'>(fan-out={int(row.get('fan_out', 0))}, fan-in={int(row.get('fan_in', 0))})</span></li>"
        for row in workspace.get("fan_out_hubs", [])[:10]
    )

    cycle_rows = workspace.get("cycles", [])
    cycle_html = "\n".join(
        f"<li>{html.escape(' -> '.join(str(node) for node in cycle))}</li>" for cycle in cycle_rows
    ) or "<li class='muted'>No workspace cycles detected.</li>"
    boundary_violation_rows = workspace.get("boundary_violations_sample", [])
    boundary_violation_html = "\n".join(
        f"<li>{html.escape(str(row.get('from', '')))} -> {html.escape(str(row.get('to', '')))} <span class='muted'>(allowed: {html.escape(', '.join(str(item) for item in row.get('allowed_roots', [])))})</span></li>"
        for row in boundary_violation_rows[:30]
    ) or "<li class='muted'>No boundary violations in workspace manifest graph.</li>"

    unowned_focus = ownership.get("focus_folders_without_owner_sample", [])
    unowned_html = "\n".join(
        f"<li>{html.escape(str(folder))}</li>" for folder in unowned_focus[:40]
    ) or "<li class='muted'>No unowned focus folders in current summary.</li>"

    workspace_pattern_sync = workspace_model.get("pattern_sync", {})
    pattern_drift = (
        len(workspace_pattern_sync.get("only_in_policy", []))
        + len(workspace_pattern_sync.get("only_in_pnpm_workspace", []))
    )
    pattern_drift_text = "none" if pattern_drift == 0 else str(pattern_drift)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>HITECH Graphviz Scoped Index</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: #0b1320; color: #e5eefb; }}
  a {{ color: #7dd3fc; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .panel {{ background: #132238; border: 1px solid #223a5a; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border-bottom: 1px solid #223a5a; padding: 8px; text-align: left; vertical-align: top; }}
  th {{ color: #9fc5db; }}
  .muted {{ color: #88a7c2; }}
  details {{ margin-top: 10px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
</style>
</head>
<body>
  <div class="panel">
    <h1>HITECH Graphviz Scoped Index</h1>
    <p class="muted">Additive index over existing Graphviz outputs. Historical folders are preserved.</p>
    <p>
      active={counts.get("active_folders", 0)} |
      focus_clean={counts.get("focus_clean_active_folders", 0)} |
      priority_focus={counts.get("priority_focus_folders", 0)} |
      noise={counts.get("noise_active_folders", 0)} |
      historical={counts.get("historical_folders", 0)}
    </p>
    <p>
      noise_ratio={risk_overview.get("noise_ratio", 0)} |
      top_hotspots={risk_overview.get("top_hotspot_count", 0)} |
      workspace_pattern_drift={pattern_drift_text}
    </p>
  </div>
  <div class="panel">
    <h2>Top Risk Focus Folders (apps/services/packages/tools)</h2>
    <table>
      <thead>
        <tr>
          <th>Folder</th>
          <th>Scope</th>
          <th>Files</th>
          <th>Edges</th>
          <th>Risk</th>
          <th>Owners</th>
          <th>Graph</th>
          <th>Summary</th>
        </tr>
      </thead>
      <tbody>
        {top_rows}
      </tbody>
    </table>
    <details>
      <summary>Show remaining focus-clean folders ({len(remaining_focus)})</summary>
      <ul>
        {remaining_rows}
      </ul>
    </details>
  </div>
  <div class="panel">
    <h2>Workspace Dependency Health</h2>
    <p>
      projects={workspace.get("project_count", 0)} |
      edges={workspace.get("edge_count", 0)} |
      cycles={workspace.get("cycle_count", 0)} |
      cross-boundary edges={workspace.get("cross_boundary_edge_count", 0)} |
      boundary violations={workspace.get("boundary_violation_count", 0)}
    </p>
    <div class="grid">
      <div>
        <h3>Cycles</h3>
        <ul>{cycle_html}</ul>
      </div>
      <div>
        <h3>Top Fan-In Hubs</h3>
        <ul>{fan_in_rows}</ul>
      </div>
      <div>
        <h3>Top Fan-Out Hubs</h3>
        <ul>{fan_out_rows}</ul>
      </div>
      <div>
        <h3>Boundary Violations</h3>
        <ul>{boundary_violation_html}</ul>
      </div>
    </div>
  </div>
  <div class="panel">
    <h2>Ownership Overlay</h2>
    <p>
      owner_count={ownership.get("owner_count", 0)} |
      single_owner_mode={ownership.get("single_owner_mode", False)} |
      focus_unowned={ownership.get("focus_folders_without_owner_count", 0)}
    </p>
    <details>
      <summary>Show sample focus folders without owner mapping</summary>
      <ul>
        {unowned_html}
      </ul>
    </details>
  </div>
  <div class="panel">
    <h2>Noise/Operational Folders</h2>
    <details>
      <summary>Show {len(noise)} active noise folders</summary>
      <ul>
        {noise_rows}
      </ul>
    </details>
  </div>
</body>
</html>
"""


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    records = load_records()
    summary = aggregate(records)

    summary_path = OUTPUT_ROOT / "scope_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    top_risk_payload = {
        "schema_version": 1,
        "generated_at_utc": summary.get("generated_at_utc"),
        "top_risks": summary.get("top_risks", []),
    }
    SCOPE_TOP_RISKS_PATH.write_text(
        json.dumps(top_risk_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    index_path = OUTPUT_ROOT / "index.scoped.html"
    index_path.write_text(render_index(records, summary), encoding="utf-8")

    print(f"[graphviz_scope_index] wrote {summary_path}")
    print(f"[graphviz_scope_index] wrote {SCOPE_TOP_RISKS_PATH}")
    print(f"[graphviz_scope_index] wrote {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
