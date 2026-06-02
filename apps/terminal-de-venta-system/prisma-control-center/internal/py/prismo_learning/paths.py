# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Path discovery and store resolution for PRISMO Learning Core."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable
from .constants import DEFAULT_OUTPUT_ROOT, STORE_FOLDER_NAME, STORE_SUBDIRS


def default_download_root() -> Path:
    return Path(os.environ.get("PRISMO_DOWNLOAD_ROOT") or DEFAULT_OUTPUT_ROOT)


def find_repo_root(start: str | os.PathLike[str] | None = None) -> Path | None:
    candidates: list[Path] = []
    if start:
        candidates.append(Path(start))
    env = os.environ.get("PRISMA_REPO_ROOT") or os.environ.get("PRISMO_REPO_ROOT")
    if env:
        candidates.append(Path(env))
    try:
        candidates.append(Path(__file__).resolve().parents[4])
    except Exception:
        pass
    cwd = Path.cwd()
    candidates.extend([cwd, *cwd.parents])
    seen: set[str] = set()
    for cand in candidates:
        try:
            p = cand.expanduser().resolve()
        except Exception:
            continue
        if str(p).lower() in seen:
            continue
        seen.add(str(p).lower())
        if (p / "prisma-control-center").exists() and ((p / "package.json").exists() or (p / "products").exists()):
            return p
        if (p / "apps" / "terminal-de-venta-system" / "prisma-control-center").exists():
            return (p / "apps" / "terminal-de-venta-system").resolve()
    return None


def control_center_py_root(repo_root: str | os.PathLike[str] | None = None) -> Path | None:
    root = Path(repo_root) if repo_root else find_repo_root()
    if not root:
        return None
    candidate = root / "prisma-control-center" / "internal" / "py"
    return candidate if candidate.exists() else None


def store_root(base: str | os.PathLike[str] | None = None) -> Path:
    base_path = Path(base) if base else default_download_root()
    return base_path / STORE_FOLDER_NAME


def ensure_store(base: str | os.PathLike[str] | None = None) -> Path:
    root = store_root(base)
    root.mkdir(parents=True, exist_ok=True)
    for sub in STORE_SUBDIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)
    manifest = root / "store_manifest.json"
    if not manifest.exists():
        manifest.write_text('{"schema_version":"1.0.0","store":"PRISMO_LEARNING_STORE"}\n', encoding="utf-8")
    return root


def allowed_roots(repo_root: str | os.PathLike[str] | None = None) -> list[Path]:
    roots: list[Path] = []
    download = default_download_root()
    roots.extend([
        download,
        download / "PRISMO_GOVERNANCE_CANON",
        download / STORE_FOLDER_NAME,
    ])
    repo = Path(repo_root) if repo_root else find_repo_root()
    if repo:
        roots.extend([
            repo / "prisma-control-center" / "internal",
            repo / "tools" / "_local" / "evidence",
        ])
    return [r for r in roots if r.exists()]


def is_within(path: str | os.PathLike[str], roots: Iterable[str | os.PathLike[str]]) -> bool:
    try:
        target = Path(path).resolve()
    except Exception:
        return False
    for root in roots:
        try:
            target.relative_to(Path(root).resolve())
            return True
        except Exception:
            continue
    return False


def safe_relative(path: str | os.PathLike[str], root: str | os.PathLike[str] | None = None) -> str:
    p = Path(path)
    if root:
        try:
            return str(p.resolve().relative_to(Path(root).resolve())).replace("\\", "/")
        except Exception:
            pass
    return p.name
