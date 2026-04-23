"""Compatibility shim for registry_index.json versus legacy query_index.json."""

from __future__ import annotations

from pathlib import Path

from contracts.shared_canon import LEGACY_INDEX_NAME, PORTABLE_CANONICAL_INDEX


class CanonicalIndexShim:
    def __init__(self, registry_dir: Path) -> None:
        self.registry_dir = registry_dir

    def resolve(self) -> tuple[Path, str]:
        canonical = self.registry_dir / PORTABLE_CANONICAL_INDEX
        legacy = self.registry_dir / LEGACY_INDEX_NAME
        if canonical.exists():
            return canonical, "canonical"
        if legacy.exists():
            return legacy, "legacy_shim"
        return canonical, "expected_missing"

    def load_name(self) -> str:
        path, _mode = self.resolve()
        return path.name
