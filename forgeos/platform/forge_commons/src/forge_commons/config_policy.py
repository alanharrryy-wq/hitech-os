from __future__ import annotations

from copy import deepcopy
from typing import Any

from .lifecycle import CapabilityLifecycle, CapabilityRuntimeState


class ConfigPolicyCapability:
    """Shared config/policy capability with deterministic override precedence."""

    capability_id = "forge.commons.config_policy"

    def __init__(self) -> None:
        self.lifecycle = CapabilityLifecycle(self.capability_id)
        self._profiles: dict[str, dict[str, Any]] = {}
        self._overrides: dict[str, Any] = {}

    def activate(self) -> CapabilityRuntimeState:
        return self.lifecycle.activate()

    def dispose(self) -> CapabilityRuntimeState:
        self._profiles.clear()
        self._overrides.clear()
        return self.lifecycle.dispose()

    def set_profile(self, profile_name: str, values: dict[str, Any]) -> None:
        self._profiles[profile_name] = deepcopy(values)

    def apply_override(self, key: str, value: Any) -> None:
        self._overrides[key] = value

    def resolve(self, profile_name: str | None = None) -> dict[str, Any]:
        base: dict[str, Any] = {}
        if profile_name:
            base = deepcopy(self._profiles.get(profile_name, {}))
        merged = {**base, **self._overrides}
        return merged
