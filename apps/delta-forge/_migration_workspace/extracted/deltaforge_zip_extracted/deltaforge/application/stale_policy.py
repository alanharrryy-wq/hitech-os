from __future__ import annotations

import copy
from dataclasses import is_dataclass, replace
from typing import Any

from application.state_machine import derive_idle_state, is_busy_state, is_terminal_state


def _clone_workspace(workspace: Any) -> Any:
    try:
        if is_dataclass(workspace):
            return replace(workspace)
        return copy.deepcopy(workspace)
    except Exception:
        return copy.copy(workspace)


def _get(workspace: Any, name: str, default: Any = None) -> Any:
    return getattr(workspace, name, default)


def _set(workspace: Any, name: str, value: Any) -> None:
    setattr(workspace, name, value)


def _bool(workspace: Any, name: str) -> bool:
    return bool(_get(workspace, name, False))


def reconcile_workspace_state(workspace: Any) -> Any:
    updated = _clone_workspace(workspace)
    current_state = _get(updated, "state", "IDLE")

    if is_terminal_state(current_state):
        return updated

    if bool(_get(updated, "busy", False)) or is_busy_state(current_state):
        return updated

    _set(updated, "state", derive_idle_state(_bool(updated, "dirty"), _bool(updated, "stale")))
    return updated


def apply_dirty_stale(workspace: Any, *, dirty: bool | None = None, stale: bool | None = None) -> Any:
    updated = _clone_workspace(workspace)

    if dirty is not None:
        _set(updated, "dirty", bool(dirty))
    if stale is not None:
        _set(updated, "stale", bool(stale))

    return reconcile_workspace_state(updated)


def mark_dirty(workspace: Any) -> Any:
    return apply_dirty_stale(workspace, dirty=True)


def mark_stale(workspace: Any) -> Any:
    return apply_dirty_stale(workspace, stale=True)


def clear_dirty(workspace: Any) -> Any:
    return apply_dirty_stale(workspace, dirty=False)


def clear_stale(workspace: Any) -> Any:
    return apply_dirty_stale(workspace, stale=False)


def clear_dirty_and_stale(workspace: Any) -> Any:
    return apply_dirty_stale(workspace, dirty=False, stale=False)


def needs_attention(workspace: Any) -> bool:
    return _bool(workspace, "dirty") or _bool(workspace, "stale")


__all__ = [
    "apply_dirty_stale",
    "clear_dirty",
    "clear_dirty_and_stale",
    "clear_stale",
    "mark_dirty",
    "mark_stale",
    "needs_attention",
    "reconcile_workspace_state",
]
