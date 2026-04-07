from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


_DEFAULT_SETTINGS_PATH = Path.home() / ".deltaforge" / "settings.json"


def _normalize_path(path: str | Path | None) -> Path:
    return Path(path) if path is not None else _DEFAULT_SETTINGS_PATH


def _read_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}

    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Settings file must contain a JSON object: {path}")

    return dict(data)


def _write_atomic(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    serialized = json.dumps(
        dict(data),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    fd, temp_path = tempfile.mkstemp(
        prefix=f"{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def load_settings(path: str | Path | None = None) -> dict[str, Any]:
    return _read_dict(_normalize_path(path))


def save_settings(
    values: Mapping[str, Any],
    path: str | Path | None = None,
) -> dict[str, Any]:
    target = _normalize_path(path)
    data = dict(values)
    _write_atomic(target, data)
    return data


class SettingsStore:
    """Canonical infrastructure settings store with compatibility aliases."""

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = _normalize_path(path)

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> dict[str, Any]:
        return load_settings(self._path)

    def save(self, values: Mapping[str, Any]) -> dict[str, Any]:
        return save_settings(values, self._path)

    def read_all(self) -> dict[str, Any]:
        return self.load()

    def write_all(self, values: Mapping[str, Any]) -> dict[str, Any]:
        return self.save(values)

    def get(self, key: str, default: Any = None) -> Any:
        return self.load().get(key, default)

    def set(self, key: str, value: Any) -> Any:
        data = self.load()
        data[key] = value
        self.save(data)
        return value

    def update(self, values: Mapping[str, Any]) -> dict[str, Any]:
        data = self.load()
        data.update(dict(values))
        return self.save(data)

    def delete(self, key: str) -> bool:
        data = self.load()
        if key not in data:
            return False

        del data[key]
        self.save(data)
        return True

    def clear(self) -> dict[str, Any]:
        return self.save({})

    def read(self, key: str, default: Any = None) -> Any:
        return self.get(key, default)

    def write(self, key: str, value: Any) -> Any:
        return self.set(key, value)

    def close(self) -> None:
        return None
