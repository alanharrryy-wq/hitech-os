from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _coerce_context(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(value)


@dataclass(slots=True)
class SentinelError(Exception):
    code: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.context = _coerce_context(self.context)
        super().__init__(self.render())

    def render(self) -> str:
        parts = [f"[{self.code}]", self.message]
        if self.context:
            ordered = " | ".join(f"{k}={self.context[k]!r}" for k in sorted(self.context))
            parts.append(ordered)
        return " ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_type": type(self).__name__,
            "code": self.code,
            "message": self.message,
            "context": dict(self.context),
        }


class ConfigurationError(SentinelError):
    def __init__(self, message: str, **context: Any) -> None:
        super().__init__("CONFIGURATION_ERROR", message, context)


class WiringError(SentinelError):
    def __init__(self, message: str, **context: Any) -> None:
        super().__init__("WIRING_ERROR", message, context)


class ContractValidationError(SentinelError):
    def __init__(self, message: str, **context: Any) -> None:
        super().__init__("CONTRACT_VALIDATION_ERROR", message, context)


class PathSafetyError(SentinelError):
    def __init__(self, message: str, **context: Any) -> None:
        super().__init__("PATH_SAFETY_ERROR", message, context)


class ProviderRegistrationError(SentinelError):
    def __init__(self, message: str, **context: Any) -> None:
        super().__init__("PROVIDER_REGISTRATION_ERROR", message, context)


class PhaseValidationError(SentinelError):
    def __init__(self, message: str, **context: Any) -> None:
        super().__init__("PHASE_VALIDATION_ERROR", message, context)


def raise_if(condition: bool, error_type: type[SentinelError], message: str, **context: Any) -> None:
    if condition:
        raise error_type(message, **context)
