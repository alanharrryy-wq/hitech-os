from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol


@dataclass(frozen=True)
class ContractObservation:
    event_type: str
    contract_id: str
    correlation_id: str
    actor: str
    outcome: str
    metadata: Mapping[str, str]
    observed_at_utc: str


class ContractObserver(Protocol):
    def on_observation(self, observation: ContractObservation) -> None:
        pass


class InMemoryContractObserver:
    """Observability hook for audits and tests."""

    def __init__(self) -> None:
        self._events: list[ContractObservation] = []

    def on_observation(self, observation: ContractObservation) -> None:
        self._events.append(observation)

    def snapshot(self) -> list[ContractObservation]:
        return list(self._events)


def build_observation(
    event_type: str,
    contract_id: str,
    correlation_id: str,
    actor: str,
    outcome: str,
    metadata: Mapping[str, str],
) -> ContractObservation:
    return ContractObservation(
        event_type=event_type,
        contract_id=contract_id,
        correlation_id=correlation_id,
        actor=actor,
        outcome=outcome,
        metadata=metadata,
        observed_at_utc=datetime.now(tz=timezone.utc).isoformat(),
    )
