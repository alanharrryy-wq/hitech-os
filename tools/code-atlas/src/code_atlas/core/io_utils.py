from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

CHUNK_SIZE = 1024 * 1024
DEFAULT_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".next", ".turbo", "node_modules",
    ".venv", "venv", "env", "dist", "build", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "coverage", "_dependency_graphs"
}
SECRET_KEY_RE = re.compile(r"(?i)(secret|token|apikey|api_key|password|passwd|credential|private[_-]?key)")


def now_stamp() -> str:
    return datetime.now().strftime("%d%m %H%M")


def iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_text(path: str | Path, text: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))


def write_json(path: str | Path, data: Any) -> Path:
    return write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def human_bytes(value: int | float) -> str:
    n = float(value or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def safe_rel(path: str | Path, root: str | Path) -> str:
    p = Path(path)
    r = Path(root)
    try:
        return p.resolve().relative_to(r.resolve()).as_posix()
    except Exception:
        return p.as_posix()


def is_ignored_path(path: str | Path, ignore_dirs: set[str] | None = None) -> bool:
    ignore = {x.lower() for x in (ignore_dirs or DEFAULT_IGNORE_DIRS)}
    return any(part.lower() in ignore for part in Path(path).parts)


def iter_project_files(root: str | Path, *, include_hidden: bool = True, ignore_dirs: set[str] | None = None) -> Iterable[Path]:
    root = Path(root)
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = sorted(d for d in dirs if not is_ignored_path(current_path / d, ignore_dirs))
        for name in sorted(files):
            p = current_path / name
            if is_ignored_path(p, ignore_dirs):
                continue
            if not include_hidden and any(part.startswith('.') for part in p.relative_to(root).parts):
                continue
            yield p


def zip_folder(folder: str | Path, out_zip: str | Path, *, compression: int = zipfile.ZIP_DEFLATED) -> Path:
    folder = Path(folder)
    out_zip = Path(out_zip)
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=compression, allowZip64=True) as zf:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and p.resolve() != out_zip.resolve():
                zf.write(p, p.relative_to(folder).as_posix())
    return out_zip


def zip_entries(zip_path: str | Path) -> list[str]:
    with zipfile.ZipFile(zip_path, "r", allowZip64=True) as zf:
        return sorted(n for n in zf.namelist() if not n.endswith("/") and not n.startswith("__split_info__/"))


def redacted_env_line(line: str) -> str:
    if "=" not in line:
        return line.strip()
    key, value = line.split("=", 1)
    if SECRET_KEY_RE.search(key):
        return f"{key}=<redacted>"
    if len(value.strip()) > 80:
        return f"{key}=<redacted-long-value>"
    return line.strip()
