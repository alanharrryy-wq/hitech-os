from __future__ import annotations

import json
import os
import pathlib
import shutil
import tempfile
from typing import Any

from .hashing import canonical_json


def ensure_dir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def atomic_write_text(path: pathlib.Path, text: str) -> None:
    ensure_dir(path.parent)
    payload = text if text.endswith("\n") else text + "\n"
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        pathlib.Path(tmp).replace(path)
    finally:
        tmp_path = pathlib.Path(tmp)
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def atomic_write_json(path: pathlib.Path, data: Any) -> None:
    atomic_write_text(path, canonical_json(data))


def read_text(path: pathlib.Path, default: str = "") -> str:
    if not path.is_file():
        return default
    return path.read_text(encoding="utf-8")


def copy_latest(latest_dir: pathlib.Path, files: list[pathlib.Path]) -> None:
    if latest_dir.exists():
        shutil.rmtree(latest_dir)
    latest_dir.mkdir(parents=True, exist_ok=True)
    for source in files:
        target = latest_dir / source.name
        shutil.copy2(source, target)


def write_latest_run_pointer(path: pathlib.Path, run_id: str) -> None:
    atomic_write_text(path, run_id + "\n")


def dump_json_lines(path: pathlib.Path, entries: list[dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    lines = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in entries]
    atomic_write_text(path, "\n".join(lines) + ("\n" if lines else ""))
