from __future__ import annotations

import fnmatch
import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stable_json_dumps(data), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_relpath(path: str | Path) -> str:
    value = str(path).replace("\\", "/")
    value = value.lstrip("./")
    return value


def match_any(path: str, patterns: Iterable[str]) -> bool:
    normalized = normalize_relpath(path)
    for pattern in patterns:
        normalized_pattern = normalize_relpath(pattern)
        if fnmatch.fnmatch(normalized, normalized_pattern):
            return True
    return False


def discover_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__).resolve()).resolve()
    for candidate in [current] + list(current.parents):
        config_path = candidate / "configs/execution_framework/system_config.json"
        if config_path.exists():
            return candidate
    raise FileNotFoundError("Could not discover repo root containing configs/execution_framework/system_config.json")


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append(path)
    return files


def deterministic_zip_dir(source_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in collect_files(source_dir):
            arcname = normalize_relpath(file_path.relative_to(source_dir))
            info = zipfile.ZipInfo(arcname)
            info.date_time = (2024, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, file_path.read_bytes())


def extract_zip_to_temp(zip_path: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="uef_"))
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(tmp)
    return tmp


def build_default_run_id(project_id: str, sequence: int = 1, when: datetime | None = None) -> str:
    stamp = (when or datetime.now(timezone.utc)).strftime("%Y%m%d")
    return f"run-{project_id}-{stamp}-{sequence:02d}"


@dataclass
class Issue:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"code": self.code, "message": self.message}
        if self.path:
            payload["path"] = self.path
        return payload


def copy_payload(payload_dir: Path, repo_root: Path, dry_run: bool = False) -> list[str]:
    copied: list[str] = []
    for file_path in collect_files(payload_dir):
        rel = normalize_relpath(file_path.relative_to(payload_dir))
        target = repo_root / rel
        copied.append(rel)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, target)
    return copied
