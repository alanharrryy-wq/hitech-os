from __future__ import annotations

from typing import Protocol, Sequence

from domain.ids import SessionId
from domain.models.diff import DiffPreview
from domain.models.ops_document import OpsDocument
from domain.models.plan import PlanResult
from domain.models.results import ApplyResult, RefreshResult, RollbackResult, ValidationResult
from domain.models.session import SessionWorkspace
from domain.models.settings import AppSettings


class SessionRepository(Protocol):
    def list_sessions(self) -> Sequence[SessionWorkspace]:
        ...

    def get_session(self, session_id: SessionId) -> SessionWorkspace | None:
        ...

    def save_session(self, session: SessionWorkspace) -> None:
        ...

    def save_ops_document(self, session_id: SessionId, ops_document: OpsDocument) -> None:
        ...

    def get_ops_document(self, session_id: SessionId) -> OpsDocument | None:
        ...

    def save_plan(self, session_id: SessionId, plan_result: PlanResult) -> None:
        ...

    def get_plan(self, session_id: SessionId) -> PlanResult | None:
        ...

    def save_diff(self, session_id: SessionId, diff_preview: DiffPreview) -> None:
        ...

    def get_diff(self, session_id: SessionId) -> DiffPreview | None:
        ...

    def save_validation_result(self, session_id: SessionId, result: ValidationResult) -> None:
        ...

    def save_apply_result(self, session_id: SessionId, result: ApplyResult) -> None:
        ...

    def save_rollback_result(self, session_id: SessionId, result: RollbackResult) -> None:
        ...

    def save_refresh_result(self, session_id: SessionId, result: RefreshResult) -> None:
        ...

    def save_settings(self, settings: AppSettings) -> None:
        ...

    def load_settings(self) -> AppSettings:
        ...
