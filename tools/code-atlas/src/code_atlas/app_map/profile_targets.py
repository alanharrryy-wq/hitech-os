"""App Map target provider backed by project profiles.

This module lets App Map derive selectable apps from a profile instead of a
hardcoded project-specific list. It is intentionally read-only.
"""
from __future__ import annotations
from typing import Any, Dict, List
try:
    from code_atlas.core.project_profile import load_project_profile
except Exception:  # pragma: no cover
    load_project_profile = None


def load_app_targets(profile_path: str | None = None) -> List[Dict[str, Any]]:
    if load_project_profile is None:
        return []
    profile = load_project_profile(profile_path)
    targets = []
    for app in profile.apps:
        targets.append({
            "id": app.id,
            "label": app.label,
            "root": app.root,
            "routes": app.routes,
            "defaultUrl": app.default_url,
            "protected": app.protected,
            "kind": app.kind,
            "source": "project-profile",
        })
    return targets


def app_target_summary(profile_path: str | None = None) -> Dict[str, Any]:
    targets = load_app_targets(profile_path)
    return {
        "mode": "profile-backed-app-targets",
        "targetCount": len(targets),
        "targets": targets,
    }
