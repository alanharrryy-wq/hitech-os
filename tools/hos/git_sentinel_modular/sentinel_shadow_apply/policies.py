from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(slots=True)
class ApplyPolicy:
    allow_delete: bool = False
    rejected_prefixes: tuple[str, ...] = (".git/", "__pycache__/")
    max_files: int = 250
    metadata: dict[str, str] = field(default_factory=dict)

def default_policy() -> ApplyPolicy:
    return ApplyPolicy()
