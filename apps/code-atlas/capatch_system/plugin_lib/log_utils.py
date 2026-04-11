#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""Helpers de logs con limites de tamano para bundles IA-first."""

import re
from collections import Counter
from pathlib import Path
from typing import Any

from .fs_utils import read_text_safe, safe_file_size

COMMON_LOG_DIR_NAMES = {"logs", "log", "reports", "tmp", "runtime", ".next", "dist", ".turbo", ".cache"}
COMMON_LOG_SUFFIXES = {".log", ".out", ".err", ".txt"}
INTERESTING_PATTERNS = [
    re.compile(r"(?i)\b(error|exception|traceback|fatal|panic|failed|refused|denied|missing|timeout)\b"),
    re.compile(r"(?i)\b(module not found|cannot find module|syntaxerror|typeerror|valueerror|runtimeerror)\b"),
    re.compile(r"(?i)\b(eaddrinuse|address already in use|bind failed|port .* in use)\b"),
]


def tail_text(text: str, *, max_lines: int = 200, max_bytes: int = 262_144) -> str:
    if len(text.encode("utf-8", errors="ignore")) > max_bytes:
        encoded = text.encode("utf-8", errors="ignore")
        text = encoded[-max_bytes:].decode("utf-8", errors="ignore")
    lines = text.splitlines()
    trimmed = lines[-max_lines:]
    return "\n".join(trimmed).strip() + ("\n" if trimmed else "")


def tail_file_text(path_value: Path, *, max_lines: int = 200, max_bytes: int = 262_144) -> str:
    return tail_text(read_text_safe(path_value), max_lines=max_lines, max_bytes=max_bytes)


def summarize_candidate_logs(root_dir: Path, limit: int = 24) -> list[dict[str, Any]]:
    root_dir = Path(root_dir)
    if not root_dir.exists() or not root_dir.is_dir():
        return []
    found: list[dict[str, Any]] = []
    for path_value in root_dir.rglob("*"):
        if len(found) >= limit:
            break
        if not path_value.is_file():
            continue
        parent_names = {part.lower() for part in path_value.parts}
        if not parent_names.intersection(COMMON_LOG_DIR_NAMES) and path_value.suffix.lower() not in COMMON_LOG_SUFFIXES:
            continue
        found.append(
            {
                "path": str(path_value.resolve()),
                "size": safe_file_size(path_value),
            }
        )
    return found


def is_interesting_log_line(line: str) -> bool:
    text = str(line or "").strip()
    if not text:
        return False
    return any(pattern.search(text) for pattern in INTERESTING_PATTERNS)


def extract_interesting_lines(text: str, *, limit: int = 80) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line or line in seen:
            continue
        if is_interesting_log_line(line):
            seen.add(line)
            lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def normalize_signature(line: str) -> str:
    value = str(line or "").strip()
    value = re.sub(r"\b0x[0-9a-fA-F]+\b", "0xADDR", value)
    value = re.sub(r"\b\d+\b", "N", value)
    value = re.sub(r"\s+", " ", value)
    return value[:220]


def group_interesting_lines(lines: list[str], *, limit: int = 20) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    exemplar: dict[str, str] = {}
    for line in lines:
        signature = normalize_signature(line)
        counter[signature] += 1
        exemplar.setdefault(signature, line[:500])
    items: list[dict[str, Any]] = []
    for signature, count in counter.most_common(limit):
        items.append(
            {
                "signature": signature,
                "count": count,
                "example": exemplar.get(signature, signature),
            }
        )
    return items
