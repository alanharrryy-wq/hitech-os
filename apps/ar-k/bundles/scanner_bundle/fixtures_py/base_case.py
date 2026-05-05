from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ScannerFixtureCase:
    name: str
    description: str
    tags: tuple[str, ...]
    source_files: dict[str, str]
    expected_summary: dict[str, int | bool | str]

    def write_tree(self, root: Path) -> Path:
        for rel, content in self.source_files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        return root
