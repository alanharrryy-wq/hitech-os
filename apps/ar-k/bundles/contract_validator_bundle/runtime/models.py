
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    family: str
    message: str
    entity: str
    location: str
    expected: Any
    observed: Any
    remediation: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
