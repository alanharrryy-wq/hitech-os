from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from forge_kernel import ContractRuntime

from .lifecycle import CapabilityLifecycle, CapabilityRuntimeState


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    producer: str
    status: str
    details: Mapping[str, str]
    appended_at_utc: str


class HistoryRunsCapability:
    """Shared run ledger capability."""

    capability_id = "forge.commons.history_runs"
    _append_contract_id = "forge.capability.runs.append.v1"

    def __init__(self, contracts: ContractRuntime) -> None:
        self.lifecycle = CapabilityLifecycle(self.capability_id)
        self._contracts = contracts
        self._runs: list[RunRecord] = []

    def activate(self) -> CapabilityRuntimeState:
        return self.lifecycle.activate()

    def dispose(self) -> CapabilityRuntimeState:
        self._runs.clear()
        return self.lifecycle.dispose()

    def append(
        self,
        run_id: str,
        producer: str,
        status: str,
        actor: str,
        correlation_id: str,
        details: Mapping[str, str] | None = None,
    ) -> RunRecord:
        payload = {
            "run_id": run_id,
            "producer": producer,
            "status": status,
        }
        self._contracts.validate_request(
            contract_id=self._append_contract_id,
            payload=payload,
            actor=actor,
            correlation_id=correlation_id,
        )
        record = RunRecord(
            run_id=run_id,
            producer=producer,
            status=status,
            details=details or {},
            appended_at_utc=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._runs.append(record)
        self._contracts.validate_response(
            contract_id=self._append_contract_id,
            payload={"accepted": True, "run_id": run_id},
            actor=actor,
            correlation_id=correlation_id,
        )
        return record

    def all_runs(self) -> list[RunRecord]:
        return list(self._runs)
