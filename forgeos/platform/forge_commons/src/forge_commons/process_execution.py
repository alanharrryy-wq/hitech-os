from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone

from forge_kernel import ContractRuntime

from .lifecycle import CapabilityLifecycle, CapabilityRuntimeState


@dataclass(frozen=True)
class ProcessExecutionRecord:
    command: tuple[str, ...]
    status: str
    return_code: int | None
    stdout: str
    stderr: str
    started_at_utc: str
    finished_at_utc: str
    duration_ms: int


class ProcessExecutionCapability:
    """Shared process execution capability with timeout and state event validation."""

    capability_id = "forge.commons.process_execution"
    _execute_contract_id = "forge.capability.process.execute.v1"
    _state_event_contract_id = "forge.event.process.state_changed.v1"

    def __init__(self, contracts: ContractRuntime) -> None:
        self.lifecycle = CapabilityLifecycle(self.capability_id)
        self._contracts = contracts
        self._records: list[ProcessExecutionRecord] = []

    def activate(self) -> CapabilityRuntimeState:
        return self.lifecycle.activate()

    def dispose(self) -> CapabilityRuntimeState:
        self._records.clear()
        return self.lifecycle.dispose()

    def execute(
        self,
        command: list[str],
        actor: str,
        correlation_id: str,
        timeout_seconds: float = 30.0,
    ) -> ProcessExecutionRecord:
        self._contracts.validate_request(
            contract_id=self._execute_contract_id,
            payload={"command": command, "timeout_seconds": timeout_seconds},
            actor=actor,
            correlation_id=correlation_id,
        )
        self._emit_state_event("requested", actor, correlation_id)
        started = datetime.now(tz=timezone.utc)
        self._emit_state_event("spawned", actor, correlation_id)
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            finished = datetime.now(tz=timezone.utc)
            status = "finished" if completed.returncode == 0 else "failed"
            self._emit_state_event(status, actor, correlation_id)
            record = ProcessExecutionRecord(
                command=tuple(command),
                status=status,
                return_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                started_at_utc=started.isoformat(),
                finished_at_utc=finished.isoformat(),
                duration_ms=int((finished - started).total_seconds() * 1000),
            )
        except subprocess.TimeoutExpired as timeout:
            finished = datetime.now(tz=timezone.utc)
            self._emit_state_event("timed_out", actor, correlation_id)
            record = ProcessExecutionRecord(
                command=tuple(command),
                status="timed_out",
                return_code=None,
                stdout=timeout.stdout or "",
                stderr=timeout.stderr or "",
                started_at_utc=started.isoformat(),
                finished_at_utc=finished.isoformat(),
                duration_ms=int((finished - started).total_seconds() * 1000),
            )
        self._contracts.validate_response(
            contract_id=self._execute_contract_id,
            payload={
                "status": record.status,
                "return_code": record.return_code,
                "duration_ms": record.duration_ms,
            },
            actor=actor,
            correlation_id=correlation_id,
        )
        self._records.append(record)
        return record

    def ledger(self) -> list[ProcessExecutionRecord]:
        return list(self._records)

    def _emit_state_event(self, state: str, actor: str, correlation_id: str) -> None:
        self._contracts.validate_request(
            contract_id=self._state_event_contract_id,
            payload={"state": state, "source": self.capability_id},
            actor=actor,
            correlation_id=correlation_id,
        )
