from dataclasses import dataclass, field


@dataclass(slots=True)
class ScopeSelection:
    targets: list[str] = field(default_factory=list)
    root_dir: str = ""

    @property
    def count(self) -> int:
        return len(self.targets)

    @property
    def is_empty(self) -> bool:
        return not self.targets

    def clear(self) -> None:
        self.targets.clear()
        self.root_dir = ""
