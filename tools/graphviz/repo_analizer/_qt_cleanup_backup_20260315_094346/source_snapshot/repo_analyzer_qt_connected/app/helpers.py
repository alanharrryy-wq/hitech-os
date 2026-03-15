#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import time
from pathlib import Path


def human_size(num: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    n = float(num)
    for unit in units:
        if n < 1024 or unit == units[-1]:
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{num} B"


def now_str() -> str:
    return time.strftime("%H:%M:%S")


def read_text_safe(path: Path) -> str:
    encodings = ("utf-8", "utf-8-sig", "latin-1", "cp1252")
    last_error = None
    for enc in encodings:
        try:
            return path.read_text(encoding=enc, errors="strict")
        except Exception as e:
            last_error = e
    raise last_error if last_error else RuntimeError(f"No se pudo leer {path}")


def extract_imports(text: str) -> list[str]:
    patterns = [
        r'^\s*import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
        r'^\s*import\s+[\'"](.+?)[\'"]',
        r'require\(\s*[\'"](.+?)[\'"]\s*\)',
        r'import\(\s*[\'"](.+?)[\'"]\s*\)',
    ]
    found: list[str] = []
    for pat in patterns:
        found.extend(re.findall(pat, text, flags=re.MULTILINE))
    deduped = []
    seen = set()
    for x in found:
        if x not in seen:
            seen.add(x)
            deduped.append(x)
    return deduped


def resolve_import(root: Path, source_file: Path, raw_import: str) -> str | None:
    candidates: list[Path] = []

    if raw_import.startswith("."):
        base = (source_file.parent / raw_import).resolve()
        candidates.append(base)
    elif raw_import.startswith("/"):
        base = (root / raw_import.lstrip("/")).resolve()
        candidates.append(base)
    else:
        base = (root / raw_import).resolve()
        candidates.append(base)

    resolved_candidates: list[Path] = []
    exts = [".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".py"]

    for base in candidates:
        resolved_candidates.append(base)
        if not base.suffix:
            for ext in exts:
                resolved_candidates.append(Path(str(base) + ext))
            for ext in exts:
                resolved_candidates.append(base / f"index{ext}")

    for cand in resolved_candidates:
        try:
            if cand.exists() and cand.is_file():
                return cand.relative_to(root).as_posix()
        except Exception:
            continue

    return None
