from __future__ import annotations

from dataclasses import dataclass

from .exceptions import KernelRuleViolation


@dataclass(frozen=True)
class StateSliceAuthority:
    slice_id: str
    owner: str
    source_of_truth: str
    readers: tuple[str, ...]
    writers: tuple[str, ...]


class StateAuthorityRegistry:
    """Registry for state ownership and read/write authority."""

    def __init__(self) -> None:
        self._slices: dict[str, StateSliceAuthority] = {}

    def register(self, authority: StateSliceAuthority) -> None:
        if not authority.slice_id:
            raise KernelRuleViolation("slice_id is required")
        if authority.slice_id in self._slices:
            raise KernelRuleViolation(
                f"state slice '{authority.slice_id}' is already registered"
            )
        if authority.owner not in authority.writers:
            raise KernelRuleViolation(
                f"owner '{authority.owner}' must be part of writers for '{authority.slice_id}'"
            )
        self._slices[authority.slice_id] = authority

    def authority_for(self, slice_id: str) -> StateSliceAuthority:
        if slice_id not in self._slices:
            raise KernelRuleViolation(f"state slice '{slice_id}' is not registered")
        return self._slices[slice_id]

    def can_write(self, slice_id: str, actor: str) -> bool:
        authority = self.authority_for(slice_id)
        return actor in authority.writers

    def can_read(self, slice_id: str, actor: str) -> bool:
        authority = self.authority_for(slice_id)
        return actor in authority.readers or actor in authority.writers

    def snapshot(self) -> list[StateSliceAuthority]:
        return [self._slices[key] for key in sorted(self._slices.keys())]
