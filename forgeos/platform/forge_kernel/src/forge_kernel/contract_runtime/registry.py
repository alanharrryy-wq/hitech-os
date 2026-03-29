from __future__ import annotations

from datetime import datetime, timezone

from ..exceptions import KernelRuleViolation
from .error_envelope import ContractErrorEnvelope, build_error_envelope
from .models import ContractDefinition, ContractRequestEnvelope, ContractResponseEnvelope
from .observability import ContractObserver, build_observation
from .validator import ContractValidator


class ContractRegistry:
    """Kernel-owned registry for contract definitions."""

    def __init__(self, validator: ContractValidator) -> None:
        self._validator = validator
        self._definitions: dict[str, ContractDefinition] = {}

    def register(self, definition: ContractDefinition) -> None:
        self._validator.validate_definition(definition)
        if definition.contract_id in self._definitions:
            raise KernelRuleViolation(
                f"contract '{definition.contract_id}' is already registered"
            )
        self._definitions[definition.contract_id] = definition

    def definition(self, contract_id: str) -> ContractDefinition:
        if contract_id not in self._definitions:
            raise KernelRuleViolation(f"unknown contract '{contract_id}'")
        return self._definitions[contract_id]

    def known_contracts(self) -> list[ContractDefinition]:
        return [self._definitions[key] for key in sorted(self._definitions.keys())]


class ContractRuntime:
    """Contract runtime with registration, validation, and observability hooks."""

    def __init__(self, validator: ContractValidator, observer: ContractObserver) -> None:
        self._validator = validator
        self._observer = observer
        self._registry = ContractRegistry(validator=validator)

    def register_contract(self, definition: ContractDefinition, actor: str) -> None:
        self._registry.register(definition)
        self._observer.on_observation(
            build_observation(
                event_type="contract_registered",
                contract_id=definition.contract_id,
                correlation_id="registration",
                actor=actor,
                outcome="accepted",
                metadata={"family": definition.family.value, "version": str(definition.version)},
            )
        )

    def validate_request(
        self,
        contract_id: str,
        payload: dict[str, object],
        actor: str,
        correlation_id: str,
    ) -> ContractRequestEnvelope:
        definition = self._registry.definition(contract_id)
        envelope = ContractRequestEnvelope(
            contract_id=contract_id,
            version=definition.version,
            payload=payload,
            metadata={"actor": actor},
            correlation_id=correlation_id,
            issued_at_utc=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._validator.validate_request_envelope(envelope, expected_version=definition.version)
        self._observer.on_observation(
            build_observation(
                event_type="contract_request_validated",
                contract_id=contract_id,
                correlation_id=correlation_id,
                actor=actor,
                outcome="accepted",
                metadata={"family": definition.family.value},
            )
        )
        return envelope

    def validate_response(
        self,
        contract_id: str,
        payload: dict[str, object],
        actor: str,
        correlation_id: str,
    ) -> ContractResponseEnvelope:
        definition = self._registry.definition(contract_id)
        envelope = ContractResponseEnvelope(
            contract_id=contract_id,
            version=definition.version,
            payload=payload,
            metadata={"actor": actor},
            correlation_id=correlation_id,
            issued_at_utc=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._validator.validate_response_envelope(
            envelope, expected_version=definition.version
        )
        self._observer.on_observation(
            build_observation(
                event_type="contract_response_validated",
                contract_id=contract_id,
                correlation_id=correlation_id,
                actor=actor,
                outcome="accepted",
                metadata={"family": definition.family.value},
            )
        )
        return envelope

    def build_error(
        self,
        contract_id: str,
        correlation_id: str,
        error_code: str,
        message: str,
        actor: str,
        classification: str = "runtime_error",
        retryable: bool = False,
        details: dict[str, object] | None = None,
    ) -> ContractErrorEnvelope:
        error = build_error_envelope(
            contract_id=contract_id,
            error_code=error_code,
            message=message,
            classification=classification,
            retryable=retryable,
            details=details or {},
            correlation_id=correlation_id,
        )
        self._observer.on_observation(
            build_observation(
                event_type="contract_error_emitted",
                contract_id=contract_id,
                correlation_id=correlation_id,
                actor=actor,
                outcome="error",
                metadata={"error_code": error_code, "classification": classification},
            )
        )
        return error

    def known_contracts(self) -> list[ContractDefinition]:
        return self._registry.known_contracts()
