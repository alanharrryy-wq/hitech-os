from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from typing import Mapping

from ..exceptions import KernelRuleViolation
from ..slot_manager import SlotManager
from ..contract_runtime import ContractRuntime
from .models import ActionInvocationResult, HostContribution


@dataclass(frozen=True)
class HostShellSnapshot:
    contribution_count: int
    slot_bindings: Mapping[str, tuple[str, ...]]


class HostShellRuntime:
    """Domain-agnostic host shell runtime for contributions and slot wiring."""

    _contribution_register_contract = "forge.contribution.surface.register.v1"
    _contribution_invoke_contract = "forge.contribution.action.invoke.v1"
    _slot_bind_contract = "forge.command.host.slot_bind.v1"
    _slot_unbind_contract = "forge.command.host.slot_unbind.v1"

    def __init__(self, slots: SlotManager, contracts: ContractRuntime) -> None:
        self._slots = slots
        self._contracts = contracts
        self._contributions: dict[str, HostContribution] = {}

    def register_contribution(
        self,
        contribution: HostContribution,
        actor: str,
        correlation_id: str,
    ) -> None:
        if contribution.contribution_id in self._contributions:
            raise KernelRuleViolation(
                f"contribution '{contribution.contribution_id}' already exists"
            )
        payload = {
            "contribution_id": contribution.contribution_id,
            "slot_id": contribution.slot_id,
            "product_id": contribution.product_id,
            "surface_kind": contribution.surface_kind,
        }
        self._contracts.validate_request(
            contract_id=self._contribution_register_contract,
            payload=payload,
            actor=actor,
            correlation_id=correlation_id,
        )
        self._contracts.validate_request(
            contract_id=self._slot_bind_contract,
            payload={
                "slot_id": contribution.slot_id,
                "contribution_id": contribution.contribution_id,
            },
            actor=actor,
            correlation_id=correlation_id,
        )
        self._slots.bind(contribution.slot_id, contribution.contribution_id)
        self._contributions[contribution.contribution_id] = contribution
        self._contracts.validate_response(
            contract_id=self._contribution_register_contract,
            payload={"accepted": True},
            actor=actor,
            correlation_id=correlation_id,
        )

    def set_visible(self, slot_id: str, visible: bool) -> None:
        self._slots.set_visibility(slot_id=slot_id, visible=visible)

    def invoke_action(
        self,
        contribution_id: str,
        action_id: str,
        actor: str,
        correlation_id: str,
        timeout_seconds: float = 1.0,
    ) -> ActionInvocationResult:
        contribution = self._contributions.get(contribution_id)
        if contribution is None:
            raise KernelRuleViolation(f"unknown contribution '{contribution_id}'")
        action = contribution.actions.get(action_id)
        if action is None:
            raise KernelRuleViolation(
                f"unknown action '{action_id}' for '{contribution_id}'"
            )
        self._contracts.validate_request(
            contract_id=self._contribution_invoke_contract,
            payload={"contribution_id": contribution_id, "action_id": action_id},
            actor=actor,
            correlation_id=correlation_id,
        )
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(action)
            try:
                value = future.result(timeout=timeout_seconds)
                self._contracts.validate_response(
                    contract_id=self._contribution_invoke_contract,
                    payload={"status": "completed"},
                    actor=actor,
                    correlation_id=correlation_id,
                )
                return ActionInvocationResult(
                    contribution_id=contribution_id,
                    action_id=action_id,
                    status="completed",
                    value=value,
                    error=None,
                )
            except TimeoutError:
                future.cancel()
                self._contracts.build_error(
                    contract_id=self._contribution_invoke_contract,
                    correlation_id=correlation_id,
                    error_code="action_timeout",
                    message="contribution action exceeded timeout",
                    actor=actor,
                    classification="timeout",
                    retryable=True,
                    details={"contribution_id": contribution_id, "action_id": action_id},
                )
                return ActionInvocationResult(
                    contribution_id=contribution_id,
                    action_id=action_id,
                    status="timed_out",
                    value=None,
                    error="timeout",
                )
            except Exception as exc:  # noqa: BLE001
                self._contracts.build_error(
                    contract_id=self._contribution_invoke_contract,
                    correlation_id=correlation_id,
                    error_code="action_failed",
                    message=str(exc),
                    actor=actor,
                    classification="runtime_error",
                    retryable=False,
                    details={"contribution_id": contribution_id, "action_id": action_id},
                )
                return ActionInvocationResult(
                    contribution_id=contribution_id,
                    action_id=action_id,
                    status="failed",
                    value=None,
                    error=str(exc),
                )

    def unregister_contribution(
        self,
        contribution_id: str,
        actor: str,
        correlation_id: str,
    ) -> None:
        contribution = self._contributions.get(contribution_id)
        if contribution is None:
            return
        self._contracts.validate_request(
            contract_id=self._slot_unbind_contract,
            payload={
                "slot_id": contribution.slot_id,
                "contribution_id": contribution.contribution_id,
            },
            actor=actor,
            correlation_id=correlation_id,
        )
        self._slots.unbind(contribution.slot_id, contribution.contribution_id)
        self._contributions.pop(contribution_id, None)

    def dispose(self, actor: str, correlation_id: str) -> None:
        contribution_ids = sorted(self._contributions.keys())
        for contribution_id in contribution_ids:
            self.unregister_contribution(
                contribution_id=contribution_id,
                actor=actor,
                correlation_id=correlation_id,
            )

    def snapshot(self) -> HostShellSnapshot:
        slot_map: dict[str, tuple[str, ...]] = {}
        for slot in self._slots.snapshot():
            slot_map[slot.slot_id] = slot.bindings
        return HostShellSnapshot(
            contribution_count=len(self._contributions),
            slot_bindings=slot_map,
        )
