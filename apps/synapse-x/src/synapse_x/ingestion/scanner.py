from __future__ import annotations

from pathlib import Path

from synapse_x.parsers import SUPPORTED_EXTENSIONS


def scan_sources(paths: list[str | Path]) -> list[Path]:
    discovered: set[Path] = set()
    for raw in paths:
        path = Path(raw).expanduser().resolve()
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                discovered.add(path)
            continue
        if path.is_dir():
            for candidate in path.rglob("*"):
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                    discovered.add(candidate.resolve())
    return sorted(discovered)
