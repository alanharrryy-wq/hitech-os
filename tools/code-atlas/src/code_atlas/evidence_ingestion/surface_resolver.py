# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from code_atlas.core.project_profile import load_project_profile

GENERIC_ROLE_RULES = [
    ("Database", [r"(?:^|[\\/])(?:prisma|migrations?|database|db|schema|sql)(?:[\\/]|$)", r"\.prisma$", r"\.sql$"]),
    ("Docs", [r"(?:^|[\\/])docs?(?:[\\/]|$)", r"\.mdx?$", r"runbook", r"manual"]),
    ("Tests/Verifiers", [r"(?:^|[\\/])(?:tests?|specs?|e2e|verifiers?)(?:[\\/]|$)", r"(?:test|verify|smoke|spec)"] ),
    ("Tooling", [r"(?:^|[\\/])(?:tools|scripts|bin)(?:[\\/]|$)"]),
    ("Shared", [r"(?:^|[\\/])(?:shared|packages|libs?)(?:[\\/]|$)"]),
    ("Configuration", [r"(?:^|[\\/])(?:config|configuration)(?:[\\/]|$)", r"(?:^|[\\/])\.[A-Za-z0-9_-]+$"]),
    ("Visual/UI", [r"(?:^|[\\/])(?:styles?|ui|components?|themes?)(?:[\\/]|$)", r"\.(?:css|scss|sass|less)$"]),
]


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {} if default is None else default


def _profile_role_rules(repo_root: Path) -> list[tuple[str, list[str]]]:
    profile = load_project_profile()
    rules: list[tuple[str, list[str]]] = []
    for app in profile.apps:
        raw = str(app.root or ".").replace("\\", "/").strip("/")
        if not raw or raw == ".":
            continue
        rules.append((str(app.label or app.id), [rf"(?:^|[\\/]){re.escape(raw)}(?:[\\/]|$)"]))
    extra = profile.metadata.get("surfaceRoleRules", [])
    if isinstance(extra, list):
        for row in extra:
            if not isinstance(row, dict):
                continue
            role = str(row.get("role") or "").strip()
            patterns = row.get("patterns") or []
            if role and isinstance(patterns, list) and all(isinstance(item, str) for item in patterns):
                rules.append((role, list(patterns)))
    return rules


def role_rules(repo_root: Path) -> list[tuple[str, list[str]]]:
    return [*_profile_role_rules(repo_root), *GENERIC_ROLE_RULES]


def classify_path(path: str, repo_root: Path | None = None) -> str:
    normalized = str(path).replace("\\", "/")
    rules = role_rules(repo_root or Path.cwd())
    for role, patterns in rules:
        for pattern in patterns:
            if re.search(pattern, normalized, re.I):
                return role
    return "Unknown"


def collect_path_strings(obj: Any, out: List[str], limit: int = 20000):
    if len(out) >= limit:
        return
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, str) and ("/" in value or "\\" in value or "." in value):
                out.append(value)
            elif isinstance(value, (dict, list)):
                collect_path_strings(value, out, limit)
    elif isinstance(obj, list):
        for value in obj:
            collect_path_strings(value, out, limit)
    elif isinstance(obj, str) and ("/" in obj or "\\" in obj):
        out.append(obj)


def _scan_roots(repo_root: Path) -> list[Path]:
    profile = load_project_profile()
    roots: list[Path] = []
    for app in profile.apps:
        candidate = (repo_root / str(app.root or ".")).resolve()
        try:
            candidate.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if candidate.exists():
            roots.append(candidate)
    if roots:
        return roots
    return [repo_root]


def build_surface_aware_index(repo_root: Path, registers_dir: Path) -> Dict[str, Any]:
    repo_root = repo_root.resolve()
    sources = [load_json(registers_dir / name, {}) for name in [
        "PATH_ROLE_INDEX.json", "ATLAS_COVERAGE_GAP_REGISTER.json",
        "IMPORTANT_ENTRYPOINTS_REGISTER.json", "TREE_INVENTORY.json",
    ]]
    strings: list[str] = []
    for source in sources:
        collect_path_strings(source, strings)

    skip = {".git", "node_modules", ".next", "dist", "build", ".cache", ".turbo", "__pycache__"}
    for base in _scan_roots(repo_root):
        for path in base.rglob("*"):
            if len(strings) >= 35000:
                break
            if any(part in skip for part in path.parts) or not path.is_file():
                continue
            try:
                strings.append(path.resolve().relative_to(repo_root).as_posix())
            except Exception:
                continue

    seen: set[str] = set()
    unique: list[str] = []
    for value in strings:
        value = str(value).strip().replace("\\", "/")
        if not value or len(value) > 400 or value in seen:
            continue
        seen.add(value)
        unique.append(value)

    counts: dict[str, int] = {}
    entries: list[dict[str, Any]] = []
    for value in unique:
        role = classify_path(value, repo_root)
        counts[role] = counts.get(role, 0) + 1
        candidate = (repo_root / value).resolve() if not Path(value).is_absolute() else None
        exists = bool(candidate and candidate.exists())
        entries.append({"path": value, "surfaceRole": role, "exists": exists})

    coverage = sources[1]
    semantic_missing = 0
    if isinstance(coverage, dict):
        for key in ["missing_atlas_nodes", "missingAtlasNodes", "missing_nodes"]:
            if isinstance(coverage.get(key), int):
                semantic_missing = int(coverage[key])
                break

    rules = role_rules(repo_root)
    return {
        "status": "PASS_SURFACE_AWARE_ATLAS_NODE_RESOLVER_BUILT",
        "resolverVersion": "code_atlas.surface.v2",
        "profileId": load_project_profile().profile_id,
        "totalResolvedCandidates": len(entries),
        "roleCounts": counts,
        "coverageComplete": False if semantic_missing else None,
        "semanticMissingCountFromPriorRegister": semantic_missing,
        "unknownCount": counts.get("Unknown", 0),
        "unknownSample": [entry for entry in entries if entry["surfaceRole"] == "Unknown"][:500],
        "resolverRules": [{"role": role, "patterns": patterns} for role, patterns in rules],
        "doesProve": [
            "paths are classified by explicit profile application or generic workspace role",
            "coverage gaps are no longer ownerless strings",
            "semantic completeness remains separately tracked",
        ],
        "doesNotProve": [
            "complete semantic Atlas coverage",
            "runtime/live certification",
            "that every documentation mention is a live node",
        ],
        "nextGate": "USE_RESOLVER_TO_REDUCE_MISSING_ATLAS_NODES_BY_OWNER",
        "productionCertified": False,
    }
