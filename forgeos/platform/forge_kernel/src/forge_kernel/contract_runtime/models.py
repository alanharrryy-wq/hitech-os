from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ContractFamily(str, Enum):
    LIFECYCLE = "lifecycle"
    STATE = "state"
    COMMAND = "command"
    EVENT = "event"
    CONTRIBUTION = "contribution"
    CAPABILITY_SERVICE = "capability_service"
    PERSISTENCE = "persistence"
    PACKAGING = "packaging"
    COMPATIBILITY = "compatibility"


@dataclass(frozen=True)
class ContractDefinition:
    contract_id: str
    family: ContractFamily
    owner: str
    version: int
    request_schema_version: int
    response_schema_version: int
    error_schema_version: int
    timeout_ms: int
    observability_required: tuple[str, ...]


@dataclass(frozen=True)
class ContractRequestEnvelope:
    contract_id: str
    version: int
    payload: Mapping[str, object]
    metadata: Mapping[str, str]
    correlation_id: str
    issued_at_utc: str


@dataclass(frozen=True)
class ContractResponseEnvelope:
    contract_id: str
    version: int
    payload: Mapping[str, object]
    metadata: Mapping[str, str]
    correlation_id: str
    issued_at_utc: str
