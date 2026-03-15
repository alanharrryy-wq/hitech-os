from __future__ import annotations

import hashlib
import json
import os
import platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .errors import ConfigurationError, PathSafetyError, PhaseValidationError


PHASE_NAME = "phase_01"
ALLOWED_SCAFFOLD_PREFIX = Path("tools/hos/git_sentinel_modular")
REQUIRED_SHARED_LAYOUT = (
    "shared",
    "tests/contracts",
    "tests/shared",
    "tests/integration",
    "docs/phases/phase_01",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class SentinelEnvironment:
    python_executable: str
    platform_name: str
    working_directory: str
    generated_at: str = field(default_factory=utc_now_iso)

    @classmethod
    def capture(cls) -> "SentinelEnvironment":
        import sys

        return cls(
            python_executable=sys.executable,
            platform_name=platform.platform(),
            working_directory=str(Path.cwd().resolve()),
        )


@dataclass(slots=True)
class SentinelPaths:
    repo_root: Path
    scaffold_root: Path
    shared_root: Path
    docs_root: Path
    tests_root: Path
    reports_root: Path

    @classmethod
    def from_scaffold_root(cls, repo_root: Path, scaffold_root: Path) -> "SentinelPaths":
        scaffold_root = scaffold_root.resolve()
        repo_root = repo_root.resolve()
        ensure_inside_root(repo_root, scaffold_root, reason="scaffold_root must live inside repo_root")
        return cls(
            repo_root=repo_root,
            scaffold_root=scaffold_root,
            shared_root=(scaffold_root / "shared").resolve(),
            docs_root=(scaffold_root / "docs").resolve(),
            tests_root=(scaffold_root / "tests").resolve(),
            reports_root=(scaffold_root / "_reports").resolve(),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "repo_root": str(self.repo_root),
            "scaffold_root": str(self.scaffold_root),
            "shared_root": str(self.shared_root),
            "docs_root": str(self.docs_root),
            "tests_root": str(self.tests_root),
            "reports_root": str(self.reports_root),
        }


def detect_repo_root(explicit: str | Path | None = None) -> Path:
    candidate = Path(explicit).resolve() if explicit else Path.cwd().resolve()
    for root in [candidate, *candidate.parents]:
        if (root / ".git").exists() and (root / "tools" / "hos").exists():
            return root.resolve()
    raise ConfigurationError(
        "Could not detect repo root.",
        start_path=str(candidate),
        expected_markers=[".git", "tools/hos"],
    )


def detect_scaffold_root(repo_root: Path, explicit: str | Path | None = None) -> Path:
    if explicit:
        p = Path(explicit).resolve()
        if not p.exists():
            raise ConfigurationError("Explicit scaffold root does not exist.", scaffold_root=str(p))
        return p

    canonical = (repo_root / ALLOWED_SCAFFOLD_PREFIX).resolve()
    if canonical.exists():
        return canonical

    parent = repo_root / "tools" / "hos"
    matches = sorted([p.resolve() for p in parent.glob("git_sentinel_modular*") if p.is_dir()])
    if matches:
        return matches[-1]

    raise ConfigurationError(
        "Could not detect modular scaffold root.",
        expected=str(canonical),
        search_parent=str(parent),
    )


def ensure_inside_root(root: Path, candidate: Path, reason: str = "") -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    if not str(candidate).startswith(str(root)):
        raise PathSafetyError(
            "Path escapes allowed root.",
            root=str(root),
            candidate=str(candidate),
            reason=reason,
        )
    return candidate


def ensure_required_layout(paths: SentinelPaths) -> list[Path]:
    created: list[Path] = []
    for rel in REQUIRED_SHARED_LAYOUT:
        target = ensure_inside_root(paths.scaffold_root, paths.scaffold_root / rel, reason="required layout")
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created.append(target)
    if not paths.reports_root.exists():
        paths.reports_root.mkdir(parents=True, exist_ok=True)
        created.append(paths.reports_root)
    return created


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PhaseValidationError("JSON file does not exist.", path=str(path)) from exc
    except json.JSONDecodeError as exc:
        raise PhaseValidationError("JSON file is invalid.", path=str(path), detail=str(exc)) from exc


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def assert_phase_docs_present(paths: SentinelPaths) -> Path:
    status_path = paths.docs_root / "phases" / PHASE_NAME
    if not status_path.exists():
        raise PhaseValidationError(
            "Phase docs root is missing.",
            expected=str(status_path),
            phase=PHASE_NAME,
        )
    return status_path
