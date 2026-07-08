"""Project profile loader for environment-neutral Code Atlas.

Project-specific values such as app roots, ports, protected globs and output roots
belong in a profile file or environment variables, not in Code Atlas core.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AppProfile:
    id: str
    label: str
    root: str = "."
    routes: List[str] = field(default_factory=list)
    default_url: Optional[str] = None
    protected: bool = False
    kind: str = "app"


@dataclass(frozen=True)
class ProjectProfile:
    profile_id: str
    project_name: str
    project_root: str = "${CODE_ATLAS_PROJECT_ROOT}"
    output_root: str = "${CODE_ATLAS_OUTPUT_ROOT}"
    apps: List[AppProfile] = field(default_factory=list)
    protected_globs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _expand(value: str) -> str:
    if not isinstance(value, str):
        return value
    out = value
    for key, val in os.environ.items():
        out = out.replace("${" + key + "}", val)
    return os.path.expandvars(out)


def load_project_profile(profile_path: str | Path | None = None) -> ProjectProfile:
    env_profile = os.environ.get("CODE_ATLAS_PROFILE")
    path = Path(profile_path or env_profile) if (profile_path or env_profile) else None
    if path and path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
    else:
        raw = {
            "profileId": "generic",
            "projectName": os.environ.get("CODE_ATLAS_PROJECT_NAME", "Generic Project"),
            "projectRoot": os.environ.get("CODE_ATLAS_PROJECT_ROOT", "."),
            "outputRoot": os.environ.get("CODE_ATLAS_OUTPUT_ROOT", "./code-atlas-out"),
            "apps": [],
            "protectedGlobs": []
        }
    apps = [AppProfile(
        id=str(a.get("id", "app")),
        label=str(a.get("label", a.get("id", "App"))),
        root=str(a.get("root", ".")),
        routes=list(a.get("routes", [])),
        default_url=a.get("defaultUrl"),
        protected=bool(a.get("protected", False)),
        kind=str(a.get("kind", "app")),
    ) for a in raw.get("apps", [])]
    return ProjectProfile(
        profile_id=str(raw.get("profileId", raw.get("id", "generic"))),
        project_name=str(raw.get("projectName", "Generic Project")),
        project_root=_expand(str(raw.get("projectRoot", "${CODE_ATLAS_PROJECT_ROOT}"))),
        output_root=_expand(str(raw.get("outputRoot", "${CODE_ATLAS_OUTPUT_ROOT}"))),
        apps=apps,
        protected_globs=list(raw.get("protectedGlobs", [])),
        metadata=dict(raw.get("metadata", {})),
    )


def profile_to_dict(profile: ProjectProfile) -> Dict[str, Any]:
    return {
        "profileId": profile.profile_id,
        "projectName": profile.project_name,
        "projectRoot": profile.project_root,
        "outputRoot": profile.output_root,
        "apps": [app.__dict__ for app in profile.apps],
        "protectedGlobs": profile.protected_globs,
        "metadata": profile.metadata,
    }
