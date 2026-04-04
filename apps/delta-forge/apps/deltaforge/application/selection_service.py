from __future__ import annotations

import copy
from dataclasses import is_dataclass, replace
from typing import Any


_DEFAULT_SELECTION: dict[str, Any] = {
    "targets": (),
    "op": None,
    "detail": None,
    "surface": "events",
    "view": "plan",
}


def _clone_workspace(workspace: Any) -> Any:
    try:
        if is_dataclass(workspace):
            return replace(workspace)
        return copy.deepcopy(workspace)
    except Exception:
        return copy.copy(workspace)


def _coerce_targets(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()

    if isinstance(value, (str, bytes)):
        return (value,)

    try:
        return tuple(value)
    except TypeError:
        return (value,)


def selection_snapshot(workspace: Any) -> dict[str, Any]:
    snapshot = dict(_DEFAULT_SELECTION)
    current = getattr(workspace, "selection", None)

    if isinstance(current, dict):
        snapshot.update(current)
    elif current is not None:
        for key in snapshot:
            snapshot[key] = getattr(current, key, snapshot[key])

    snapshot["targets"] = _coerce_targets(snapshot.get("targets"))
    snapshot["surface"] = str(snapshot.get("surface") or "events")
    snapshot["view"] = str(snapshot.get("view") or "plan")
    return snapshot


def replace_selection(workspace: Any, **updates: Any) -> Any:
    updated = _clone_workspace(workspace)
    snapshot = selection_snapshot(updated)
    snapshot.update(updates)
    snapshot["targets"] = _coerce_targets(snapshot.get("targets"))
    setattr(updated, "selection", snapshot)
    return updated


def clear_selection(workspace: Any) -> Any:
    return replace_selection(workspace, targets=(), op=None, detail=None)


class SelectionService:
    def snapshot(self, workspace: Any) -> dict[str, Any]:
        return selection_snapshot(workspace)

    def replace(self, workspace: Any, **updates: Any) -> Any:
        return replace_selection(workspace, **updates)

    def clear(self, workspace: Any) -> Any:
        return clear_selection(workspace)


__all__ = [
    "SelectionService",
    "clear_selection",
    "replace_selection",
    "selection_snapshot",
]
