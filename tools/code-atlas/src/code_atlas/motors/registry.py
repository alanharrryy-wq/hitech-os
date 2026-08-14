# CODE_ATLAS_MOTOR_HUB_MODULE_V02
"""Environment-neutral declarative registry for Code Atlas Motor Hub.

The reusable hub has no product, OS, repository or external-tool inventory baked
into source. Motors are loaded only from an explicit JSON registry selected by
``CODE_ATLAS_MOTOR_REGISTRY`` or by the active project profile's ``motorRegistry``
metadata field.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from code_atlas.core.project_profile import load_project_profile
from .specs import MotorSpec


def _expand(value: object) -> str:
    return os.path.expandvars(str(value or ""))


def _project_root(explicit: str | Path | None = None) -> Path:
    raw = explicit or os.environ.get("CODE_ATLAS_PROJECT_ROOT") or Path.cwd()
    return Path(raw).expanduser().resolve()


def _registry_path(explicit: str | Path | None = None) -> Path | None:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env_path = os.environ.get("CODE_ATLAS_MOTOR_REGISTRY")
    if env_path:
        return Path(env_path).expanduser().resolve()

    profile_path = os.environ.get("CODE_ATLAS_PROFILE")
    profile = load_project_profile(profile_path)
    configured = profile.metadata.get("motorRegistry")
    if not configured:
        return None
    candidate = Path(_expand(configured)).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    if profile_path:
        return (Path(profile_path).expanduser().resolve().parent / candidate).resolve()
    return (_project_root() / candidate).resolve()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("motors") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("CODE_ATLAS_MOTOR_REGISTRY_MUST_CONTAIN_LIST")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("CODE_ATLAS_MOTOR_REGISTRY_ROWS_MUST_BE_OBJECTS")
    return rows


def _resolve_root(raw: object, project_root: Path) -> Path:
    text = _expand(raw).strip() or "."
    candidate = Path(text).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (project_root / candidate).resolve()


def _to_spec(row: dict[str, Any], project_root: Path) -> MotorSpec:
    motor_id = str(row.get("motorId") or row.get("motor_id") or "").strip()
    group = str(row.get("group") or "External").strip() or "External"
    label = str(row.get("label") or motor_id).strip()
    description = str(row.get("description") or "").strip()
    program = _expand(row.get("program")).strip()
    args_raw = row.get("args") or []
    if not motor_id:
        raise ValueError("MOTOR_ID_REQUIRED")
    if not program:
        raise ValueError(f"MOTOR_PROGRAM_REQUIRED:{motor_id}")
    if not isinstance(args_raw, list):
        raise ValueError(f"MOTOR_ARGS_MUST_BE_LIST:{motor_id}")
    root = _resolve_root(row.get("root"), project_root)
    return MotorSpec(
        motor_id=motor_id,
        group=group,
        label=label,
        description=description,
        root=str(root),
        program=program,
        args=tuple(_expand(value) for value in args_raw),
    )


def build_motor_registry(
    registry_path: str | Path | None = None,
    *,
    project_root: str | Path | None = None,
) -> list[MotorSpec]:
    path = _registry_path(registry_path)
    if path is None:
        return []
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"CODE_ATLAS_MOTOR_REGISTRY_NOT_FOUND:{path}")
    root = _project_root(project_root)
    specs = [_to_spec(row, root) for row in _load_rows(path)]
    ids = [spec.motor_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("CODE_ATLAS_MOTOR_REGISTRY_DUPLICATE_IDS")
    return specs


def grouped_motor_registry(
    registry_path: str | Path | None = None,
    *,
    project_root: str | Path | None = None,
) -> dict[str, list[MotorSpec]]:
    grouped: dict[str, list[MotorSpec]] = {}
    for spec in build_motor_registry(registry_path, project_root=project_root):
        grouped.setdefault(spec.group, []).append(spec)
    return grouped
