from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Protocol

from application.contracts import EngineAdapter
from application.session_manager import SessionManager
from domain import AppEvent
from domain.models import (
    ApplyResult,
    OpsDocument,
    RefreshResult,
    RollbackResult,
    SessionWorkspace,
    ValidationResult,
)
from domain.models.plan import PlanResult
from domain.models.process_report import ProcessReport
from domain.session_states import SessionState
from infrastructure.event_bus import EventBus
from infrastructure.watcher import FileWatcherService


class CommandUiBridge(Protocol):
    def refresh_ui(self, session: SessionWorkspace | None = None) -> None:
        ...

    def pick_files(self) -> list[str]:
        ...

    def pick_folder(self) -> str:
        ...

    def pick_ops_to_load(self) -> str:
        ...

    def pick_ops_to_save(self) -> str:
        ...

    def current_ops_text(self) -> str:
        ...

    def choose_rollback_token(self, rollback_tokens: list[str]) -> str:
        ...

    def show_info(self, message: str) -> None:
        ...

    def show_warning(self, message: str) -> None:
        ...

    def show_error(self, message: str) -> None:
        ...

    def open_path(self, path: str) -> None:
        ...


class CommandController:
    def __init__(
        self,
        *,
        ui: CommandUiBridge,
        manager: SessionManager,
        event_bus: EventBus,
        watcher: FileWatcherService,
        engine: EngineAdapter,
    ) -> None:
        self._ui = ui
        self._manager = manager
        self._event_bus = event_bus
        self._watcher = watcher
        self._engine = engine

    def bootstrap(self) -> None:
        if self._manager.current() is None:
            session = self._manager.create_session()
            self._emit("session_created", session)
        self._ui.refresh_ui(self._manager.current())

    def activate_session(self, session_id: str) -> None:
        session = self._manager.activate(session_id)
        self._ui.refresh_ui(session)

    def new_session(self) -> None:
        session = self._manager.create_session()
        self._emit("session_created", session)
        self._ui.refresh_ui(session)

    def clone_session(self) -> None:
        current = self._manager.current()
        if current is None:
            return

        cloned = self._manager.clone_session(current.session_id)
        if cloned is None:
            return

        self._watcher.watch_session(cloned.session_id)
        self._emit("session_cloned", cloned, {"source": current.session_id})
        self._ui.refresh_ui(cloned)

    def close_session(self) -> None:
        current = self._manager.current()
        if current is None:
            return

        self._watcher.unwatch_session(current.session_id)
        next_session = self._manager.close_session(current.session_id)
        self._emit("session_closed", current)

        if next_session is None:
            next_session = self._manager.create_session()
            self._emit("session_created", next_session)

        self._ui.refresh_ui(next_session)

    def choose_files(self) -> None:
        session = self._require_session()
        if session is None:
            return

        files = self._ui.pick_files()
        if not files:
            return

        normalized = [str(Path(item).resolve()) for item in files]
        root = self._common_root(normalized)
        updated = self._manager.update_scope(session.session_id, normalized, root)
        if updated is None:
            return

        self._watcher.watch_session(updated.session_id)
        self._emit("scope_loaded", updated, {"count": len(normalized)})
        self._ui.refresh_ui(updated)

    def choose_folder(self) -> None:
        session = self._require_session()
        if session is None:
            return

        folder = self._ui.pick_folder()
        if not folder:
            return

        resolved = str(Path(folder).resolve())
        updated = self._manager.update_scope(session.session_id, [resolved], resolved)
        if updated is None:
            return

        self._watcher.watch_session(updated.session_id)
        self._emit("scope_loaded", updated, {"count": updated.scope.count})
        self._ui.refresh_ui(updated)

    def clear_scope(self) -> None:
        session = self._require_session()
        if session is None:
            return

        updated = self._manager.clear_scope(session.session_id)
        if updated is None:
            return

        self._watcher.unwatch_session(updated.session_id)
        self._emit("scope_cleared", updated)
        self._ui.refresh_ui(updated)

    def load_ops(self) -> None:
        session = self._require_session()
        if session is None:
            return

        path = self._ui.pick_ops_to_load()
        if not path:
            return

        try:
            doc = self._engine.load_ops(path)
        except Exception as exc:
            self._manager.set_state(session.session_id, SessionState.ERROR)
            self._ui.show_error(f"No se pudo cargar ops: {exc}")
            self._ui.refresh_ui(self._manager.get(session.session_id))
            return

        session.ops_document = doc
        session.ops_metadata = doc.summary_payload()
        session.state = SessionState.OPS_LOADED
        session.dirty = False
        self._emit("ops_loaded", session, {"path": doc.source_path})
        self._ui.refresh_ui(session)

    def save_ops(self) -> None:
        session = self._require_session()
        if session is None:
            return

        text = self._ui.current_ops_text()
        session.ops_document = OpsDocument(text=text, source_path=session.ops_document.source_path)
        session.ops_metadata = session.ops_document.summary_payload()

        path = self._ui.pick_ops_to_save()
        if not path:
            return

        try:
            io_result = self._engine.save_ops(path, session.ops_document)
        except Exception as exc:
            self._ui.show_error(f"No se pudo guardar ops: {exc}")
            return

        if io_result.ok:
            session.ops_document.source_path = io_result.path
            session.ops_metadata = session.ops_document.summary_payload()
            session.state = SessionState.OPS_LOADED
            session.dirty = False
            self._emit("ops_saved", session, {"path": io_result.path})
            self._ui.refresh_ui(session)
            return

        self._ui.show_warning(io_result.message)

    def validate(self) -> None:
        session = self._require_session()
        if session is None:
            return

        self._sync_ops_from_ui(session)
        self._emit("validation_started", session)

        try:
            result = self._engine.validate(session)
        except Exception as exc:
            result = ValidationResult(
                ok=False,
                status="failed",
                summary="Validation execution failed",
                errors=[str(exc)],
                process=ProcessReport(engine_name="controller", mode="validate", stderr_tail=[str(exc)]),
            )

        session.validation_result = result
        session.ops_metadata = session.ops_document.summary_payload()
        session.state = SessionState.VALIDATED if result.ok else SessionState.ERROR
        self._emit("validation_finished", session, {"ok": result.ok, "summary": result.summary})
        self._ui.refresh_ui(session)

    def plan(self) -> None:
        session = self._require_session()
        if session is None:
            return

        self._sync_ops_from_ui(session)
        self._emit("plan_started", session)

        try:
            result = self._engine.plan(session)
        except Exception as exc:
            result = PlanResult(
                ok=False,
                status="failed",
                summary="Plan execution failed",
                errors=[str(exc)],
                process=ProcessReport(engine_name="controller", mode="plan", stderr_tail=[str(exc)]),
            )

        session.plan_result = result
        session.ops_metadata = session.ops_document.summary_payload()
        session.state = SessionState.PLAN_GENERATED if result.ok else SessionState.ERROR
        self._emit("plan_finished", session, {"ok": result.ok, "summary": result.summary})
        self._ui.refresh_ui(session)

    def apply(self) -> None:
        session = self._require_session()
        if session is None:
            return

        self._sync_ops_from_ui(session)
        self._emit("apply_started", session)

        try:
            result = self._engine.apply(session)
        except Exception as exc:
            result = ApplyResult(
                ok=False,
                status="failed",
                summary="Apply execution failed",
                errors=[str(exc)],
                process=ProcessReport(engine_name="controller", mode="apply", stderr_tail=[str(exc)]),
            )

        session.apply_result = result
        if result.rollback_token:
            session.rollback_tokens.append(result.rollback_token)
            session.rollback_token = result.rollback_token

        if result.rollback_token and result.ok:
            session.state = SessionState.ROLLBACK_AVAILABLE
        else:
            session.state = SessionState.APPLIED if result.ok else SessionState.ERROR

        self._emit("apply_finished", session, {"ok": result.ok, "summary": result.summary})
        self._ui.refresh_ui(session)

    def rollback(self) -> None:
        session = self._require_session()
        if session is None:
            return

        token = self._ui.choose_rollback_token(session.rollback_tokens)
        if not token:
            token = session.rollback_token

        if not token:
            self._ui.show_warning("No se seleccionó rollback.")
            return

        self._emit("rollback_started", session, {"token": token})

        try:
            result = self._engine.rollback(session, token)
        except Exception as exc:
            result = RollbackResult(
                ok=False,
                status="failed",
                summary="Rollback execution failed",
                errors=[str(exc)],
                rollback_token=token,
                process=ProcessReport(engine_name="controller", mode="rollback", stderr_tail=[str(exc)]),
            )

        session.rollback_result = result
        session.rollback_token = ""
        if result.ok:
            session.state = SessionState.ROLLBACK_AVAILABLE
            session.dirty = False
            session.stale = False
        else:
            session.state = SessionState.ERROR

        self._emit("rollback_finished", session, {"ok": result.ok, "summary": result.summary})
        self._ui.refresh_ui(session)

    def refresh(self) -> None:
        session = self._require_session()
        if session is None:
            return

        try:
            result = self._engine.refresh(session)
        except Exception as exc:
            result = RefreshResult(
                ok=False,
                status="failed",
                summary="Refresh execution failed",
                errors=[str(exc)],
                process=ProcessReport(engine_name="controller", mode="refresh", stderr_tail=[str(exc)]),
            )

        session.refresh_result = result
        session.ops_metadata = session.ops_document.summary_payload()
        if result.ok and session.state == SessionState.DIRTY_OR_STALE:
            session.state = SessionState.SCOPE_LOADED
            session.stale = False
            session.dirty = False

        self._ui.refresh_ui(session)

    def open_root(self) -> None:
        session = self._require_session()
        if session is None:
            return

        if session.scope.root_dir:
            self._ui.open_path(session.scope.root_dir)
            return

        self._ui.show_warning("No hay root activo en la sesión.")

    def settings(self) -> None:
        self._ui.show_info("Settings UI aún no expone opciones avanzadas.")

    def on_ops_text_changed(self, new_text: str) -> None:
        session = self._manager.current()
        if session is None:
            return

        session.ops_document.text = new_text
        session.ops_metadata = session.ops_document.summary_payload()
        session.dirty = True
        if new_text.strip():
            session.state = SessionState.OPS_LOADED

        self._ui.refresh_ui(session)

    def next_session(self) -> None:
        sessions = self._manager.sessions
        if len(sessions) < 2:
            return

        current_id = self._manager.current_session_id
        ids = [item.session_id for item in sessions]
        current_index = ids.index(current_id)
        next_index = (current_index + 1) % len(ids)
        session = self._manager.activate(ids[next_index])
        self._ui.refresh_ui(session)

    def prev_session(self) -> None:
        sessions = self._manager.sessions
        if len(sessions) < 2:
            return

        current_id = self._manager.current_session_id
        ids = [item.session_id for item in sessions]
        current_index = ids.index(current_id)
        next_index = (current_index - 1) % len(ids)
        session = self._manager.activate(ids[next_index])
        self._ui.refresh_ui(session)

    def focus_left(self) -> None:
        self._ui.refresh_ui(self._manager.current())

    def focus_center(self) -> None:
        self._ui.refresh_ui(self._manager.current())

    def focus_right(self) -> None:
        self._ui.refresh_ui(self._manager.current())

    def focus_bottom(self) -> None:
        self._ui.refresh_ui(self._manager.current())

    def _require_session(self) -> SessionWorkspace | None:
        session = self._manager.current()
        if session is not None:
            return session

        self._ui.show_warning("No hay sesión activa.")
        return None

    def _sync_ops_from_ui(self, session: SessionWorkspace) -> None:
        text = self._ui.current_ops_text()
        session.ops_document.text = text
        session.ops_metadata = session.ops_document.summary_payload()
        if text.strip() and session.state == SessionState.SCOPE_LOADED:
            session.state = SessionState.OPS_LOADED

    def _emit(self, name: str, session: SessionWorkspace, payload: dict | None = None) -> None:
        event = AppEvent(name=name, session_id=session.session_id, payload=payload or {})
        session.add_log(name, str(payload or ""))
        self._event_bus.emit(event)

    def _common_root(self, paths: list[str]) -> str:
        if not paths:
            return ""
        try:
            return os.path.commonpath(paths)
        except Exception:
            return str(Path(paths[0]).parent)
