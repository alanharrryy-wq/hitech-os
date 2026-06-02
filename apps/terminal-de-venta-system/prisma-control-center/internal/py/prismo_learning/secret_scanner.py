# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Secret-like pattern scanner.

The scanner never stores or returns the secret value. It reports labels and redacted
previews only. This is used for normal text files and for safe small entries inside ZIPs.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from .constants import MAX_TEXT_BYTES
from .sanitize import clean_text

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("openai_key_pattern", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}")),
    ("google_api_key_pattern", re.compile(r"AIza[A-Za-z0-9_\-]{25,}")),
    ("github_token_pattern", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("cloudflare_token_pattern", re.compile(r"(?i)cloudflare[^\n]{0,40}(token|api)[^\n]{0,20}[=:][^\n]{10,}")),
    ("generic_secret_assignment", re.compile(r"(?i)\b(token|secret|password|passwd|api[_-]?key)\b\s*[=:]\s*[^\s#]{8,}")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]


def redact(text: str) -> str:
    out = clean_text(text, max_chars=20000)
    for name, pattern in PATTERNS:
        out = pattern.sub(f"[{name}:REDACTED]", out)
    return out


def scan_text(text: str) -> dict[str, Any]:
    hits: list[str] = []
    for name, pattern in PATTERNS:
        if pattern.search(text or ""):
            hits.append(name)
    preview = redact(text)[:1600]
    return {
        "has_secret_like_pattern": bool(hits),
        "hits": sorted(set(hits)),
        "redacted_preview": preview,
    }


def scan_file(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        raw = p.read_bytes()[:MAX_TEXT_BYTES]
        text = raw.decode("utf-8", errors="replace")
    except Exception as exc:
        return {"has_secret_like_pattern": False, "hits": [], "redacted_preview": "", "error": str(exc)}
    result = scan_text(text)
    result["bytes_scanned"] = len(raw)
    return result
