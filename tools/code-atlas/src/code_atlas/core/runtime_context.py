"""Runtime context resolution for environment-neutral Code Atlas execution."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .project_profile import ProjectProfile, load_project_profile


def _resolved_path(value: str | Path | None, *, fallback: Path) -> Path:
    if value is None or not str(value).strip():
        return fallback.resolve()
    return Path(value).expanduser().resolve()


def _profile_path(profile: ProjectProfile, attr: str) -> str | None:
    value = getattr(profile, attr, None)
    if not isinstance(value, str) or not value.strip():
        return None
    if value.startswith("${") and value.endswith("}"):
        return None
    return value


@dataclass(frozen=True)
class RuntimeContext:
    repo_root: Path
    output_root: Path
    result_root: Path
    profile: ProjectProfile

    @classmethod
    def resolve(
        cls,
        repo_root: str | Path | None,
        output_root: str | Path | None,
        result_root: str | Path | None = None,
        *,
        profile_path: str | Path | None = None,
    ) -> "RuntimeContext":
        profile = load_project_profile(profile_path)
        cwd = Path.cwd()
        repo_value = repo_root or os.environ.get("CODE_ATLAS_PROJECT_ROOT") or _profile_path(profile, "project_root")
        repo = _resolved_path(repo_value, fallback=cwd)

        output_value = output_root or os.environ.get("CODE_ATLAS_OUTPUT_ROOT") or _profile_path(profile, "output_root")
        out = _resolved_path(output_value, fallback=repo / "code-atlas-out")

        result_value = result_root or os.environ.get("CODE_ATLAS_RESULT_ROOT")
        results = _resolved_path(result_value, fallback=out)
        return cls(repo_root=repo, output_root=out, result_root=results, profile=profile)

    def app_roots(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for app in self.profile.apps:
            raw = str(app.root or ".").replace("\\", "/").strip()
            candidate = Path(raw)
            if candidate.is_absolute() or ".." in candidate.parts:
                rows.append({
                    "id": app.id,
                    "label": app.label,
                    "kind": app.kind,
                    "root": raw,
                    "path": None,
                    "valid": False,
                    "reason": "APP_ROOT_MUST_BE_REPO_RELATIVE",
                })
                continue
            resolved = (self.repo_root / candidate).resolve()
            try:
                resolved.relative_to(self.repo_root)
            except ValueError:
                rows.append({
                    "id": app.id,
                    "label": app.label,
                    "kind": app.kind,
                    "root": raw,
                    "path": None,
                    "valid": False,
                    "reason": "APP_ROOT_ESCAPES_REPOSITORY",
                })
                continue
            rows.append({
                "id": app.id,
                "label": app.label,
                "kind": app.kind,
                "root": raw or ".",
                "path": resolved,
                "valid": True,
                "reason": None,
            })
        return rows

    def metadata(self, key: str, default: Any = None) -> Any:
        return self.profile.metadata.get(key, default)
