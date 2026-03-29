from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

class PluginCallable(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

@dataclass(slots=True)
class PluginContract:
    name: str
    kind: str
    enabled: bool = True
    health_check: PluginCallable | None = None
    repair_hook: PluginCallable | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["health_check"] = bool(self.health_check)
        payload["repair_hook"] = bool(self.repair_hook)
        return payload
