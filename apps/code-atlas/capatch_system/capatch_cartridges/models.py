from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CartridgePolicy:
    allowed_paths: tuple[str, ...] = ()
    excluded_paths: tuple[str, ...] = ()
    required_verifiers: tuple[str, ...] = ()
    evidence_required: tuple[str, ...] = ()
    risk_gates: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Cartridge:
    cartridge_id: str
    title: str
    version: str = '1.0.0'
    inherits: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    policy: CartridgePolicy = field(default_factory=CartridgePolicy)
    raw: dict[str, Any] = field(default_factory=dict)

    def allows_path(self, relative_path: str) -> bool:
        value = relative_path.replace('\\', '/')
        if any(value.startswith(prefix.rstrip('/') + '/') or value == prefix.rstrip('/') for prefix in self.policy.excluded_paths):
            return False
        if not self.policy.allowed_paths:
            return True
        return any(value.startswith(prefix.rstrip('/') + '/') or value == prefix.rstrip('/') for prefix in self.policy.allowed_paths)
