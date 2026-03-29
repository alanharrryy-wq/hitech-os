from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping


@dataclass(frozen=True)
class ContractErrorEnvelope:
    contract_id: str
    error_code: str
    message: str
    classification: str
    retryable: bool
    details: Mapping[str, object]
    correlation_id: str
    occurred_at_utc: str


def build_error_envelope(
    contract_id: str,
    error_code: str,
    message: str,
    classification: str,
    retryable: bool,
    details: Mapping[str, object],
    correlation_id: str,
) -> ContractErrorEnvelope:
    return ContractErrorEnvelope(
        contract_id=contract_id,
        error_code=error_code,
        message=message,
        classification=classification,
        retryable=retryable,
        details=details,
        correlation_id=correlation_id,
        occurred_at_utc=datetime.now(tz=timezone.utc).isoformat(),
    )
