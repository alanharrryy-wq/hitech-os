import unittest

from forge_kernel import (
    ContractDefinition,
    ContractFamily,
    ContractRuntime,
    ContractValidator,
    InMemoryContractObserver,
    KernelRuleViolation,
    WAVE1_CONTRACTS,
    register_wave1_contracts,
)


class ContractRuntimeTests(unittest.TestCase):
    def test_register_and_validate_roundtrip(self) -> None:
        observer = InMemoryContractObserver()
        runtime = ContractRuntime(validator=ContractValidator(), observer=observer)
        runtime.register_contract(
            ContractDefinition(
                contract_id="forge.lifecycle.package.register.v1",
                family=ContractFamily.LIFECYCLE,
                owner="forge_kernel",
                version=1,
                request_schema_version=1,
                response_schema_version=1,
                error_schema_version=1,
                timeout_ms=5000,
                observability_required=("contract_id", "correlation_id", "outcome"),
            ),
            actor="kernel.bootstrap",
        )
        request = runtime.validate_request(
            contract_id="forge.lifecycle.package.register.v1",
            payload={"package_id": "pkg.kernel.base"},
            actor="kernel.bootstrap",
            correlation_id="corr-001",
        )
        response = runtime.validate_response(
            contract_id="forge.lifecycle.package.register.v1",
            payload={"status": "accepted"},
            actor="kernel.bootstrap",
            correlation_id="corr-001",
        )
        self.assertEqual(request.version, 1)
        self.assertEqual(response.version, 1)
        self.assertEqual(len(observer.snapshot()), 3)

    def test_duplicate_contract_rejected(self) -> None:
        runtime = ContractRuntime(
            validator=ContractValidator(),
            observer=InMemoryContractObserver(),
        )
        definition = ContractDefinition(
            contract_id="forge.command.host.slot_bind.v1",
            family=ContractFamily.COMMAND,
            owner="forge_kernel",
            version=1,
            request_schema_version=1,
            response_schema_version=1,
            error_schema_version=1,
            timeout_ms=3000,
            observability_required=("contract_id", "correlation_id", "outcome"),
        )
        runtime.register_contract(definition, actor="kernel.bootstrap")
        with self.assertRaises(KernelRuleViolation):
            runtime.register_contract(definition, actor="kernel.bootstrap")

    def test_error_envelope_emits_observation(self) -> None:
        observer = InMemoryContractObserver()
        runtime = ContractRuntime(validator=ContractValidator(), observer=observer)
        runtime.register_contract(
            ContractDefinition(
                contract_id="forge.event.package.faulted.v1",
                family=ContractFamily.EVENT,
                owner="forge_kernel",
                version=1,
                request_schema_version=1,
                response_schema_version=1,
                error_schema_version=1,
                timeout_ms=1000,
                observability_required=("contract_id", "correlation_id", "outcome"),
            ),
            actor="kernel.bootstrap",
        )
        error = runtime.build_error(
            contract_id="forge.event.package.faulted.v1",
            correlation_id="corr-err-1",
            error_code="runtime_fault",
            message="faulted",
            actor="kernel.lifecycle",
        )
        self.assertEqual(error.error_code, "runtime_fault")
        self.assertGreaterEqual(len(observer.snapshot()), 2)

    def test_wave1_catalog_registration_count(self) -> None:
        runtime = ContractRuntime(
            validator=ContractValidator(),
            observer=InMemoryContractObserver(),
        )
        register_wave1_contracts(runtime=runtime, actor="kernel.bootstrap")
        self.assertEqual(len(runtime.known_contracts()), len(WAVE1_CONTRACTS))


if __name__ == "__main__":
    unittest.main()
