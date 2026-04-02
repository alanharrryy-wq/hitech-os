from __future__ import annotations

import copy
from dataclasses import dataclass, is_dataclass, replace
from typing import Any

from application.state_machine import assert_transition, derive_idle_state, normalize_state


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


@dataclass(frozen=True, slots=True)
class RefreshDecision:
    should_refresh: bool
    reason: str
    force: bool = False
    preserve_dirty: bool = False


def build_refresh_decision(workspace: Any, *, force: bool = False) -> RefreshDecision:
    if _bool(workspace, "busy"):
        return RefreshDecision(False, "busy", force=force, preserve_dirty=_bool(workspace, "dirty"))

    if force:
        return RefreshDecision(True, "forced", force=True, preserve_dirty=_bool(workspace, "dirty"))

    if _bool(workspace, "stale"):
        return RefreshDecision(True, "stale", preserve_dirty=_bool(workspace, "dirty"))

    if normalize_state(_get(workspace, "state", "IDLE")) == "FAILED":
        return RefreshDecision(True, "failed_recovery", preserve_dirty=_bool(workspace, "dirty"))

    return RefreshDecision(False, "clean", preserve_dirty=_bool(workspace, "dirty"))


def begin_refresh(workspace: Any, *, force: bool = False) -> Any:
    decision = build_refresh_decision(workspace, force=force)
    updated = _clone_workspace(workspace)

    if not decision.should_refresh:
        return updated

    current_state = _get(updated, "state", "IDLE")
    _set(updated, "state", assert_transition(current_state, "REFRESHING"))
    _set(updated, "busy", True)
    return updated


def finish_refresh(
    workspace: Any,
    *,
    refreshed_scope: Any | None = None,
    refreshed_results: Any | None = None,
) -> Any:
    updated = _clone_workspace(workspace)

    if refreshed_scope is not None:
        _set(updated, "scope", refreshed_scope)
    if refreshed_results is not None:
        _set(updated, "results", refreshed_results)

    dirty = _bool(updated, "dirty")
    _set(updated, "busy", False)
    _set(updated, "stale", False)
    _set(updated, "state", derive_idle_state(dirty, False))
    return updated


def fail_refresh(workspace: Any, *, error: object | None = None) -> Any:
    updated = _clone_workspace(workspace)
    stale_now = _bool(updated, "stale") or error is not None

    _set(updated, "busy", False)
    _set(updated, "stale", stale_now)
    _set(updated, "state", "FAILED")

    if error is not None:
        _set(updated, "last_error", str(error))

    return updated


__all__ = [
    "RefreshDecision",
    "begin_refresh",
    "build_refresh_decision",
    "fail_refresh",
    "finish_refresh",
]
