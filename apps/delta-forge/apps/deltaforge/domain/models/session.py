from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from domain.ids import SessionId, parse_session_id
from domain.models.ops_document import OpsDocument
from domain.models.plan import PlanResult
from domain.models.results import (
    ApplyResult,
    EventLogEntry,
    RefreshResult,
    RollbackResult,
    ValidationResult,
)
from domain.models.scope import ScopeSelection
from domain.session_states import SessionState


@dataclass(slots=True)
class SessionSelection:
    file_path: str = ""
    plan_step_id: str = ""
    target_path: str = ""


@dataclass(slots=True)
class SessionWorkspace:
    session_id: SessionId | str
    title: str
    scope: ScopeSelection = field(default_factory=ScopeSelection)
    ops_document: OpsDocument = field(default_factory=OpsDocument)
    state: SessionState = SessionState.EMPTY
    mode: str = "local"
    stale: bool = False
    dirty: bool = False
    busy: bool = False

    selection: SessionSelection = field(default_factory=SessionSelection)
    event_feed: list[EventLogEntry] = field(default_factory=list)

    validation_result: ValidationResult | None = None
    plan_result: PlanResult | None = None
    apply_result: ApplyResult | None = None
    rollback_result: RollbackResult | None = None
    refresh_result: RefreshResult | None = None
    rollback_tokens: list[str] = field(default_factory=list)
    rollback_token: str = ""
    refresh_origin_state: SessionState | None = None
    ops_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.session_id = parse_session_id(self.session_id)
        self.state = SessionState(self.state)
        if not self.ops_metadata:
            self.ops_metadata = self.ops_document.summary_payload()

    @property
    def is_busy(self) -> bool:
        return self.busy

    @is_busy.setter
    def is_busy(self, value: bool) -> None:
        self.busy = bool(value)

    @property
    def log_entries(self) -> list[EventLogEntry]:
        return self.event_feed

    def set_state(self, state: SessionState) -> None:
        self.state = SessionState(state)

    def set_busy(self, value: bool) -> None:
        self.busy = bool(value)

    def sync_ops_metadata(self) -> dict[str, Any]:
        self.ops_metadata = self.ops_document.summary_payload()
        return dict(self.ops_metadata)

    def add_event(self, event: EventLogEntry) -> None:
        entry = deepcopy(event)
        entry.session_id = self.session_id
        self.event_feed.append(entry)

    def add_log(self, category: str, message: str) -> None:
        self.event_feed.append(
            EventLogEntry(
                category=category,
                message=message,
                session_id=self.session_id,
            )
        )

    def clone_for_new_session(self, *, session_id: SessionId | str, title: str) -> "SessionWorkspace":
        cloned = SessionWorkspace(
            session_id=session_id,
            title=title,
            scope=deepcopy(self.scope),
            ops_document=deepcopy(self.ops_document),
            state=self.state,
            mode=self.mode,
            stale=self.stale,
            dirty=self.dirty,
            busy=False,
            selection=deepcopy(self.selection),
            event_feed=deepcopy(self.event_feed),
            validation_result=deepcopy(self.validation_result),
            plan_result=deepcopy(self.plan_result),
            apply_result=deepcopy(self.apply_result),
            rollback_result=deepcopy(self.rollback_result),
            refresh_result=deepcopy(self.refresh_result),
            rollback_tokens=deepcopy(self.rollback_tokens),
            rollback_token=self.rollback_token,
            refresh_origin_state=self.refresh_origin_state,
            ops_metadata=deepcopy(self.ops_metadata),
        )
        return cloned
