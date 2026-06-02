# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""General sanitizers used before evidence enters registry or UI payloads."""
from __future__ import annotations
import re
from typing import Any

WINDOWS_ABS_RE = re.compile(r"[A-Za-z]:[\\/][^\s\"'<>|]+")
HOME_RE = re.compile(r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+)")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(value: Any, max_chars: int = 12000) -> str:
    text = "" if value is None else str(value)
    text = CONTROL_CHARS_RE.sub(" ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) > max_chars:
        text = text[: max_chars - 40] + "\n...[PRISMO_PREVIEW_TRUNCATED]"
    return text


def safe_source_label(path: str) -> str:
    label = WINDOWS_ABS_RE.sub("PRISMA_LOCAL_PATH_REDACTED", str(path))
    label = HOME_RE.sub("<HOME_PATH>", label)
    return label.replace("\\", "/")


def redact_paths(text: str) -> str:
    return WINDOWS_ABS_RE.sub("PRISMA_LOCAL_PATH_REDACTED", text)


def shallow_public_copy(obj: Any) -> Any:
    if isinstance(obj, dict):
        blocked = {"source_path", "absolute_path", "raw_preview", "raw_text", "secret_preview"}
        return {k: shallow_public_copy(v) for k, v in obj.items() if k not in blocked}
    if isinstance(obj, list):
        return [shallow_public_copy(v) for v in obj]
    if isinstance(obj, str):
        return redact_paths(obj)
    return obj
