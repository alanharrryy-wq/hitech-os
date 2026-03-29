from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DummyProductState(str, Enum):
    REGISTERED = "registered"
    PREPARED = "prepared"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class DummyContribution:
    contribution_id: str
    slot_id: str
    surface_kind: str


class DummyProductRuntime:
    """Dummy product runtime used to validate product skeleton lifecycle."""

    product_id = "dummy_product"

    def __init__(self) -> None:
        self._state = DummyProductState.REGISTERED
        self._contribution = DummyContribution(
            contribution_id="contrib.dummy_product.main_surface",
            slot_id="primary_workspace",
            surface_kind="panel",
        )

    @property
    def state(self) -> DummyProductState:
        return self._state

    @property
    def contribution(self) -> DummyContribution:
        return self._contribution

    def prepare(self) -> DummyProductState:
        self._state = DummyProductState.PREPARED
        return self._state

    def activate(self) -> DummyProductState:
        self._state = DummyProductState.ACTIVE
        return self._state

    def suspend(self) -> DummyProductState:
        self._state = DummyProductState.SUSPENDED
        return self._state

    def dispose(self) -> DummyProductState:
        self._state = DummyProductState.DISPOSING
        self._state = DummyProductState.DISPOSED
        return self._state
