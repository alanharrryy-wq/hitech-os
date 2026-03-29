from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .exceptions import KernelRuleViolation


class SlotState(str, Enum):
    UNBOUND = "unbound"
    BOUND = "bound"
    VISIBLE = "visible"
    HIDDEN = "hidden"
    DISPOSING = "disposing"
    DISPOSED = "disposed"


@dataclass(frozen=True)
class SlotSnapshot:
    slot_id: str
    state: SlotState
    max_bindings: int
    bindings: tuple[str, ...]


@dataclass
class _SlotRecord:
    max_bindings: int
    bindings: list[str]
    state: SlotState


class SlotManager:
    """Kernel-owned slot model with explicit binding and visibility states."""

    def __init__(
        self,
        default_slot_id: str = "primary_workspace",
        default_capacity: int = 1,
    ) -> None:
        self._slots: dict[str, _SlotRecord] = {}
        self.define_slot(default_slot_id, max_bindings=default_capacity)

    def define_slot(self, slot_id: str, max_bindings: int = 1) -> None:
        if not slot_id:
            raise KernelRuleViolation("slot_id is required")
        if max_bindings < 1:
            raise KernelRuleViolation("max_bindings must be at least 1")
        if slot_id in self._slots:
            raise KernelRuleViolation(f"slot '{slot_id}' is already defined")
        self._slots[slot_id] = _SlotRecord(
            max_bindings=max_bindings,
            bindings=[],
            state=SlotState.UNBOUND,
        )

    def bind(self, slot_id: str, contribution_id: str) -> None:
        record = self._slot(slot_id)
        if record.state in {SlotState.DISPOSING, SlotState.DISPOSED}:
            raise KernelRuleViolation(f"slot '{slot_id}' cannot accept new bindings")
        if contribution_id in record.bindings:
            return
        if len(record.bindings) >= record.max_bindings:
            raise KernelRuleViolation(
                f"slot '{slot_id}' reached capacity {record.max_bindings}"
            )
        record.bindings.append(contribution_id)
        record.state = SlotState.BOUND

    def unbind(self, slot_id: str, contribution_id: str) -> None:
        record = self._slot(slot_id)
        if contribution_id not in record.bindings:
            return
        record.bindings.remove(contribution_id)
        record.state = SlotState.UNBOUND if not record.bindings else SlotState.BOUND

    def set_visibility(self, slot_id: str, visible: bool) -> None:
        record = self._slot(slot_id)
        if record.state in {SlotState.DISPOSING, SlotState.DISPOSED}:
            raise KernelRuleViolation(
                f"slot '{slot_id}' cannot change visibility in state {record.state.value}"
            )
        if not record.bindings:
            raise KernelRuleViolation(
                f"slot '{slot_id}' must have at least one binding before visibility change"
            )
        record.state = SlotState.VISIBLE if visible else SlotState.HIDDEN

    def dispose_slot(self, slot_id: str) -> None:
        record = self._slot(slot_id)
        record.state = SlotState.DISPOSING
        record.bindings.clear()
        record.state = SlotState.DISPOSED

    def snapshot(self, slot_id: str | None = None) -> list[SlotSnapshot]:
        if slot_id is not None:
            record = self._slot(slot_id)
            return [
                SlotSnapshot(
                    slot_id=slot_id,
                    state=record.state,
                    max_bindings=record.max_bindings,
                    bindings=tuple(record.bindings),
                )
            ]
        snapshots: list[SlotSnapshot] = []
        for current_slot_id, record in sorted(self._slots.items()):
            snapshots.append(
                SlotSnapshot(
                    slot_id=current_slot_id,
                    state=record.state,
                    max_bindings=record.max_bindings,
                    bindings=tuple(record.bindings),
                )
            )
        return snapshots

    def _slot(self, slot_id: str) -> _SlotRecord:
        if slot_id not in self._slots:
            raise KernelRuleViolation(f"slot '{slot_id}' is not defined")
        return self._slots[slot_id]
