from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def local_stamp() -> str:
    return dt.datetime.now().strftime("%d%m %H%M%S")


def run_token() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def package_directory(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())
    return destination


def git_snapshot(repo_root: Path) -> dict[str, Any]:
    import subprocess

    result: dict[str, Any] = {"repo_root": str(repo_root), "available": False}
    if not (repo_root / ".git").exists():
        return result
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=str(repo_root), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45,
        )
        result.update({
            "available": head.returncode == 0 and status.returncode == 0,
            "head": head.stdout.strip() if head.returncode == 0 else None,
            "status_porcelain": status.stdout,
            "head_stderr": head.stderr[-4000:],
            "status_stderr": status.stderr[-4000:],
        })
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}:{exc}"
    return result


def safe_remove_stage(stage: Path) -> None:
    shutil.rmtree(stage, ignore_errors=True)


def artifact_hash_file(root: Path) -> None:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "ARTIFACT_HASHES.sha256":
            rows.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    write_text(root / "ARTIFACT_HASHES.sha256", "\n".join(rows))
