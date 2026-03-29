#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def ensure_trailing_newline(text: str) -> str:
    if text.endswith("\n"):
        return text
    return text + "\n"


def write_text(path: Path, content: str, trailing_newline: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_newlines(content)
    if trailing_newline:
        normalized = ensure_trailing_newline(normalized)
    path.write_text(normalized, encoding="utf-8", newline="\n")

