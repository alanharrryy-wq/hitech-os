from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .common import REPO_ROOT, ensure_dir

EXPECTED_FACTORY_ROLES: tuple[str, ...] = (
    "A_core",
    "B_tooling",
    "C_features",
    "D_validation",
    "Z_aggregator",
)

LEGACY_ROLE_MAP: dict[str, str] = {
    "A_core": "A_worker",
    "B_tooling": "B_worker",
    "C_features": "C_worker",
    "D_validation": "D_worker",
    "Z_aggregator": "Z_integrator",
}

WORKER_TO_FACTORY_ROLE: dict[str, str] = {
    "A_core": "A_core",
    "A_worker": "A_core",
    "B_tooling": "B_tooling",
    "B_worker": "B_tooling",
    "C_features": "C_features",
    "C_worker": "C_features",
    "D_validation": "D_validation",
    "D_worker": "D_validation",
    "Z_aggregator": "Z_aggregator",
    "Z_integrator": "Z_aggregator",
}

SKILLS_ROOT_CANDIDATES: tuple[str, ...] = (
    ".codex/skills",
    ".agents/skills",
)
DEFAULT_SKILLS_ROOT = SKILLS_ROOT_CANDIDATES[0]


def find_repo_root(start: Path | None = None) -> Path:
    probe = (start or Path.cwd()).resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / ".git").exists():
            return candidate
    fallback = REPO_ROOT.resolve()
    if (fallback / ".git").exists():
        return fallback
    raise FileNotFoundError("Unable to locate repo root (.git) from current working directory.")


def _sort_key(path: Path, root: Path) -> tuple[str, str]:
    rel = path.relative_to(root).as_posix()
    return (rel.lower(), rel)


def _scan_role_skills(*, repo_root: Path, role_root: Path) -> list[dict[str, str]]:
    if not role_root.exists() or not role_root.is_dir():
        return []
    docs = sorted(role_root.rglob("SKILL.md"), key=lambda item: _sort_key(item, repo_root))
    entries: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for doc in docs:
        skill_dir = doc.parent
        name = skill_dir.name
        path_value = skill_dir.relative_to(repo_root).as_posix()
        doc_value = doc.relative_to(repo_root).as_posix()
        key = (name.lower(), doc_value.lower())
        if key in seen:
            continue
        seen.add(key)
        entries.append(
            {
                "name": name,
                "path": path_value,
                "doc_path": doc_value,
            }
        )
    entries.sort(key=lambda row: (str(row["name"]).lower(), str(row["name"]), str(row["doc_path"]).lower(), str(row["doc_path"])))
    return entries


def factory_role_for_worker(worker_id: str) -> str:
    worker = str(worker_id).strip()
    return WORKER_TO_FACTORY_ROLE.get(worker, worker)


def resolve_skills_root(*, repo_root: Path | None = None) -> dict[str, str]:
    root = (repo_root or find_repo_root()).resolve()
    for rel in SKILLS_ROOT_CANDIDATES:
        candidate = root / Path(rel)
        if candidate.exists() and candidate.is_dir():
            return {"relative": rel, "path": candidate.as_posix()}
    fallback = root / Path(DEFAULT_SKILLS_ROOT)
    return {"relative": DEFAULT_SKILLS_ROOT, "path": fallback.as_posix()}


def build_skills_index(*, repo_root: Path | None = None) -> dict[str, Any]:
    root = (repo_root or find_repo_root()).resolve()
    skills_root_info = resolve_skills_root(repo_root=root)
    skills_root = Path(str(skills_root_info["path"]))
    skills_root_rel = str(skills_root_info["relative"])
    available_roles = {entry.name for entry in skills_root.iterdir() if entry.is_dir()} if skills_root.exists() else set()

    roles: dict[str, list[dict[str, str]]] = {}
    role_sources: dict[str, str] = {}
    for role in EXPECTED_FACTORY_ROLES:
        chosen_source = ""
        if role in available_roles:
            chosen_source = role
        else:
            legacy = LEGACY_ROLE_MAP.get(role, "")
            if legacy in available_roles:
                chosen_source = legacy
        role_sources[role] = chosen_source
        if not chosen_source:
            roles[role] = []
            continue
        roles[role] = _scan_role_skills(repo_root=root, role_root=skills_root / chosen_source)

    return {
        "version": 1,
        "skills_root": skills_root_rel,
        "skills_root_candidates": list(SKILLS_ROOT_CANDIDATES),
        "roles": roles,
        "role_sources": role_sources,
    }


def cache_paths(*, repo_root: Path | None = None) -> dict[str, Path]:
    root = (repo_root or find_repo_root()).resolve()
    cache_dir = root / "tools" / "codex" / "_cache"
    return {
        "cache_dir": cache_dir,
        "index_json": cache_dir / "skills_index.json",
        "index_md": cache_dir / "skills_index.md",
    }


def render_skills_index_markdown(index: Mapping[str, Any]) -> str:
    lines: list[str] = [
        "# Skills Index",
        "",
        f"- version: {int(index.get('version', 1))}",
        f"- skills_root: `{str(index.get('skills_root', DEFAULT_SKILLS_ROOT))}`",
        "",
    ]
    roles = index.get("roles", {})
    role_sources = index.get("role_sources", {})
    for role in EXPECTED_FACTORY_ROLES:
        source_role = str(role_sources.get(role, "")).strip()
        skills = list(roles.get(role, [])) if isinstance(roles, Mapping) else []
        lines.append(f"## {role}")
        lines.append("")
        lines.append(f"- source_role: `{source_role or 'missing'}`")
        lines.append(f"- skills_count: {len(skills)}")
        if not skills:
            lines.append("- (no skills discovered)")
            lines.append("")
            continue
        for row in skills:
            name = str(row.get("name", "")).strip()
            doc_path = str(row.get("doc_path", "")).strip()
            lines.append(f"- `{name}` -> `{doc_path}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_skills_index(
    index: Mapping[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, str]:
    root = (repo_root or find_repo_root()).resolve()
    paths = cache_paths(repo_root=root)
    ensure_dir(paths["cache_dir"])
    paths["index_json"].write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    paths["index_md"].write_text(render_skills_index_markdown(index), encoding="utf-8", newline="\n")
    return {
        "index_json": paths["index_json"].as_posix(),
        "index_md": paths["index_md"].as_posix(),
    }


def generate_and_write_skills_index(*, repo_root: Path | None = None) -> dict[str, Any]:
    root = (repo_root or find_repo_root()).resolve()
    index = build_skills_index(repo_root=root)
    written = write_skills_index(index, repo_root=root)
    role_counts = {
        role: len(index.get("roles", {}).get(role, []))
        for role in EXPECTED_FACTORY_ROLES
    }
    return {
        "status": "PASS",
        "repo_root": root.as_posix(),
        "skills_root": str(index.get("skills_root", DEFAULT_SKILLS_ROOT)),
        "role_counts": role_counts,
        "index": index,
        **written,
    }
