from __future__ import annotations

from typing import NewType
from uuid import uuid4

SessionId = NewType("SessionId", str)
ScopeId = NewType("ScopeId", str)


def parse_session_id(raw: SessionId | str) -> SessionId:
    value = str(raw).strip()
    if not value:
        raise ValueError("SessionId cannot be empty.")
    return SessionId(value)


def parse_scope_id(raw: ScopeId | str) -> ScopeId:
    value = str(raw).strip()
    if not value:
        raise ValueError("ScopeId cannot be empty.")
    return ScopeId(value)


def new_session_id(sequence: int | None = None, *, prefix: str = "s") -> SessionId:
    if sequence is None:
        return SessionId(f"{prefix}_{uuid4().hex[:10]}")
    if sequence < 1:
        raise ValueError("Session sequence must be >= 1.")
    return SessionId(f"{prefix}{sequence:03d}")


def new_scope_id(*, prefix: str = "scp") -> ScopeId:
    return ScopeId(f"{prefix}_{uuid4().hex[:12]}")
