from __future__ import annotations

from typing import Any

from deltaforge.application.session_actions import SessionActions
from deltaforge.application.session_manager import SessionManager
from deltaforge.application.workspace_facade import WorkspaceFacade


class UiCommandController:
    """
    Thin controller bridge consumed by Charlie.

    It delegates legal mutations to SessionActions and keeps UI logic out of widgets.
    Domain-specific execution remains intentionally conservative.
    """

    def __init__(
        self,
        manager: SessionManager,
        actions: SessionActions,
        facade: WorkspaceFacade | None = None,
    ) -> None:
        self._manager = manager
        self._actions = actions
        self._facade = facade

    def dispatch_ui_action(self, action_name: str, *args: Any) -> Any:
        callback = getattr(self, action_name, None)
        if not callable(callback):
            return False
        return callback(*args)

    def create_session(self) -> bool:
        self._actions.create_session(make_active=True)
        return True

    def close_session(self, session_id: object) -> bool:
        self._actions.close_session(session_id)
        return True

    def select_session(self, session_id: object) -> bool:
        self._actions.activate_session(session_id)
        return True

    def browse_root_dir(self) -> bool:
        # Hook for a real picker in the repo-local runtime.
        return False

    def validate_active(self) -> bool:
        session_id = self._require_active_session_id()
        self._actions.start_run(session_id, "VALIDATING")
        self._actions.complete_run(session_id, surface="validation", result={"summary": "Validation finished", "items": []})
        return True

    def plan_active(self) -> bool:
        session_id = self._require_active_session_id()
        self._actions.start_run(session_id, "PLANNING")
        self._actions.complete_run(
            session_id,
            surface="plan",
            result={"title": "Plan preview", "summary": "Plan generated", "groups": []},
        )
        return True

    def apply_active(self) -> bool:
        session_id = self._require_active_session_id()
        self._actions.start_run(session_id, "APPLYING")
        self._actions.complete_run(session_id, surface="apply", result={"summary": "Apply finished"})
        return True

    def rollback_active(self) -> bool:
        session_id = self._require_active_session_id()
        self._actions.start_run(session_id, "ROLLING_BACK")
        self._actions.complete_run(session_id, surface="rollback", result={"summary": "Rollback finished"})
        return True

    def refresh_active(self) -> bool:
        session_id = self._require_active_session_id()
        self._actions.begin_refresh(session_id)
        self._actions.finish_refresh(session_id)
        return True

    def select_op(self, payload: Any) -> bool:
        session_id = self._require_active_session_id()
        self._actions.update_selection(session_id, op=payload, detail=payload, surface="plan")
        return True

    def select_target(self, payload: Any) -> bool:
        session_id = self._require_active_session_id()
        targets = self._normalize_targets(payload)
        self._actions.update_selection(session_id, targets=targets, detail=payload, surface="events")
        return True

    def _require_active_session_id(self) -> object:
        session_id = self._manager.active_session_id
        if session_id is None:
            created = self._actions.create_session(make_active=True)
            session_id = getattr(created, "session_id", None)
        if session_id is None:
            raise RuntimeError("No active session available")
        return session_id

    def _normalize_targets(self, payload: Any) -> tuple[str, ...]:
        if payload is None:
            return ()
        if isinstance(payload, dict):
            for key in ("path", "label", "name", "id"):
                value = payload.get(key)
                if value:
                    return (str(value),)
        return (str(payload),)
