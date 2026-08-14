from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from code_atlas.core.project_profile import AppProfile, ProjectProfile, load_project_profile


SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".md", ".yaml", ".yml", ".toml", ".sql", ".prisma", ".css", ".html"}
ROUTE_FILENAMES = {"page.tsx", "page.ts", "page.jsx", "page.js", "route.ts", "route.js", "route.mjs", "layout.tsx", "layout.ts", "layout.jsx", "layout.js"}


@dataclass(frozen=True)
class SurfaceSpec:
    surface_id: str
    label: str
    root: str
    kind: str = "app"


@dataclass(frozen=True)
class OperationalRuntimeProfile:
    profile_id: str
    project_name: str
    repo_root: Path
    output_root: Path
    result_root: Path
    scan_roots: tuple[Path, ...]
    evidence_roots: tuple[Path, ...]
    support_resolver_roots: tuple[Path, ...]
    surfaces: tuple[SurfaceSpec, ...]
    support_resolver_enabled: bool
    metadata: dict[str, Any]


def _is_unresolved(value: str) -> bool:
    return "${" in value or "%" in value and value.count("%") >= 2


def _path_from(value: str | Path, *, base: Path) -> Path:
    text = os.path.expandvars(os.path.expanduser(str(value or ".")))
    path = Path(text)
    return (path if path.is_absolute() else base / path).resolve()


def _paths(values: Any, *, base: Path) -> tuple[Path, ...]:
    if not isinstance(values, (list, tuple)):
        values = [] if values in (None, "") else [values]
    out: list[Path] = []
    for raw in values:
        text = str(raw or "").strip()
        if not text or _is_unresolved(text):
            continue
        path = _path_from(text, base=base)
        if path not in out:
            out.append(path)
    return tuple(out)


def _discover_surfaces(repo_root: Path) -> tuple[SurfaceSpec, ...]:
    candidates: list[SurfaceSpec] = []
    for parent_name in ("apps", "services", "packages", "products"):
        parent = repo_root / parent_name
        if not parent.is_dir():
            continue
        for child in sorted((p for p in parent.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
            candidates.append(SurfaceSpec(f"{parent_name}.{child.name}", child.name, child.relative_to(repo_root).as_posix(), parent_name[:-1] or "app"))
    if not candidates:
        candidates.append(SurfaceSpec("repository", repo_root.name or "Repository", ".", "repository"))
    return tuple(candidates)


def _profile_surfaces(profile: ProjectProfile, repo_root: Path) -> tuple[SurfaceSpec, ...]:
    if not profile.apps:
        return _discover_surfaces(repo_root)
    out: list[SurfaceSpec] = []
    for app in profile.apps:
        root = str(app.root or ".").strip() or "."
        out.append(SurfaceSpec(str(app.id or "app"), str(app.label or app.id or "App"), root, str(app.kind or "app")))
    return tuple(out)


def resolve_runtime_profile(
    repo_root: str | Path,
    output_dir: str | Path,
    result_root: str | Path | None = None,
    *,
    profile_path: str | Path | None = None,
) -> OperationalRuntimeProfile:
    repo = Path(repo_root).expanduser().resolve()
    out = Path(output_dir).expanduser().resolve()
    profile = load_project_profile(profile_path)
    metadata = dict(profile.metadata or {})

    configured_output = str(profile.output_root or "").strip()
    if configured_output and not _is_unresolved(configured_output) and configured_output not in {".", "./code-atlas-out"}:
        profile_output = _path_from(configured_output, base=repo)
    else:
        profile_output = out

    if result_root is not None:
        results = _path_from(result_root, base=repo)
    else:
        configured_result = str(metadata.get("resultRoot") or "").strip()
        results = _path_from(configured_result, base=repo) if configured_result and not _is_unresolved(configured_result) else profile_output.parent

    scan_roots = _paths(metadata.get("scanRoots"), base=repo)
    if not scan_roots:
        scan_roots = (repo,)

    evidence_roots = _paths(metadata.get("evidenceRoots"), base=repo)
    if results not in evidence_roots:
        evidence_roots = (results, *evidence_roots)

    support_roots = _paths(metadata.get("supportResolverRoots"), base=repo)
    enabled_raw = metadata.get("supportResolverEnabled")
    support_enabled = bool(support_roots) if enabled_raw is None else bool(enabled_raw)

    return OperationalRuntimeProfile(
        profile_id=str(profile.profile_id or "generic"),
        project_name=str(profile.project_name or repo.name or "Project"),
        repo_root=repo,
        output_root=profile_output,
        result_root=results,
        scan_roots=scan_roots,
        evidence_roots=evidence_roots,
        support_resolver_roots=support_roots,
        surfaces=_profile_surfaces(profile, repo),
        support_resolver_enabled=support_enabled,
        metadata=metadata,
    )


def public_path(path: str | Path, repo_root: str | Path) -> str:
    path_obj = Path(path).expanduser().resolve()
    repo = Path(repo_root).expanduser().resolve()
    try:
        return path_obj.relative_to(repo).as_posix()
    except Exception:
        digest = hashlib.sha256(str(path_obj).encode("utf-8", errors="ignore")).hexdigest()[:20]
        return f"external-sha256:{digest}/{path_obj.name}"


def iter_profile_source_files(profile: OperationalRuntimeProfile) -> Iterable[Path]:
    seen: set[str] = set()
    excluded = {".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "venv", ".venv"}
    for root in profile.scan_roots:
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in excluded and not name.startswith(".")]
            for name in files:
                path = Path(current) / name
                if path.suffix.lower() not in SOURCE_SUFFIXES:
                    continue
                key = str(path.resolve()).lower()
                if key in seen:
                    continue
                seen.add(key)
                yield path


__all__ = [
    "OperationalRuntimeProfile",
    "ROUTE_FILENAMES",
    "SOURCE_SUFFIXES",
    "SurfaceSpec",
    "iter_profile_source_files",
    "public_path",
    "resolve_runtime_profile",
]
