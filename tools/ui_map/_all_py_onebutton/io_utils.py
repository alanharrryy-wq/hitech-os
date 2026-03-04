from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT_MARKERS = ("package.json", "pnpm-workspace.yaml")
SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".turbo",
    "__pycache__",
    ".venv",
}


def detect_repo_root(start: Path | None = None, markers: Sequence[str] = ROOT_MARKERS) -> Path:
    probe = (start or Path.cwd()).resolve()
    current = probe if probe.is_dir() else probe.parent
    while True:
        if any((current / marker).exists() for marker in markers):
            return current
        if current.parent == current:
            marker_list = ", ".join(markers)
            raise FileNotFoundError(f"unable to detect repo root using markers: {marker_list}")
        current = current.parent


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_json(path: Path) -> Any:
    return json.loads(read_text(path))


def dump_json(data: Any, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=True, separators=(",", ": ")) + "\n"


def write_json(path: Path, data: Any, indent: int = 2) -> None:
    write_text(path, dump_json(data, indent=indent))


def list_files(base: Path, extensions: Iterable[str]) -> list[Path]:
    wanted = {item.lower() for item in extensions}
    files: list[Path] = []
    for path in base.rglob("*"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in wanted:
            files.append(path)
    files.sort(key=lambda item: item.as_posix().lower())
    return files
