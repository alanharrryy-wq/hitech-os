from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from deltaforge.domain.models.ops_document import OpsDocument
from deltaforge.domain.models.plan import PlanResult
from deltaforge.domain.models.results import (
    ApplyResult,
    EventLogEntry,
    RefreshResult,
    RollbackResult,
    ValidationResult,
)
from deltaforge.domain.models.scope import ScopeSelection
from deltaforge.domain.session_states import SessionState


@dataclass(slots=True)
class SessionSelection:
    file_path: str = ""
    plan_step_id: str = ""


@dataclass(slots=True)
class SessionWorkspace:
    session_id: str
    title: str
    scope: ScopeSelection = field(default_factory=ScopeSelection)
    ops_document: OpsDocument = field(default_factory=OpsDocument)
    state: SessionState = SessionState.EMPTY
    mode: str = "mock"
    stale: bool = False
    dirty: bool = False
    is_busy: bool = False

    selection: SessionSelection = field(default_factory=SessionSelection)
    log_entries: list[EventLogEntry] = field(default_factory=list)

    validation_result: ValidationResult | None = None
    plan_result: PlanResult | None = None
    apply_result: ApplyResult | None = None
    rollback_result: RollbackResult | None = None
    refresh_result: RefreshResult | None = None
    rollback_tokens: list[str] = field(default_factory=list)

    def set_state(self, state: SessionState) -> None:
        self.state = state

    def add_log(self, category: str, message: str) -> None:
        self.log_entries.append(EventLogEntry(category=category, message=message))

    def clone_for_new_session(self, *, session_id: str, title: str) -> "SessionWorkspace":
        cloned = SessionWorkspace(
            session_id=session_id,
            title=title,
            scope=deepcopy(self.scope),
            ops_document=deepcopy(self.ops_document),
            state=self.state,
            mode=self.mode,
            stale=self.stale,
            dirty=self.dirty,
            selection=deepcopy(self.selection),
            log_entries=deepcopy(self.log_entries),
            validation_result=deepcopy(self.validation_result),
            plan_result=deepcopy(self.plan_result),
            apply_result=deepcopy(self.apply_result),
            rollback_result=deepcopy(self.rollback_result),
            refresh_result=deepcopy(self.refresh_result),
            rollback_tokens=deepcopy(self.rollback_tokens),
        )
        cloned.is_busy = False
        return cloned
