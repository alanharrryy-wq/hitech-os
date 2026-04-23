from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import asdict
from pathlib import Path


def _default_root() -> Path:
    env_root = os.getenv("SYNAPSE_X_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


@dataclass(slots=True)
class Settings:
    root: Path = _default_root()
    db_path: Path | None = None
    cache_dir: Path | None = None
    raw_dir: Path | None = None
    export_dir: Path | None = None
    diagnostics_dir: Path | None = None
    log_dir: Path | None = None
    source_paths: tuple[Path, ...] = ()

    def __post_init__(self) -> None:
        if self.db_path is None:
            self.db_path = self.root / "data" / "sqlite" / "synapse_x.db"
        if self.cache_dir is None:
            self.cache_dir = self.root / "data" / "cache"
        if self.raw_dir is None:
            self.raw_dir = self.root / "data" / "raw"
        if self.export_dir is None:
            self.export_dir = self.root / "data" / "exports"
        if self.diagnostics_dir is None:
            self.diagnostics_dir = self.root / "data" / "diagnostics"
        if self.log_dir is None:
            self.log_dir = self.root / "logs"
        if not self.source_paths:
            self.source_paths = (self.root / "sample_inputs",)

    def ensure_dirs(self) -> None:
        for path in (
            self.root,
            self.db_path.parent,
            self.cache_dir,
            self.raw_dir,
            self.export_dir,
            self.diagnostics_dir,
            self.log_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


def get_settings(root: Path | None = None) -> dict:
    settings = Settings(root=root.resolve()) if root else Settings()
    settings.ensure_dirs()
    payload = asdict(settings)
    for key, value in payload.items():
        if isinstance(value, Path):
            payload[key] = str(value)
        if isinstance(value, tuple):
            payload[key] = [str(item) for item in value]
    return payload
