from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping


@dataclass(frozen=True)
class HostContribution:
    contribution_id: str
    slot_id: str
    product_id: str
    surface_kind: str
    metadata: Mapping[str, str]
    actions: Mapping[str, Callable[[], object]]


@dataclass(frozen=True)
class ActionInvocationResult:
    contribution_id: str
    action_id: str
    status: str
    value: object | None
    error: str | None
