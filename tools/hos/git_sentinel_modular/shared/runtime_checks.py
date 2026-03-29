from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .contracts import CONTRACT_VERSION, validate_contract_version
from .errors import ProviderRegistrationError, WiringError
from .foundation import SentinelEnvironment, SentinelPaths, assert_phase_docs_present, ensure_required_layout
from .interfaces import DEFAULT_PROVIDER_SPECS, ProviderBinding, ProviderSpec, provider_specs_by_name


@dataclass(slots=True)
class RuntimeCheckFinding:
    level: str
    code: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StartupDoctorResult:
    ok: bool
    findings: list[RuntimeCheckFinding]
    checked_contract_version: str
    paths: dict[str, str]
    environment: dict[str, str]

    def errors(self) -> list[RuntimeCheckFinding]:
        return [f for f in self.findings if f.level == "ERROR"]


class ProviderRegistry:
    def __init__(self, specs: tuple[ProviderSpec, ...] = DEFAULT_PROVIDER_SPECS):
        self._specs = {spec.name: spec for spec in specs}
        self._bindings: dict[str, ProviderBinding] = {}

    def register(self, name: str, provider: object, **metadata: Any) -> ProviderBinding:
        if name not in self._specs:
            raise ProviderRegistrationError(
                "Unknown provider name.",
                provider_name=name,
                known_providers=sorted(self._specs),
            )
        spec = self._specs[name]
        if provider is None:
            raise ProviderRegistrationError("Provider cannot be None.", provider_name=name)

        if not isinstance(provider, spec.expected_protocol):
            raise ProviderRegistrationError(
                "Provider does not satisfy expected protocol.",
                provider_name=name,
                expected_protocol=spec.expected_protocol.__name__,
                actual_type=type(provider).__name__,
            )

        binding = ProviderBinding(spec=spec, provider=provider, metadata=dict(metadata)).validate()
        self._bindings[name] = binding
        return binding

    def resolve(self, name: str) -> object:
        if name not in self._bindings:
            raise WiringError("Provider not registered.", provider_name=name)
        return self._bindings[name].provider

    def bindings(self) -> dict[str, ProviderBinding]:
        return dict(self._bindings)

    def validate_required_bindings(self) -> list[RuntimeCheckFinding]:
        findings: list[RuntimeCheckFinding] = []
        for spec in self._specs.values():
            if spec.name not in self._bindings:
                if spec.optional:
                    findings.append(
                        RuntimeCheckFinding(
                            level="WARN",
                            code="OPTIONAL_PROVIDER_MISSING",
                            message=f"Optional provider `{spec.name}` is not registered.",
                            context={"provider_name": spec.name},
                        )
                    )
                else:
                    findings.append(
                        RuntimeCheckFinding(
                            level="ERROR",
                            code="REQUIRED_PROVIDER_MISSING",
                            message=f"Required provider `{spec.name}` is not registered.",
                            context={"provider_name": spec.name},
                        )
                    )
        return findings


def validate_contract_runtime() -> list[RuntimeCheckFinding]:
    findings: list[RuntimeCheckFinding] = []
    try:
        validate_contract_version(CONTRACT_VERSION)
    except Exception as exc:
        findings.append(
            RuntimeCheckFinding(
                level="ERROR",
                code="CONTRACT_VERSION_INVALID",
                message=str(exc),
                context={"contract_version": CONTRACT_VERSION},
            )
        )
    return findings


def validate_paths(paths: SentinelPaths) -> list[RuntimeCheckFinding]:
    findings: list[RuntimeCheckFinding] = []
    ensure_required_layout(paths)
    try:
        assert_phase_docs_present(paths)
    except Exception as exc:
        findings.append(
            RuntimeCheckFinding(
                level="ERROR",
                code="PHASE_DOCS_MISSING",
                message=str(exc),
                context={"phase": "phase_01"},
            )
        )
    return findings


def validate_wiring(registry: ProviderRegistry) -> list[RuntimeCheckFinding]:
    return registry.validate_required_bindings()


def run_startup_doctor(paths: SentinelPaths, registry: ProviderRegistry) -> StartupDoctorResult:
    findings: list[RuntimeCheckFinding] = []
    findings.extend(validate_contract_runtime())
    findings.extend(validate_paths(paths))
    findings.extend(validate_wiring(registry))

    ok = not any(item.level == "ERROR" for item in findings)
    env = SentinelEnvironment.capture()
    return StartupDoctorResult(
        ok=ok,
        findings=findings,
        checked_contract_version=CONTRACT_VERSION,
        paths=paths.to_dict(),
        environment={
            "python_executable": env.python_executable,
            "platform_name": env.platform_name,
            "working_directory": env.working_directory,
            "generated_at": env.generated_at,
        },
    )


def require_doctor_ok(result: StartupDoctorResult) -> StartupDoctorResult:
    if not result.ok:
        first = result.errors()[0]
        raise WiringError(
            "Startup doctor failed.",
            code=first.code,
            message=first.message,
            context=first.context,
        )
    return result
