# PRISMO Learning Core V1.1 F2
# Generated package: prismo learn2 3005 1100 fix1
# Operation model: evidence-intake-real, local store writes only, read-only against repo/DB/secrets.
# This file intentionally uses only Python standard library modules.

"""F2 intake policy and root planning.

This module decides what PRISMO is allowed to inspect. It never executes evidence,
never reads forbidden secret files and never touches DB contents.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
import os

from .constants import (
    DEFAULT_OUTPUT_ROOT,
    INTAKE_DEFAULT_MAX_FILES_PER_ROOT,
    INTAKE_DEFAULT_MAX_TOTAL_SECONDS,
    INTAKE_DEFAULT_MAX_ZIPS,
    INTAKE_PRIORITY_EXTENSIONS,
    INTAKE_PRIORITY_KEYWORDS,
    STORE_FOLDER_NAME,
)
from .paths import default_download_root, find_repo_root
from .safety import is_forbidden_path


@dataclass(frozen=True)
class IntakeLimits:
    max_files_per_root: int = INTAKE_DEFAULT_MAX_FILES_PER_ROOT
    max_zips: int = INTAKE_DEFAULT_MAX_ZIPS
    max_total_seconds: int = INTAKE_DEFAULT_MAX_TOTAL_SECONDS
    max_depth_hint: int = 9

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntakeRoot:
    path: str
    label: str
    priority: int
    exists: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _root(path: Path, label: str, priority: int, reason: str) -> IntakeRoot:
    return IntakeRoot(str(path), label, priority, path.exists(), reason)


def planned_roots(repo_root: str | Path | None = None, include_downloads: bool = True) -> list[IntakeRoot]:
    roots: list[IntakeRoot] = []
    downloads = default_download_root()
    repo = Path(repo_root) if repo_root else find_repo_root()
    if include_downloads:
        roots.append(_root(downloads, "downloads_root", 100, "Primary local evidence drop."))
        roots.append(_root(downloads / "PRISMO_GOVERNANCE_CANON", "governance_canon", 95, "Governance canon evidence."))
    if repo:
        roots.append(_root(repo / "tools" / "_local" / "evidence", "repo_local_evidence", 90, "Repo local evidence folder."))
        roots.append(_root(repo / "prisma-control-center" / "internal", "control_center_internal", 70, "Control Center internal docs/reports only."))
        roots.append(_root(repo / "docs", "repo_docs", 60, "Project docs evidence."))
    roots.append(_root(downloads / STORE_FOLDER_NAME, "learning_store", 50, "Existing learning store snapshots/reports."))
    # Deduplicate by normalized path while preserving highest priority.
    best: dict[str, IntakeRoot] = {}
    for r in roots:
        key = str(Path(r.path)).lower()
        if key not in best or r.priority > best[key].priority:
            best[key] = r
    return sorted(best.values(), key=lambda r: r.priority, reverse=True)


def is_priority_candidate(path: str | Path) -> bool:
    p = Path(path)
    if is_forbidden_path(p):
        return False
    name = p.name.lower()
    suffix = p.suffix.lower()
    if suffix not in INTAKE_PRIORITY_EXTENSIONS:
        return False
    if suffix == ".zip":
        return any(k in name for k in INTAKE_PRIORITY_KEYWORDS) or True
    return any(k in name for k in INTAKE_PRIORITY_KEYWORDS)


def candidate_rank(path: str | Path) -> int:
    p = Path(path)
    name = p.name.lower()
    rank = 0
    if p.suffix.lower() == ".zip": rank += 80
    if "result" in name: rank += 35
    if "fail" in name or "diagnostic" in name: rank += 40
    if "prismo" in name: rank += 40
    if "prisma" in name: rank += 25
    if "playwright" in name: rank += 35
    if "verify" in name or "verification" in name: rank += 25
    if "manifest" in name or "report" in name: rank += 20
    if "node_modules" in str(p).lower(): rank -= 100
    return rank


def policy_snapshot(repo_root: str | Path | None = None) -> dict[str, Any]:
    roots = planned_roots(repo_root)
    return {
        "ok": True,
        "schema_version": "f2.1",
        "mode": "evidence_intake_real",
        "read_only": True,
        "mutation_allowed": False,
        "allowed_runtime_write": "PRISMO_LEARNING_STORE only",
        "forbidden": [".env", "raw sqlite/db contents", "node_modules", ".git", "execution of evidence", "deploy", "git push"],
        "priority_extensions": sorted(INTAKE_PRIORITY_EXTENSIONS),
        "roots": [r.to_dict() for r in roots],
        "limits": IntakeLimits().to_dict(),
    }
