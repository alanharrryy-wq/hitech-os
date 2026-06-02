# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Local read-only safety firewall for file evidence.

Rule: when uncertain, classify as metadata-only. The engine may fingerprint and classify
metadata for unsafe files, but it must not read raw contents from DBs, env files, large
binaries, dependency folders or generated build output.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable
from .constants import FORBIDDEN_NAMES, FORBIDDEN_PATH_PARTS, METADATA_ONLY_EXTENSIONS, SAFE_TEXT_EXTENSIONS

class SafetyViolation(RuntimeError):
    pass

READ_OPERATION_NAMES = {"scan", "fingerprint", "inspect", "ingest", "classify", "query", "report"}
WRITE_OPERATION_NAMES = {"delete", "deploy", "push", "execute", "install_dependency", "mutate_db", "write_db"}


def norm_parts(path: str | os.PathLike[str]) -> list[str]:
    return [p.lower() for p in Path(path).parts if p not in {"", os.sep}]


def is_forbidden_path(path: str | os.PathLike[str]) -> bool:
    p = Path(path)
    parts = set(norm_parts(p))
    name = p.name.lower()
    if name in FORBIDDEN_NAMES:
        return True
    if parts.intersection(FORBIDDEN_PATH_PARTS):
        return True
    if name.endswith((".pem", ".key", ".pfx", ".p12")):
        return True
    return False


def is_metadata_only(path: str | os.PathLike[str]) -> bool:
    p = Path(path)
    suffix = p.suffix.lower()
    if is_forbidden_path(p):
        return True
    if suffix in METADATA_ONLY_EXTENSIONS:
        return True
    if suffix and suffix not in SAFE_TEXT_EXTENSIONS:
        return True
    try:
        if p.stat().st_size > 8 * 1024 * 1024:
            return True
    except Exception:
        return True
    return False


def safe_to_read_text(path: str | os.PathLike[str]) -> bool:
    p = Path(path)
    return p.exists() and p.is_file() and not is_metadata_only(p) and p.suffix.lower() in SAFE_TEXT_EXTENSIONS


def assert_read_only_operation(operation: str) -> None:
    op = (operation or "").strip().lower()
    if op in WRITE_OPERATION_NAMES:
        raise SafetyViolation(f"Operation blocked by PRISMO read-only firewall: {operation}")
    if op and op not in READ_OPERATION_NAMES:
        # Unknown operations are not executed. They are not automatically unsafe as labels,
        # but callers must not use this as permission for mutation.
        return


def safe_open_text(path: str | os.PathLike[str], max_bytes: int) -> str:
    p = Path(path)
    if not safe_to_read_text(p):
        raise SafetyViolation(f"File is not safe for text read: {p}")
    raw = p.read_bytes()[:max_bytes]
    if b"\x00" in raw[:4096]:
        raise SafetyViolation(f"Binary-like text blocked: {p}")
    return raw.decode("utf-8", errors="replace")


def filter_safe_roots(paths: Iterable[str | os.PathLike[str]]) -> list[Path]:
    roots: list[Path] = []
    for item in paths:
        try:
            p = Path(item).expanduser().resolve()
            if p.exists() and not is_forbidden_path(p):
                roots.append(p)
        except Exception:
            continue
    return roots
