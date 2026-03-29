from __future__ import annotations

from dataclasses import dataclass

from .contract_runtime import (
    ContractRuntime,
    ContractValidator,
    InMemoryContractObserver,
    register_wave1_contracts,
)
from .host_shell import HostShellRuntime
from .lifecycle_authority import LifecycleAuthority
from .packaging_gate import PackagingGate
from .slot_manager import SlotManager
from .state_authority_registry import StateAuthorityRegistry


@dataclass
class KernelSession:
    kernel_version: str
    lifecycle: LifecycleAuthority
    contracts: ContractRuntime
    slots: SlotManager
    host_shell: HostShellRuntime
    state_authority: StateAuthorityRegistry
    packaging_gate: PackagingGate


class KernelBootstrap:
    """Entry point that composes phase-1 kernel authorities."""

    @staticmethod
    def start(kernel_version: str = "0.1.0") -> KernelSession:
        lifecycle = LifecycleAuthority()
        contracts = ContractRuntime(
            validator=ContractValidator(),
            observer=InMemoryContractObserver(),
        )
        register_wave1_contracts(runtime=contracts, actor="kernel.bootstrap")
        slots = SlotManager(default_slot_id="primary_workspace", default_capacity=1)
        host_shell = HostShellRuntime(slots=slots, contracts=contracts)
        state_authority = StateAuthorityRegistry()
        packaging_gate = PackagingGate()
        return KernelSession(
            kernel_version=kernel_version,
            lifecycle=lifecycle,
            contracts=contracts,
            slots=slots,
            host_shell=host_shell,
            state_authority=state_authority,
            packaging_gate=packaging_gate,
        )
