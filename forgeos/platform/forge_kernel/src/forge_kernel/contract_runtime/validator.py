from __future__ import annotations

import re

from ..exceptions import KernelRuleViolation
from .models import ContractDefinition, ContractRequestEnvelope, ContractResponseEnvelope

_CONTRACT_ID_PATTERN = re.compile(r"^forge\.[a-z0-9_]+\.[a-z0-9_.]+\.(v[1-9][0-9]*)$")
_FAMILY_PREFIX: dict[str, str] = {
    "lifecycle": "lifecycle",
    "state": "state",
    "command": "command",
    "event": "event",
    "contribution": "contribution",
    "capability_service": "capability",
    "persistence": "persistence",
    "packaging": "packaging",
    "compatibility": "compatibility",
}


class ContractValidator:
    """Validation rules for contract metadata and envelopes."""

    def validate_definition(self, definition: ContractDefinition) -> None:
        problems: list[str] = []
        if not _CONTRACT_ID_PATTERN.match(definition.contract_id):
            problems.append(f"invalid contract_id '{definition.contract_id}'")
        expected_prefix = _FAMILY_PREFIX[definition.family.value]
        actual_prefix = definition.contract_id.split(".")[1]
        if expected_prefix != actual_prefix:
            problems.append(
                "contract_id family prefix mismatch: "
                f"expected '{expected_prefix}', got '{actual_prefix}'"
            )
        if definition.version < 1:
            problems.append("version must be >= 1")
        if definition.request_schema_version < 1:
            problems.append("request_schema_version must be >= 1")
        if definition.response_schema_version < 1:
            problems.append("response_schema_version must be >= 1")
        if definition.error_schema_version < 1:
            problems.append("error_schema_version must be >= 1")
        if definition.timeout_ms <= 0:
            problems.append("timeout_ms must be > 0")
        if not definition.owner:
            problems.append("owner is required")
        if not definition.observability_required:
            problems.append("observability_required cannot be empty")
        if problems:
            raise KernelRuleViolation("; ".join(problems))

    def validate_request_envelope(
        self,
        envelope: ContractRequestEnvelope,
        expected_version: int,
    ) -> None:
        self._validate_envelope_version(envelope.version, expected_version)
        if not envelope.correlation_id:
            raise KernelRuleViolation("correlation_id is required")
        if not envelope.issued_at_utc:
            raise KernelRuleViolation("issued_at_utc is required")

    def validate_response_envelope(
        self,
        envelope: ContractResponseEnvelope,
        expected_version: int,
    ) -> None:
        self._validate_envelope_version(envelope.version, expected_version)
        if not envelope.correlation_id:
            raise KernelRuleViolation("correlation_id is required")
        if not envelope.issued_at_utc:
            raise KernelRuleViolation("issued_at_utc is required")

    def _validate_envelope_version(self, actual: int, expected: int) -> None:
        if actual != expected:
            raise KernelRuleViolation(
                f"envelope version mismatch: got {actual}, expected {expected}"
            )
