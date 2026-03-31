from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class OpsDocument:
    text: str = ""
    source_path: str = ""
    loaded_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def is_loaded(self) -> bool:
        return bool(self.text.strip())
