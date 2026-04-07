from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.models import (
    ApplyResult,
    OpsDocument,
    PlanResult,
    RefreshResult,
    RollbackResult,
    SessionWorkspace,
    ValidationResult,
)


@dataclass(slots=True)
class EngineIoResult:
    ok: bool
    message: str
    path: str = ""


class EngineAdapter(Protocol):
    def load_ops(self, path: str) -> OpsDocument:
        ...

    def validate(self, session: SessionWorkspace) -> ValidationResult:
        ...

    def plan(self, session: SessionWorkspace) -> PlanResult:
        ...

    def apply(self, session: SessionWorkspace) -> ApplyResult:
        ...

    def rollback(self, session: SessionWorkspace, rollback_token: str = "") -> RollbackResult:
        ...

    def refresh(self, session: SessionWorkspace) -> RefreshResult:
        ...

    def save_ops(self, path: str, document: OpsDocument) -> EngineIoResult:
        ...
